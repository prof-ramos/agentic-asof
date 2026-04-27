from __future__ import annotations

import os
import argparse
from pathlib import Path

from supabase import create_client
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_core.documents import Document


SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://aerkqudrangsqrdsfsys.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
DOCS_DIR = Path(__file__).parent / "legislacoes"


def _ensure_types(obj: object) -> None:
    # Helper to quiet type-checkers in limited runtime environments
    return None


def apply_migration(supabase) -> None:
    migration_paths = [
        Path(__file__).parent / "supabase" / "migrations" / "20250427020000_create_documents.sql",
        Path(__file__).parent / "supabase" / "migrations" / "20250427030000_add_fts.sql",
    ]
    for migration_path in migration_paths:
        if not migration_path.exists():
            print(f"Migration file not found: {migration_path}")
            continue
        sql = migration_path.read_text()
        for statement in sql.split(";"):
            statement = statement.strip()
            if statement:
                try:
                    supabase.rpc("exec_sql", {"sql": statement}).execute()
                except Exception as e:
                    print(f"Migration step failed: {e}")
    
    print("Database migrations applied (if present)")


def chunk_document(file_path: Path) -> list[Document]:
    content = file_path.read_text(encoding="utf-8")
    
    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "titulo"), ("##", "secao"), ("###", "artigo")],
        strip_headers=False
    )
    
    docs = splitter.split_text(content)
    filename = file_path.stem
    parts = filename.replace("lei-", "").replace("decreto-", "").split("-")
    
    for doc in docs:
        doc.metadata.update({
            "source": str(file_path),
            "filename": filename,
            "tipo": "lei" if "lei" in filename else "decreto",
            "numero": parts[0],
            "ano": parts[1],
        })
    
    return docs


def index_documents(supabase, embeddings, limit: int = None) -> int:
    excluded = {"README.md", "marcacoes-planalto.md"}
    md_files = sorted([f for f in DOCS_DIR.glob("*.md") if f.name not in excluded])
    
    if limit:
        md_files = md_files[:limit]
    
    total_chunks = 0
    
    for file_path in md_files:
        print(f"Indexing: {file_path.name}")
        
        chunks = chunk_document(file_path)
        
        for chunk in chunks:
            embedding = embeddings.embed_query(chunk.page_content)
            
            supabase.table("documents").insert({
                "content": chunk.page_content,
                "metadata": chunk.metadata,
                "embedding": embedding,
            }).execute()
            
            total_chunks += 1
        
        print(f"  ✓ {len(chunks)} chunks")
    
    return total_chunks


def query_similar(supabase, embeddings, query: str, k: int = 5):
    query_embedding = embeddings.embed_query(query)
    
    result = supabase.rpc(
        "match_documents",
        {
            "query_embedding": query_embedding,
            "match_threshold": 0.5,
            "match_count": k,
        }
    ).execute()
    
    return result.data


def hybrid_query(supabase, embeddings, query_text: str, k: int = 20, threshold: float = 0.5, rrf_k: int = 60):
    """Hybrid search across vector and full-text using Reciprocal Rank Fusion.

    This uses the new Postgres function `hybrid_search` exposed via RPC. It
    embeds the query, then delegates to the DB which performs a vector search,
    an FT search, and combines results with RRF. Returns documents with an
    additional `source` column indicating the origin of the result.

    Args:
        supabase: Supabase client
        embeddings: Embeddings object with `embed_query`.
        query_text: Text query to search across FT and vector spaces
        k: Limit per-source candidates
        threshold: Vector similarity threshold to consider
        rrf_k: RRF parameter (k in the denominator)

    Returns:
        List of documents with fields: id, content, metadata, similarity, source
    """
    query_embedding = embeddings.embed_query(query_text)
    result = supabase.rpc(
        "hybrid_search",
        {
            "query_embedding": query_embedding,
            "query_text": query_text,
            "match_threshold": threshold,
            "match_count": k,
            "rrf_k": rrf_k,
        }
    ).execute()
    return result.data


def query_fts_only(supabase, embeddings, query_text: str, k: int = 20):
    """Return only FT-search results from the hybrid_search RPC.

    This is a convenience wrapper to enable an FT-only path if the caller
    requests it. It relies on the `hybrid_search` function and then filters
    results to those originating from FT (source == 'fts' or 'both').
    """
    results = hybrid_query(supabase, embeddings, query_text, k=k, threshold=0.0, rrf_k=60)
    if not results:
        return []
    return [r for r in results if r.get("source") in ("fts", "both")]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["migrate", "index", "query"])
    parser.add_argument("--method", choices=["vector", "hybrid", "fts"], default="vector",
                        help="Search method: vector, hybrid, or fts (full-text search)")
    parser.add_argument("--limit", type=int, help="Limit number of documents to index")
    parser.add_argument("--query", type=str, help="Query text for similarity search")
    args = parser.parse_args()
    
    if not SUPABASE_KEY:
        print("Error: Set SUPABASE_SERVICE_ROLE_KEY environment variable")
        return 1
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    if args.command == "migrate":
        apply_migration(supabase)
    
    elif args.command == "index":
        count = index_documents(supabase, embeddings, args.limit)
        print(f"\n✓ Indexed {count} total chunks")
    
    elif args.command == "query":
        if not args.query:
            print("Error: --query required")
            return 1
        
        if args.method == "vector":
            results = query_similar(supabase, embeddings, args.query)
        elif args.method == "hybrid":
            results = hybrid_query(supabase, embeddings, args.query, k=20, threshold=0.5, rrf_k=60)
        else:  # fts
            results = query_fts_only(supabase, embeddings, args.query, k=20)
        for i, doc in enumerate(results, 1):
            print(f"\n{i}. [{doc['metadata']['tipo'].upper()} {doc['metadata']['numero']}/{doc['metadata']['ano']}]")
            print(f"   Similarity: {doc['similarity']:.3f}")
            print(f"   Content: {doc['content'][:200]}...")
    
    return 0


if __name__ == "__main__":
    exit(main())

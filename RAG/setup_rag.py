from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from supabase import create_client
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_core.documents import Document


SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://aerkqudrangsqrdsfsys.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
DOCS_DIR = Path(__file__).parent / "legislacoes"


def setup_database(supabase: Any) -> None:
    extensions_sql = "CREATE EXTENSION IF NOT EXISTS vector;"
    supabase.rpc("exec_sql", {"sql": extensions_sql}).execute()
    print("pgvector enabled")
    
    table_sql = """
    CREATE TABLE IF NOT EXISTS documents (
        id SERIAL PRIMARY KEY,
        content TEXT NOT NULL,
        metadata JSONB DEFAULT '{}',
        embedding VECTOR(1536),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """
    supabase.rpc("exec_sql", {"sql": table_sql}).execute()
    print("documents table created")
    
    index_sql = "CREATE INDEX IF NOT EXISTS documents_embedding_idx ON documents USING hnsw (embedding vector_cosine_ops);"
    supabase.rpc("exec_sql", {"sql": index_sql}).execute()
    print("hnsw index created")


def parse_filename_metadata(filename: str) -> dict:
    parts = filename.replace("lei-", "").replace("decreto-", "").split("-")
    return {
        "filename": filename,
        "type": "lei" if "lei" in filename else "decreto",
        "numero": parts[0],
        "ano": parts[1],
    }


def chunk_legal_document(file_path: Path) -> list[Document]:
    content = file_path.read_text(encoding="utf-8")
    
    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "titulo"), ("##", "secao"), ("###", "artigo")],
        strip_headers=False
    )
    
    docs = splitter.split_text(content)
    metadata = parse_filename_metadata(file_path.stem)
    
    for doc in docs:
        doc.metadata.update(metadata)
        doc.metadata["source"] = str(file_path)
    
    return docs


def index_documents(supabase: Any, embeddings: OpenAIEmbeddings) -> None:
    excluded = {"README.md", "marcacoes-planalto.md"}
    md_files = [f for f in DOCS_DIR.glob("*.md") if f.name not in excluded]
    
    print(f"\nIndexing {len(md_files)} documents\n")
    
    for file_path in md_files:
        print(f"Processing: {file_path.name}")
        
        chunks = chunk_legal_document(file_path)
        print(f"  {len(chunks)} chunks")
        
        for chunk in chunks:
            embedding = embeddings.embed_query(chunk.page_content)
            
            data = {
                "content": chunk.page_content,
                "metadata": chunk.metadata,
                "embedding": embedding,
            }
            
            supabase.table("documents").insert(data).execute()
        
        print(f"  ✓ {file_path.name}\n")


def main() -> None:
    if not SUPABASE_KEY:
        print("Error: SUPABASE_SERVICE_ROLE_KEY not set")
        print("Get from: Supabase Dashboard → Project Settings → API → service_role key")
        return 1
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    print("\n=== Database Setup ===")
    setup_database(supabase)
    
    print("\n=== Document Indexing ===")
    index_documents(supabase, embeddings)
    
    print("\n✓ RAG setup complete")
    return 0


if __name__ == "__main__":
    exit(main())

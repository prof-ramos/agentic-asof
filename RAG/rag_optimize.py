from __future__ import annotations

import os
import argparse
from pathlib import Path
from typing import Any

from supabase import create_client
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from legal_splitter import split_legal_document
from langchain_core.documents import Document


SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://aerkqudrangsqrdsfsys.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
DOCS_DIR = Path(__file__).parent / "legislacoes"


def chunk_with_token_splitter(file_path: Path) -> list[Document]:
    # Use the legal-aware BR splitter instead of token-based chunking
    content = file_path.read_text(encoding="utf-8")
    filename = file_path.stem
    # split_legal_document returns List[Document] with rich metadata
    try:
        docs = split_legal_document(content, filename)
    except Exception:
        # Fallback to original token-based approach if BR splitter fails
        splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            encoding_name="cl100k_base",
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " ", ""]
        )
        docs = splitter.create_documents([content])
        for i, doc in enumerate(docs):
            doc.metadata.update({
                "source": str(file_path),
                "filename": filename,
                "tipo": "lei" if "lei" in filename else "decreto",
                "numero": filename.replace("lei-", "").replace("decreto-", "").split("-")[0],
                "ano": filename.split("-")[1],
                "chunk_index": i,
            })
    return docs


def index_optimized(supabase: Any, embeddings: Any, limit: int = None) -> int:
    excluded = {"README.md", "marcacoes-planalto.md"}
    md_files = sorted([f for f in DOCS_DIR.glob("*.md") if f.name not in excluded])
    
    if limit:
        md_files = md_files[:limit]
    
    total_chunks = 0
    total_chars = 0
    
    for file_path in md_files:
        print(f"Processing: {file_path.name}")
        
        chunks = chunk_with_token_splitter(file_path)
        chunk_sizes = [len(c.page_content) for c in chunks]
        
        for chunk in chunks:
            embedding = embeddings.embed_query(chunk.page_content)
            
            supabase.table("documents").upsert({
                "content": chunk.page_content,
                "metadata": chunk.metadata,
                "embedding": embedding,
            }).execute()
            
            total_chunks += 1
            total_chars += len(chunk.page_content)
        
        avg_size = sum(chunk_sizes) // len(chunks) if chunks else 0
        print(f"  {len(chunks)} chunks (avg {avg_size} chars)")
    
    print(f"\nTotal: {total_chunks} chunks, {total_chars} chars")
    return total_chunks


def clear_documents(supabase: Any) -> None:
    result = supabase.table("documents").delete().neq("id", 0).execute()
    print(f"Cleared documents table")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["reindex", "clear"])
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    
    if not SUPABASE_KEY:
        print("Error: SUPABASE_SERVICE_ROLE_KEY not set")
        return 1
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    if args.command == "clear":
        clear_documents(supabase)
    elif args.command == "reindex":
        print("Clearing existing documents...")
        clear_documents(supabase)
        print("\nReindexing with optimized chunking...")
        count = index_optimized(supabase, embeddings, args.limit)
        print(f"\nReindexed {count} chunks")
    
    return 0


if __name__ == "__main__":
    exit(main())

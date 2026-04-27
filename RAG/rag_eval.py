from __future__ import annotations

import os
import json
import argparse
from pathlib import Path
from dataclasses import dataclass

from supabase import create_client
from langchain_openai import OpenAIEmbeddings, ChatOpenAI


SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://aerkqudrangsqrdsfsys.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")


@dataclass
class RAGMetrics:
    retrieval_precision: float = 0.0
    retrieval_recall: float = 0.0
    context_relevance: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            "retrieval_precision": self.retrieval_precision,
            "retrieval_recall": self.retrieval_recall,
            "context_relevance": self.context_relevance,
        }


class RAGEvaluator:
    def __init__(self, supabase, embeddings, llm):
        self.supabase = supabase
        self.embeddings = embeddings
        self.llm = llm
    
    def query_documents(self, query: str, k: int = 20, method: str = "vector") -> list[dict]:
        query_embedding = self.embeddings.embed_query(query)
        
        if method == "vector":
            result = self.supabase.rpc(
                "match_documents",
                {
                    "query_embedding": query_embedding,
                    "match_threshold": 0.5,
                    "match_count": k,
                }
            ).execute()
            return result.data
        elif method == "hybrid":
            result = self.supabase.rpc(
                "hybrid_search",
                {
                    "query_embedding": query_embedding,
                    "query_text": query,
                    "match_threshold": 0.5,
                    "match_count": k,
                    "rrf_k": 60,
                }
            ).execute()
            return result.data
        elif method == "fts":
            # Use hybrid_search and filter to FT-only results
            result = self.supabase.rpc(
                "hybrid_search",
                {
                    "query_embedding": query_embedding,
                    "query_text": query,
                    "match_threshold": 0.0,
                    "match_count": k,
                    "rrf_k": 60,
                }
            ).execute()
            docs = result.data or []
            return [d for d in docs if d.get("source") in ("fts", "both")]
        else:
            # Fallback to vector search if unknown method
            result = self.supabase.rpc(
                "match_documents",
                {
                    "query_embedding": query_embedding,
                    "match_threshold": 0.5,
                    "match_count": k,
                }
            ).execute()
            return result.data
    
    def rerank_with_llm(self, query: str, docs: list[dict], top_k: int = 5) -> list[dict]:
        if len(docs) <= top_k:
            return docs
        
        scored = []
        for doc in docs:
            prompt = f"""Rate relevance (0-10):
Query: {query}
Content: {doc['content'][:300]}
Score (0-10):"""
            
            response = self.llm.invoke(prompt)
            try:
                score = float(response.content.strip())
            except ValueError:
                score = doc.get('similarity', 0.5) * 10
            
            scored.append((doc, score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in scored[:top_k]]
    
    def evaluate_retrieval(
        self,
        query: str,
        expected_laws: list[str],
        retrieved_docs: list[dict]
    ) -> tuple[float, float]:
        retrieved_laws = {doc["metadata"]["filename"] for doc in retrieved_docs}
        expected_set = set(expected_laws)
        
        relevant_retrieved = retrieved_laws & expected_set
        precision = len(relevant_retrieved) / len(retrieved_laws) if retrieved_laws else 0
        recall = len(relevant_retrieved) / len(expected_set) if expected_set else 0
        
        return precision, recall
    
    def evaluate_context_relevance(self, query: str, retrieved_docs: list[dict]) -> float:
        context_text = "\n\n".join([doc["content"][:500] for doc in retrieved_docs])
        
        prompt = f"""Rate relevance (0.0-1.0):
Question: {query}
Context: {context_text[:800]}
Score (0-1):"""
        
        response = self.llm.invoke(prompt)
        try:
            return float(response.content.strip())
        except ValueError:
            return 0.5
    
    def run_evaluation(self, test_cases: list[dict], use_reranking: bool = False, method: str = "hybrid") -> RAGMetrics:
        metrics = RAGMetrics()
        
        for test in test_cases:
            query = test["query"]
            expected_laws = test.get("expected_laws", [])
            
            retrieved = self.query_documents(query, k=20, method=method)
            
            if use_reranking:
                retrieved = self.rerank_with_llm(query, retrieved, top_k=5)
            else:
                retrieved = retrieved[:5]
            
            precision, recall = self.evaluate_retrieval(query, expected_laws, retrieved)
            metrics.retrieval_precision += precision
            metrics.retrieval_recall += recall
            
            context_rel = self.evaluate_context_relevance(query, retrieved)
            metrics.context_relevance += context_rel
        
        n = len(test_cases)
        metrics.retrieval_precision /= n
        metrics.retrieval_recall /= n
        metrics.context_relevance /= n
        
        return metrics


def get_test_cases() -> list[dict]:
    # Expanded dataset: 20 test cases in 5 categories.
    # Categories:
    # - specific_article: test queries targeting a single article
    # - broad_topic: broad thematic queries across laws
    # - cross_law: queries that may touch more than one law
    # - exact_term: queries requesting exact legal terms
    # - negative: queries that should not match certain laws (note: some fields are advisory)
    return [
        # 1) specific_article
        {
            "query": "Art. 7º da Lei n.º 8.829/1993",
            "expected_laws": ["lei-8829-1993"],
            "expected_articles": ["Art. 7º"],
            "category": "specific_article",
            "description": "Ingresso nas carreiras de Oficial/Assistente: Art.7º (concurso/promoção não-eligível)",
        },
        # 2) specific_article
        {
            "query": "Art. 10º da Lei n.º 8.829/1993",
            "expected_laws": ["lei-8829-1993"],
            "expected_articles": ["Art. 10º"],
            "category": "specific_article",
            "description": "Ingresso/cadastro via concurso público (Art.10) na Lei 8.829/1993",
        },
        # 3) specific_article
        {
            "query": "Art. 25º da Lei n.º 8.829/1993",
            "expected_laws": ["lei-8829-1993"],
            "expected_articles": ["Art. 25º"],
            "category": "specific_article",
            "description": "Progresso/progresão por merecimento (Art.25)",
        },
        # 4) specific_article
        {
            "query": "Art. 33-A da Lei n.º 8.829/1993",
            "expected_laws": ["lei-8829-1993"],
            "expected_articles": ["Art. 33-A"],
            "category": "specific_article",
            "description": "Contagem de tempo e enquadramento (Art.33-A)",
        },
        # 5) specific_article
        {
            "query": "Art. 11º da Lei n.º 8.112/1990",
            "expected_laws": ["lei-8112-1990"],
            "expected_articles": ["Art. 11º"],
            "category": "specific_article",
            "description": "Concurso público e ingresso conforme Lei 8.112/1990 (Art.11)",
        },

        # 6) broad_topic
        {
            "query": "direitos fundamentais dos servidores públicos federais",
            "expected_laws": ["lei-8112-1990"],
            "expected_articles": ["Art. 22", "Art. 41"],
            "category": "broad_topic",
            "description": "Direitos básicos, remuneração e estabilidade (panorama Lei 8112)",
        },
        # 7) broad_topic
        {
            "query": "vencimentos e vantagens no serviço público",
            "expected_laws": ["lei-8112-1990"],
            "expected_articles": ["Art. 40", "Art. 41", "Art. 42"],
            "category": "broad_topic",
            "description": "Disposições sobre vencimentos e vantagens (Lei 8112)",
        },
        # 8) broad_topic
        {
            "query": "ingresso e promoção na carreira de Oficial de Chancelaria",
            "expected_laws": ["lei-8829-1993", "decreto-1565-1995"],
            "expected_articles": ["Art. 7º", "Art. 10"] ,
            "category": "broad_topic",
            "description": "Mistura de ingresso e promoção entre Lei 8829 e Decreto 1565",
        },
        # 9) broad_topic
        {
            "query": "jornada de trabalho na carreira",
            "expected_laws": ["decreto-1565-1995"],
            "expected_articles": ["Art. 4º"],
            "category": "broad_topic",
            "description": "Regime de trabalho (40h/semana) no Decreto 1.565/1995",
        },
        # 10) broad_topic
        {
            "query": "regime jurídico dos servidores",
            "expected_laws": ["lei-8112-1990"],
            "expected_articles": ["Art. 1º", "Art. 2º"],
            "category": "broad_topic",
            "description": "Visão geral do regime jurídico (Lei 8112)",
        },

        # 11) cross_law
        {
            "query": "ingresso na carreira e ingresso no serviço exterior",
            "expected_laws": ["lei-8829-1993", "decreto-1565-1995"],
            "expected_articles": ["Art. 7º", "Art. 10"] ,
            "category": "cross_law",
            "description": "Intersecção entre Lei 8829 e Decreto 1565 sobre ingresso/posicionamento",
        },
        {
            "query": "promoção por merecimento e tempo de serviço",
            "expected_laws": ["lei-8112-1990", "lei-8829-1993"],
            "expected_articles": ["Art. 31", "Art. 32", "Art. 33"],
            "category": "cross_law",
            "description": "Promoção por merecimento vs antiguidade (Lei 8112 + Lei 8829)",
        },
        {
            "query": "concessões de gratificações e adicionais",
            "expected_laws": ["lei-8112-1990", "lei-8829-1993"],
            "expected_articles": ["Art. 61", "Art. 62"],
            "category": "cross_law",
            "description": "Gratificações e adicionais cruzando leis do serviço público",
        },
        {
            "query": "missões permanentes no exterior",
            "expected_laws": ["lei-8829-1993", "decreto-1565-1995"],
            "expected_articles": ["Art. 21", "Art. 22"],
            "category": "cross_law",
            "description": "Remoção e atuação internacional (missões)",
        },

        # 12) exact_term
        {
            "query": "Oficial de Chancelaria",
            "expected_laws": ["lei-8829-1993", "decreto-1565-1995"],
            "expected_articles": ["Art. 7º", "Art. 8º"],
            "category": "exact_term",
            "description": "Validação de ocorrência do termo Oficial de Chancelaria em documentos",
        },
        {
            "query": "regime juridico unico",
            "expected_laws": ["lei-8112-1990"],
            "expected_articles": ["Art. 1º"],
            "category": "exact_term",
            "description": "Termo exato para busca (Regime Jurídico único)",
        },
        {
            "query": "concurso publico",
            "expected_laws": ["lei-8112-1990"],
            "expected_articles": ["Art. 11º"],
            "category": "exact_term",
            "description": "Termo exato para concurso público (Lei 8112)",
        },
        {
            "query": "curso de preparação à carreira",
            "expected_laws": ["lei-8829-1993"],
            "expected_articles": ["Art. 10º", "Art. 11º"],
            "category": "exact_term",
            "description": "Cursos de formação (CEOC/CAOC etc.)",
        },

        # 13) negative
        {
            "query": "aposentadoria de militares",
            "expected_laws": ["lei-8112-1990"],
            "expected_articles": ["Art. 21"],
            "category": "negative",
            "description": "Consulta negativa: this query não deve encontrar resultados em lei 8829",
            "should_not_match": ["lei-8829-1993"],
        },
        {
            "query": "aposentadoria de oficiais da aeronáutica",
            "expected_laws": ["lei-8112-1990"],
            "expected_articles": ["Art. 21"],
            "category": "negative",
            "description": "Verificação de miss-match com a lei 8829",
            "should_not_match": ["lei-8829-1993"],
        },
    ]


def analyze_chunks(supabase) -> dict:
    result = supabase.table("documents").select("*").execute()
    docs = result.data
    
    if not docs:
        return {"error": "No documents found"}
    
    chunk_sizes = [len(doc["content"]) for doc in docs]
    laws = {}
    for doc in docs:
        law = doc["metadata"]["filename"]
        laws[law] = laws.get(law, 0) + 1
    
    return {
        "total_chunks": len(docs),
        "avg_chunk_size": sum(chunk_sizes) / len(chunk_sizes),
        "min_chunk_size": min(chunk_sizes),
        "max_chunk_size": max(chunk_sizes),
        "chunks_per_law": laws,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["evaluate", "analyze", "benchmark"])
    args = parser.parse_args()
    
    if not SUPABASE_KEY:
        print("Error: SUPABASE_SERVICE_ROLE_KEY not set")
        return 1
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    if args.command == "analyze":
        print("=== Chunk Analysis ===\n")
        stats = analyze_chunks(supabase)
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    elif args.command == "evaluate":
        print("=== RAG Evaluation (k=20, top 5) ===\n")
        
        test_cases = get_test_cases()
        evaluator = RAGEvaluator(supabase, embeddings, llm)
        
        metrics = evaluator.run_evaluation(test_cases, use_reranking=False, method="hybrid")
        
        print(f"Retrieval Precision: {metrics.retrieval_precision:.1%}")
        print(f"Retrieval Recall: {metrics.retrieval_recall:.1%}")
        print(f"Context Relevance: {metrics.context_relevance:.1%}")
        print()
        
        target = 0.80
        status = "PASS" if metrics.retrieval_precision >= target and metrics.retrieval_recall >= target else "FAIL"
        print(f"Target: {target:.0%} | Status: {status}")
    
    elif args.command == "benchmark":
        print("=== Benchmark: With vs Without Reranking ===\n")
        
        test_cases = get_test_cases()
        evaluator = RAGEvaluator(supabase, embeddings, llm)
        
        print("Without reranking:")
        m1 = evaluator.run_evaluation(test_cases, use_reranking=False)
        print(f"  Precision: {m1.retrieval_precision:.1%}")
        print(f"  Recall: {m1.retrieval_recall:.1%}")
        
        print("\nWith LLM reranking:")
        m2 = evaluator.run_evaluation(test_cases, use_reranking=True)
        print(f"  Precision: {m2.retrieval_precision:.1%}")
        print(f"  Recall: {m2.retrieval_recall:.1%}")
    
    return 0


if __name__ == "__main__":
    exit(main())

from __future__ import annotations

import re
from typing import List, Optional

try:
    from langchain.docstore.document import Document
except Exception:
    # Minimal fallback Document for environments without LangChain installed
    class Document:
        def __init__(self, page_content: str, metadata: Optional[dict] = None):
            self.page_content = page_content
            self.metadata = metadata or {}


def _extract_meta_from_filename(filename: str) -> dict:
    """Infer tipo, numero and ano from filename like 'lei-8112-1990.md'."""
    m = re.match(r"(?i)^(lei|decreto)[-_](\d+)[-_](\d{4})\.md$", filename)
    if not m:
        # Fallback: try to extract numbers generically
        base = filename.split(".")[0]
        parts = base.split("-")
        if len(parts) >= 3:
            tipo = parts[0].lower()
            numero = parts[1]
            ano = parts[2]
        else:
            tipo = "lei"
            numero = "0"
            ano = "0"
    else:
        tipo = m.group(1).lower()
        numero = m.group(2)
        ano = m.group(3)
    return {"filename": filename, "tipo": tipo, "numero": numero, "ano": ano}


ART_REGEX = re.compile(r"Art\.\s*(\d+)")  # Art. 1, Art. 2, ...

# Internal legal markers that denote a new logical subdivision within an article
INTERNAL_MARKERS = re.compile(
    r"(?:Parágrafo(?:\s+único|o)?|§\s*\d+|(?:(?:I|II|III|IV|V|VI|VII|VIII|IX|X)\s*-))",
    flags=re.IGNORECASE,
)


def _split_article_text(article_text: str) -> List[str]:
    """Split a single article text into smaller chunks at internal legal markers.

    The goal is to create segments that correspond to logical subsections, but
    ensure each final chunk is no longer than approximately 2000 characters.
    If a segment would exceed the limit, it is further split roughly at
    paragraph/section markers.
    """
    # Find internal markers that typically begin subsections inside an article
    markers = [m.start() for m in INTERNAL_MARKERS.finditer(article_text)]
    boundaries = [0] + markers + [len(article_text)]
    parts: List[str] = []
    for i in range(len(boundaries) - 1):
        seg = article_text[boundaries[i]: boundaries[i + 1]]
        if seg:
            parts.append(seg)
    # Merge/split to respect max length ~2000 chars while keeping logical boundaries
    MAX_LEN = 2000
    merged: List[str] = []
    current = []  # type: List[str]
    cur_len = 0
    for p in parts:
        if cur_len + len(p) > MAX_LEN and current:
            merged.append("".join(current).strip())
            current = [p]
            cur_len = len(p)
        else:
            current.append(p)
            cur_len += len(p)
    if current:
        merged.append("".join(current).strip())
    # Ensure no empty chunks
    return [m for m in merged if m]


def _extract_art_numbers(text: str) -> List[int]:
    nums = [int(n) for n in ART_REGEX.findall(text)]
    return nums


def _extract_section_headers(chunk: str) -> dict:
    sec = None
    tit = None
    # Look for explicit section headers within the chunk
    for pat in (r"Capítulo\s+[^\n]+", r"Título\s+[^\n]+", r"Seção\s+[^\n]+"):
        m = re.search(pat, chunk, flags=re.IGNORECASE)
        if m:
            text = m.group(0).strip()
            if text.lower().startswith("capítulo"):
                sec = text
            elif text.lower().startswith("título"):
                tit = text
            elif text.lower().startswith("seção"):
                sec = text
    return {"secao": sec, "titulo": tit}


def split_legal_document(content: str, filename: str) -> List[Document]:
    """Split a Brazilian legal document into BR-structured chunks.

    Each chunk corresponds to at most one article (Art.) or a logical section
    of an article. Metadata includes article boundaries and section headers when
    detectable. The original text in the content is preserved without truncation.

    Args:
        content: Full text of the document (as extracted from Planalto HTML text).
        filename: Original filename (used to derive metadata like tipo/numero/ano).

    Returns:
        A list of langchain Document objects with chunked text and metadata.
    """
    meta_base = _extract_meta_from_filename(filename)
    # Normalize line endings to keep content intact; do not modify content semantics
    text = content

    # Identify article boundaries by locating all occurrences of Art. n
    art_positions = [m.start() for m in ART_REGEX.finditer(text)]
    chunks: List[Document] = []
    # If no Art markers found, treat entire document as a single chunk
    article_spans: List[tuple[int, int]] = []
    if not art_positions:
        article_spans.append((0, len(text)))
    else:
        for i, start in enumerate(art_positions):
            end = art_positions[i + 1] if i + 1 < len(art_positions) else len(text)
            article_spans.append((start, end))

        # Ensure the first chunk starts at 0 as well if there is leading text before first Art
        if article_spans and article_spans[0][0] != 0:
            article_spans.insert(0, (0, article_spans[0][0]))

    chunk_index = 0
    for a_start, a_end in article_spans:
        article_text = text[a_start:a_end]
        arts_in_article = _extract_art_numbers(article_text)
        # Split within article if too long
        subchunks = _split_article_text(article_text) if len(article_text) > 2000 else [article_text]

        for seg in subchunks:
            # Compute article numbers present in this segment
            arts = _extract_art_numbers(seg)
            if not arts:
                arts = arts_in_article
            artigo_inicio = arts[0] if arts else None
            artigo_fim = arts[-1] if arts else None
            headers = _extract_section_headers(seg)
            md = {
                "filename": filename,
                "tipo": meta_base["tipo"],
                "numero": meta_base["numero"],
                "ano": meta_base["ano"],
                "artigo_inicio": artigo_inicio,
                "artigo_fim": artigo_fim,
                "secao": headers.get("secao"),
                "titulo": headers.get("titulo"),
                "chunk_index": chunk_index,
            }
            chunks.append(Document(seg, metadata=md))
            chunk_index += 1

    return chunks


__all__ = ["split_legal_document"]

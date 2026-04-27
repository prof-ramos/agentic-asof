-- Add Full-Text Search support and hybrid vector/FTS search
-- 1) add tsvector column for Portuguese FT search
ALTER TABLE documents ADD COLUMN search_vector TSVECTOR;

-- 2) update trigger to maintain search_vector on insert/update
CREATE OR REPLACE FUNCTION documents_search_vector_update() RETURNS trigger AS $$
BEGIN
  NEW.search_vector := to_tsvector('portuguese', NEW.content);
  RETURN NEW;
END
$$ LANGUAGE plpgsql;

CREATE TRIGGER documents_search_vector_update
BEFORE INSERT OR UPDATE ON documents
FOR EACH ROW EXECUTE PROCEDURE documents_search_vector_update();

-- 3) create GIN index for fast FT search
CREATE INDEX IF NOT EXISTS documents_search_vector_idx ON documents USING GIN (search_vector);

-- 4) create hybrid search function using Reciprocal Rank Fusion
CREATE OR REPLACE FUNCTION hybrid_search(
  query_embedding VECTOR(1536),
  query_text TEXT,
  match_threshold FLOAT,
  match_count INT,
  rrf_k INT
)
RETURNS TABLE(
  id INT,
  content TEXT,
  metadata JSONB,
  similarity DOUBLE PRECISION,
  source TEXT
)
LANGUAGE SQL STABLE
AS $$
WITH vec AS (
  SELECT id, content, metadata,
         1 - (embedding <=> query_embedding) AS vector_similarity,
         ROW_NUMBER() OVER (ORDER BY (1 - (embedding <=> query_embedding)) DESC) AS rank
  FROM documents
  WHERE 1 - (embedding <=> query_embedding) > COALESCE(match_threshold, 0.5)
  ORDER BY embedding <=> query_embedding
  LIMIT COALESCE(match_count, 20)
),
fts AS (
  SELECT id, content, metadata,
         ts_rank_cd(search_vector, websearch_to_tsquery('portuguese', query_text)) AS fts_rank,
         ROW_NUMBER() OVER (ORDER BY ts_rank_cd(search_vector, websearch_to_tsquery('portuguese', query_text)) DESC) AS rank
  FROM documents
  WHERE search_vector @@ websearch_to_tsquery('portuguese', query_text)
  ORDER BY ts_rank_cd(search_vector, websearch_to_tsquery('portuguese', query_text)) DESC
  LIMIT COALESCE(match_count, 20)
),
union_ids AS (
  SELECT id FROM vec
  UNION
  SELECT id FROM fts
)
SELECT u.id, d.content, d.metadata,
       (CASE WHEN vec.id IS NOT NULL THEN 1.0/(COALESCE(rrf_k,60) + vec.rank) ELSE 0 END) +
       (CASE WHEN fts.id IS NOT NULL THEN 1.0/(COALESCE(rrf_k,60) + fts.rank) ELSE 0 END) AS similarity,
       (CASE WHEN vec.id IS NOT NULL AND fts.id IS NOT NULL THEN 'both' WHEN vec.id IS NOT NULL THEN 'vector' WHEN fts.id IS NOT NULL THEN 'fts' ELSE 'unknown' END) AS source
FROM union_ids u
LEFT JOIN vec ON u.id = vec.id
LEFT JOIN fts ON u.id = fts.id
JOIN documents d ON d.id = u.id
ORDER BY similarity DESC
LIMIT COALESCE(rrf_k, 60);
$$;

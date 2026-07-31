CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS embedding_indexes (
  index_id text PRIMARY KEY,
  model_name text NOT NULL,
  model_version text NOT NULL,
  dimension integer NOT NULL CHECK (dimension = 3),
  normalized boolean NOT NULL,
  distance text NOT NULL CHECK (distance IN ('cosine')),
  status text NOT NULL CHECK (status IN ('building', 'ready', 'active', 'retired'))
);

CREATE UNIQUE INDEX IF NOT EXISTS one_active_embedding_index
  ON embedding_indexes ((status))
  WHERE status = 'active';

CREATE TABLE IF NOT EXISTS chunk_embeddings (
  index_id text NOT NULL REFERENCES embedding_indexes(index_id),
  chunk_id text NOT NULL,
  owner_id text NOT NULL,
  source_id text NOT NULL,
  source_version integer NOT NULL,
  text_value text NOT NULL,
  embedding vector(3) NOT NULL,
  PRIMARY KEY (index_id, chunk_id)
);

CREATE INDEX IF NOT EXISTS chunk_embeddings_hnsw_cosine
  ON chunk_embeddings USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS chunk_embeddings_acl
  ON chunk_embeddings (owner_id, index_id);

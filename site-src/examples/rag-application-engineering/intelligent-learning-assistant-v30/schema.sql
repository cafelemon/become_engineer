CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS knowledge_sources (
  source_id text PRIMARY KEY,
  owner_id text NOT NULL,
  name text NOT NULL,
  status text NOT NULL CHECK (status IN ('active','inactive'))
);
CREATE TABLE IF NOT EXISTS document_versions (
  version_id text PRIMARY KEY,
  source_id text NOT NULL REFERENCES knowledge_sources(source_id),
  version integer NOT NULL,
  kind text NOT NULL,
  checksum text NOT NULL,
  status text NOT NULL,
  UNIQUE(source_id, version), UNIQUE(source_id, checksum)
);
CREATE TABLE IF NOT EXISTS document_blocks (
  block_id text PRIMARY KEY,
  version_id text NOT NULL REFERENCES document_versions(version_id),
  page integer,
  title_path jsonb NOT NULL DEFAULT '[]'
);
CREATE TABLE IF NOT EXISTS chunks (
  chunk_id text PRIMARY KEY,
  version_id text NOT NULL REFERENCES document_versions(version_id),
  block_id text NOT NULL REFERENCES document_blocks(block_id),
  strategy_version text NOT NULL,
  fingerprint text NOT NULL,
  body text NOT NULL
);
CREATE TABLE IF NOT EXISTS embedding_indexes (
  index_id text PRIMARY KEY,
  model_name text NOT NULL,
  model_version text NOT NULL,
  dimensions integer NOT NULL,
  normalized boolean NOT NULL,
  distance text NOT NULL,
  status text NOT NULL CHECK (status IN ('building','active','retired'))
);
CREATE TABLE IF NOT EXISTS chunk_embeddings (
  index_id text NOT NULL REFERENCES embedding_indexes(index_id),
  chunk_id text NOT NULL REFERENCES chunks(chunk_id),
  embedding vector(3) NOT NULL,
  PRIMARY KEY(index_id, chunk_id)
);
CREATE TABLE IF NOT EXISTS ingestion_jobs (
  job_id text PRIMARY KEY,
  source_id text NOT NULL REFERENCES knowledge_sources(source_id),
  version integer NOT NULL,
  status text NOT NULL,
  attempts integer NOT NULL DEFAULT 0,
  error_code text
);
CREATE TABLE IF NOT EXISTS retrieval_runs (
  retrieval_run_id text PRIMARY KEY,
  subject_id text NOT NULL,
  query_text text NOT NULL,
  prompt_version text NOT NULL,
  stage_counts jsonb NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS chat_sessions (
  session_id text PRIMARY KEY,
  owner_id text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS chat_messages (
  message_id text PRIMARY KEY,
  session_id text NOT NULL REFERENCES chat_sessions(session_id),
  role text NOT NULL,
  body text NOT NULL,
  citations jsonb NOT NULL DEFAULT '[]',
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS audit_events (
  event_id bigserial PRIMARY KEY,
  subject_id text NOT NULL,
  action text NOT NULL,
  resource_id text,
  result text NOT NULL,
  request_id text,
  created_at timestamptz NOT NULL DEFAULT now()
);

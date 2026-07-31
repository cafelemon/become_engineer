# Intelligent learning assistant v0.30

This teaching build joins the document-management and chat application boundary. The default service is deterministic and in-memory so unit and browser tests stay offline; the Compose database applies the real PostgreSQL/pgvector schema. v0.27 remains the real exact/HNSW/index-switch implementation. A production adapter must persist every service mutation before readiness can be claimed.

```bash
../../../../.venv/bin/python -m unittest -v test_knowledge_service.py test_api.py
../../web-engineering/learning-dashboard-v12/node_modules/.bin/tsc -p tsconfig.json
../../../../.venv/bin/uvicorn app:app --host 127.0.0.1 --port 8000
```

For the real schema, create the untracked `secrets/db_password.txt`, run `docker compose up -d db`, obtain its random/local mapped port, and set `RAG_APP_DATABASE_URL` before running `test_postgres_schema.py`. Do not commit the password. The optional model requirements file is documentation only.

import os
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import quote_plus
from fastapi import FastAPI, HTTPException
import psycopg

@asynccontextmanager
async def lifespan(application: FastAPI):
    application.state.accepting_requests = True
    yield
    application.state.accepting_requests = False

app = FastAPI(version="0.13.0", lifespan=lifespan)
@app.get("/health/live")
def live(): return {"status":"live"}
@app.get("/health/ready")
def ready():
    template = os.environ.get("DATABASE_URL")
    secret_file = os.environ.get("DATABASE_PASSWORD_FILE")
    if not template or not secret_file: raise HTTPException(503, "database configuration missing")
    try:
        password = quote_plus(Path(secret_file).read_text(encoding="utf-8").strip())
        with psycopg.connect(template.format(password=password), connect_timeout=1) as connection:
            connection.execute("SELECT 1").fetchone()
    except (OSError, psycopg.Error, KeyError) as error:
        raise HTTPException(503, "database not ready") from error
    return {"status":"ready"}

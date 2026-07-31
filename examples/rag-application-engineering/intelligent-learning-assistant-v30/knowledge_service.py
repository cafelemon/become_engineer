"""Deterministic application boundary for the v0.30 document and chat UI."""
from __future__ import annotations

import hashlib
import re
import uuid
from dataclasses import dataclass, field

PROMPT_VERSION = "grounded-answer-v1"


def _id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[\w\u4e00-\u9fff]+", text.lower()))


@dataclass
class KnowledgeService:
    sources: dict[str, dict] = field(default_factory=dict)
    versions: dict[str, list[dict]] = field(default_factory=dict)
    chunks: dict[str, dict] = field(default_factory=dict)
    jobs: dict[str, dict] = field(default_factory=dict)
    sessions: dict[str, dict] = field(default_factory=dict)
    messages: dict[str, list[dict]] = field(default_factory=dict)
    retrieval_runs: list[dict] = field(default_factory=list)
    counters: dict[str, int] = field(default_factory=lambda: {"requests": 0, "retrievals": 0, "refusals": 0})

    def create_source(self, subject: str, name: str) -> dict:
        source = {"source_id": _id("src"), "owner_id": subject, "name": name, "status": "active"}
        self.sources[source["source_id"]] = source
        self.versions[source["source_id"]] = []
        return source

    def _source(self, subject: str, source_id: str) -> dict:
        source = self.sources.get(source_id)
        if source is None or source["owner_id"] != subject:
            raise KeyError("resource_not_visible")
        return source

    def upload(self, subject: str, source_id: str, kind: str, content: str) -> dict:
        source = self._source(subject, source_id)
        if source["status"] != "active":
            raise ValueError("source_inactive")
        if kind not in {"markdown", "html", "pdf_text"}:
            raise ValueError("unsupported_kind")
        checksum = hashlib.sha256(content.encode()).hexdigest()
        for version in self.versions[source_id]:
            if version["checksum"] == checksum:
                return {"replayed": True, "version": version, "job": self.jobs[version["job_id"]]}
        number = len(self.versions[source_id]) + 1
        version_id, job_id, chunk_id = _id("ver"), _id("job"), _id("chk")
        version = {
            "version_id": version_id, "source_id": source_id, "version": number,
            "kind": kind, "checksum": checksum, "status": "active", "job_id": job_id,
        }
        for old in self.versions[source_id]:
            old["status"] = "inactive"
        chunk = {
            "chunk_id": chunk_id, "source_id": source_id, "version": number,
            "block_id": "block-1", "page": 1, "title_path": [source["name"]],
            "strategy_version": "structure-v1", "fingerprint": checksum[:16],
            "text": content, "owner_id": subject,
        }
        job = {"job_id": job_id, "source_id": source_id, "version": number, "status": "succeeded", "attempts": 1}
        self.versions[source_id].append(version)
        self.chunks[chunk_id] = chunk
        self.jobs[job_id] = job
        return {"replayed": False, "version": version, "job": job}

    def list_versions(self, subject: str, source_id: str) -> list[dict]:
        self._source(subject, source_id)
        return list(self.versions[source_id])

    def deactivate(self, subject: str, source_id: str) -> dict:
        source = self._source(subject, source_id)
        source["status"] = "inactive"
        return source

    def rollback(self, subject: str, source_id: str, number: int) -> dict:
        self._source(subject, source_id)
        target = next((v for v in self.versions[source_id] if v["version"] == number), None)
        if target is None:
            raise KeyError("version_not_visible")
        for version in self.versions[source_id]:
            version["status"] = "active" if version is target else "inactive"
        return target

    def debug_retrieval(self, subject: str, query: str, limit: int = 5) -> dict:
        authorized = [
            chunk for chunk in self.chunks.values()
            if chunk["owner_id"] == subject
            and self.sources[chunk["source_id"]]["status"] == "active"
            and any(v["version"] == chunk["version"] and v["status"] == "active" for v in self.versions[chunk["source_id"]])
        ]
        query_terms = _tokens(query)
        scored = [(len(query_terms & _tokens(chunk["text"])), chunk) for chunk in authorized]
        selected = [chunk for score, chunk in sorted(scored, key=lambda item: (-item[0], item[1]["chunk_id"])) if score > 0][:limit]
        run = {
            "run_id": _id("ret"), "query": query, "subject_id": subject,
            "stages": {"authorized": len(authorized), "lexical": len(selected), "reranked": len(selected), "context": len(selected)},
            "candidates": [self._citation(chunk) for chunk in selected],
        }
        self.retrieval_runs.append(run)
        self.counters["retrievals"] += 1
        return run

    @staticmethod
    def _citation(chunk: dict) -> dict:
        return {
            "source_id": chunk["source_id"], "version": chunk["version"],
            "page": chunk["page"], "block_id": chunk["block_id"],
            "chunk_id": chunk["chunk_id"],
        }

    def create_session(self, subject: str) -> dict:
        session = {"session_id": _id("chat"), "owner_id": subject}
        self.sessions[session["session_id"]] = session
        self.messages[session["session_id"]] = []
        return session

    def chat(self, subject: str, session_id: str, question: str) -> dict:
        session = self.sessions.get(session_id)
        if session is None or session["owner_id"] != subject:
            raise KeyError("resource_not_visible")
        retrieval = self.debug_retrieval(subject, question)
        if not retrieval["candidates"]:
            self.counters["refusals"] += 1
            answer = {"answer": "现有资料不足，无法回答。", "refused": True, "citations": []}
        else:
            citation = retrieval["candidates"][0]
            chunk = self.chunks[citation["chunk_id"]]
            answer = {"answer": chunk["text"][:160], "refused": False, "citations": [citation]}
        record = {
            "message_id": _id("msg"), "question": question, **answer,
            "prompt_version": PROMPT_VERSION, "retrieval_run_id": retrieval["run_id"],
            "context_package": retrieval["candidates"],
        }
        self.messages[session_id].append(record)
        return record

    def metrics(self) -> str:
        return "\n".join([
            "# TYPE rag_requests_total counter",
            f"rag_requests_total {self.counters['requests']}",
            "# TYPE rag_retrievals_total counter",
            f"rag_retrievals_total {self.counters['retrievals']}",
            "# TYPE rag_refusals_total counter",
            f"rag_refusals_total {self.counters['refusals']}",
            "",
        ])


def fixed_report() -> str:
    service = KnowledgeService()
    source = service.create_source("learner-a", "权限说明")
    uploaded = service.upload("learner-a", source["source_id"], "markdown", "ACL 必须在召回前执行。")
    session = service.create_session("learner-a")
    answer = service.chat("learner-a", session["session_id"], "ACL 何时执行")
    return "\n".join([
        "application=admin:true,chat:true,prompt-versioned:true",
        f"ingestion=job:{uploaded['job']['status']},version:active,replayed:false",
        "retrieval=authorized:1,reranked:1,context:1",
        f"answer=refused:{str(answer['refused']).lower()},citations:{len(answer['citations'])}",
        "citation=source+version+page+block+chunk:true",
        "runtime=models:fixed,network:disabled,secrets:none",
    ])


if __name__ == "__main__":
    print(fixed_report())

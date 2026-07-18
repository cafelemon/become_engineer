PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS learners (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    completed_lessons INTEGER NOT NULL CHECK (completed_lessons >= 0),
    status TEXT NOT NULL CHECK (status IN ('起步中', '按计划推进', '本周已完成')),
    next_milestone TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS study_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    learner_id TEXT NOT NULL,
    hours REAL NOT NULL CHECK (
        hours > 0
        AND hours <= 24
        AND hours * 4 = CAST(hours * 4 AS INTEGER)
    ),
    note TEXT NOT NULL CHECK (length(trim(note)) BETWEEN 2 AND 200),
    idempotency_key TEXT UNIQUE,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (learner_id) REFERENCES learners(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_study_sessions_learner_id_id
    ON study_sessions(learner_id, id);

PRAGMA user_version = 3;

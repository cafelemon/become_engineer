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
    hours REAL NOT NULL CHECK (hours > 0 AND hours <= 24),
    note TEXT NOT NULL CHECK (length(note) BETWEEN 1 AND 200),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (learner_id) REFERENCES learners(id) ON DELETE CASCADE
);

PRAGMA user_version = 1;

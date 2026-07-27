"""initial PostgreSQL learning data

Revision ID: 0001_postgres_learning_data
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_postgres_learning_data"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("learners", sa.Column("learner_id", sa.String(32), primary_key=True), sa.Column("name", sa.String(80), nullable=False), sa.Column("description", sa.Text(), nullable=False))
    op.create_table("study_sessions", sa.Column("session_id", sa.Integer(), primary_key=True), sa.Column("learner_id", sa.String(32), sa.ForeignKey("learners.learner_id", ondelete="CASCADE"), nullable=False), sa.Column("hours", sa.Numeric(5, 2), nullable=False), sa.Column("note", sa.String(200), nullable=False), sa.Column("idempotency_key", sa.String(80), nullable=False, unique=True), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")))


def downgrade() -> None:
    op.drop_table("study_sessions")
    op.drop_table("learners")

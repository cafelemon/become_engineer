"""server-side authentication sessions

Revision ID: 0002_auth_sessions
Revises: 0001_postgres_learning_data
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_auth_sessions"
down_revision = "0001_postgres_learning_data"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("user_id", sa.String(36), primary_key=True),
        sa.Column("username", sa.String(80), nullable=False, unique=True),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("role", sa.String(24), nullable=False),
        sa.CheckConstraint("role IN ('learner', 'operator')", name="ck_users_role"),
    )
    op.create_table(
        "auth_sessions",
        sa.Column("session_id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_digest", sa.String(64), nullable=False, unique=True),
        sa.Column("csrf_digest", sa.String(64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_auth_sessions_user_expires", "auth_sessions", ["user_id", "expires_at"])

def downgrade() -> None:
    op.drop_index("ix_auth_sessions_user_expires", table_name="auth_sessions")
    op.drop_table("auth_sessions")
    op.drop_table("users")

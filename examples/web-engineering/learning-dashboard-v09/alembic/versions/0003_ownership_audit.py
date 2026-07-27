"""resource ownership and redacted audit events

Revision ID: 0003_ownership_audit
Revises: 0002_auth_sessions
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_ownership_audit"
down_revision = "0002_auth_sessions"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column("learners", sa.Column("owner_user_id", sa.String(36)))
    op.create_foreign_key("fk_learners_owner_user", "learners", "users", ["owner_user_id"], ["user_id"], ondelete="RESTRICT")
    op.create_index("ix_learners_owner_user", "learners", ["owner_user_id"])
    op.create_table(
        "audit_events",
        sa.Column("event_id", sa.BigInteger(), primary_key=True),
        sa.Column("subject_user_id", sa.String(36), sa.ForeignKey("users.user_id", ondelete="SET NULL")),
        sa.Column("action", sa.String(80), nullable=False),
        sa.Column("resource_type", sa.String(80), nullable=False),
        sa.Column("resource_id", sa.String(80)),
        sa.Column("result", sa.String(32), nullable=False),
        sa.Column("request_id", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.CheckConstraint("result IN ('allowed','unauthenticated','forbidden','not_found')", name="ck_audit_result"),
    )
    op.create_index("ix_audit_request_id", "audit_events", ["request_id"])

def downgrade() -> None:
    op.drop_index("ix_audit_request_id", table_name="audit_events")
    op.drop_table("audit_events")
    op.drop_index("ix_learners_owner_user", table_name="learners")
    op.drop_constraint("fk_learners_owner_user", "learners", type_="foreignkey")
    op.drop_column("learners", "owner_user_id")

"""Initial schema.

Revision ID: 20261107_initial
Revises: None
Create Date: 2026-11-07
"""

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


revision = "20261107_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "businesses",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("owner_email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("widget_key", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("owner_email", name="uq_businesses_owner_email"),
        sa.UniqueConstraint("widget_key", name="uq_businesses_widget_key"),
    )
    op.create_index(op.f("ix_businesses_owner_email"), "businesses", ["owner_email"], unique=True)
    op.create_index(op.f("ix_businesses_widget_key"), "businesses", ["widget_key"], unique=True)

    op.create_table(
        "documents",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("business_id", sa.String(36), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_documents_business_id"), "documents", ["business_id"], unique=False)

    op.create_table(
        "chunks",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("document_id", sa.String(36), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(768), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_chunks_document_id"), "chunks", ["document_id"], unique=False)

    op.create_table(
        "conversations",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("business_id", sa.String(36), nullable=False),
        sa.Column("session_id", sa.String(length=64), nullable=False),
        sa.Column("language", sa.String(length=20), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_conversations_business_id"), "conversations", ["business_id"], unique=False)
    op.create_index(op.f("ix_conversations_session_id"), "conversations", ["session_id"], unique=False)
    op.create_index("ix_conversations_business_created", "conversations", ["business_id", "created_at"], unique=False)

    op.create_table(
        "messages",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("conversation_id", sa.String(36), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("sources", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_messages_conversation_id"), "messages", ["conversation_id"], unique=False)

    op.create_table(
        "tool_calls",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("message_id", sa.String(36), nullable=False),
        sa.Column("tool_name", sa.String(length=50), nullable=False),
        sa.Column("input", sa.JSON(), nullable=False),
        sa.Column("output", sa.JSON(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["message_id"], ["messages.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tool_calls_message_id"), "tool_calls", ["message_id"], unique=False)

    op.create_table(
        "handoffs",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("conversation_id", sa.String(36), nullable=False),
        sa.Column("reason", sa.String(length=255), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("claimed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("conversation_id", name="uq_handoffs_conversation_id"),
    )

    op.create_table(
        "mock_orders",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("business_id", sa.String(36), nullable=False),
        sa.Column("order_no", sa.String(length=50), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("items", sa.JSON(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("last_update", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("business_id", "order_no", name="uq_business_order_no"),
    )
    op.create_index(op.f("ix_mock_orders_business_id"), "mock_orders", ["business_id"], unique=False)
    op.create_index("ix_mock_orders_phone", "mock_orders", ["business_id", "phone"], unique=False)

    op.create_table(
        "mock_payments",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("business_id", sa.String(36), nullable=False),
        sa.Column("mpesa_code", sa.String(length=20), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("matched_order_no", sa.String(length=50), nullable=True),
        sa.Column("paid_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("business_id", "mpesa_code", name="uq_business_mpesa_code"),
    )
    op.create_index(op.f("ix_mock_payments_business_id"), "mock_payments", ["business_id"], unique=False)
    op.create_index("ix_mock_payments_code", "mock_payments", ["business_id", "mpesa_code"], unique=False)


def downgrade():
    op.drop_index("ix_mock_payments_code", table_name="mock_payments")
    op.drop_index(op.f("ix_mock_payments_business_id"), table_name="mock_payments")
    op.drop_table("mock_payments")
    op.drop_index("ix_mock_orders_phone", table_name="mock_orders")
    op.drop_index(op.f("ix_mock_orders_business_id"), table_name="mock_orders")
    op.drop_table("mock_orders")
    op.drop_table("handoffs")
    op.drop_index(op.f("ix_tool_calls_message_id"), table_name="tool_calls")
    op.drop_table("tool_calls")
    op.drop_index(op.f("ix_messages_conversation_id"), table_name="messages")
    op.drop_table("messages")
    op.drop_index("ix_conversations_business_created", table_name="conversations")
    op.drop_index(op.f("ix_conversations_session_id"), table_name="conversations")
    op.drop_index(op.f("ix_conversations_business_id"), table_name="conversations")
    op.drop_table("conversations")
    op.drop_index(op.f("ix_chunks_document_id"), table_name="chunks")
    op.drop_table("chunks")
    op.drop_index(op.f("ix_documents_business_id"), table_name="documents")
    op.drop_table("documents")
    op.drop_index(op.f("ix_businesses_widget_key"), table_name="businesses")
    op.drop_index(op.f("ix_businesses_owner_email"), table_name="businesses")
    op.drop_table("businesses")

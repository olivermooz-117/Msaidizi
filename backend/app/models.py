from datetime import datetime, timezone
import uuid
from typing import Optional, List

from sqlalchemy import (
    String, Text, Integer, Float, DateTime, ForeignKey, JSON,
    Index, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector

from backend.app.extensions import db


def gen_uuid() -> str:
    return str(uuid.uuid4())


def utcnow():
    return datetime.now(timezone.utc)


class Business(db.Model):
    __tablename__ = "businesses"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    widget_key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    documents: Mapped[List["Document"]] = relationship(back_populates="business", cascade="all, delete-orphan")
    conversations: Mapped[List["Conversation"]] = relationship(back_populates="business", cascade="all, delete-orphan")
    mock_orders: Mapped[List["MockOrder"]] = relationship(back_populates="business", cascade="all, delete-orphan")
    mock_payments: Mapped[List["MockPayment"]] = relationship(back_populates="business", cascade="all, delete-orphan")


class Document(db.Model):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    business_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("businesses.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)  # paste | pdf | csv
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    business: Mapped["Business"] = relationship(back_populates="documents")
    chunks: Mapped[List["Chunk"]] = relationship(back_populates="document", cascade="all, delete-orphan")


class Chunk(db.Model):
    __tablename__ = "chunks"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    document_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("documents.id"), nullable=False, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding = mapped_column(Vector(768), nullable=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    document: Mapped["Document"] = relationship(back_populates="chunks")

    __table_args__ = (
        Index(
            "ix_chunks_embedding",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )


class Conversation(db.Model):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    business_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("businesses.id"), nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    language: Mapped[Optional[str]] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="open")  # open | resolved | escalated
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    business: Mapped["Business"] = relationship(back_populates="conversations")
    messages: Mapped[List["Message"]] = relationship(back_populates="conversation", cascade="all, delete-orphan")
    handoff: Mapped[Optional["Handoff"]] = relationship(back_populates="conversation", uselist=False)

    __table_args__ = (
        Index("ix_conversations_business_created", "business_id", "created_at"),
    )


class Message(db.Model):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    conversation_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("conversations.id"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # customer | agent | human
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sources: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")
    tool_calls: Mapped[List["ToolCall"]] = relationship(back_populates="message", cascade="all, delete-orphan")


class ToolCall(db.Model):
    __tablename__ = "tool_calls"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    message_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("messages.id"), nullable=False, index=True)
    tool_name: Mapped[str] = mapped_column(String(50), nullable=False)
    input: Mapped[dict] = mapped_column(JSON, nullable=False)
    output: Mapped[Optional[dict]] = mapped_column(JSON)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer)

    message: Mapped["Message"] = relationship(back_populates="tool_calls")


class Handoff(db.Model):
    __tablename__ = "handoffs"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    conversation_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("conversations.id"), unique=True, nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending | claimed | resolved
    claimed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    conversation: Mapped["Conversation"] = relationship(back_populates="handoff")


class MockOrder(db.Model):
    __tablename__ = "mock_orders"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    business_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("businesses.id"), nullable=False, index=True)
    order_no: Mapped[str] = mapped_column(String(50), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    items: Mapped[dict] = mapped_column(JSON, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    last_update: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    business: Mapped["Business"] = relationship(back_populates="mock_orders")

    __table_args__ = (
        UniqueConstraint("business_id", "order_no", name="uq_business_order_no"),
        Index("ix_mock_orders_phone", "business_id", "phone"),
    )


class MockPayment(db.Model):
    __tablename__ = "mock_payments"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    business_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("businesses.id"), nullable=False, index=True)
    mpesa_code: Mapped[str] = mapped_column(String(20), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="completed")
    matched_order_no: Mapped[Optional[str]] = mapped_column(String(50))
    paid_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    business: Mapped["Business"] = relationship(back_populates="mock_payments")

    __table_args__ = (
        UniqueConstraint("business_id", "mpesa_code", name="uq_business_mpesa_code"),
        Index("ix_mock_payments_code", "business_id", "mpesa_code"),
    )

"""Session logger for tracking nickname generation sessions."""

import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from sqlalchemy import (
    JSON,
    Column,
    Engine,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
    event,
    select,
)

metadata = MetaData()

sessions_table = Table(
    "sessions",
    metadata,
    Column("session_id", Integer, primary_key=True, autoincrement=True),
    Column("process_id", String, nullable=False),
    Column("timestamp", String, nullable=False),
    Column("style", String, nullable=False),
    Column("qa_transcript", JSON, nullable=False),
    Column("nicknames", JSON, nullable=False),
    Column("llm_response_raw", Text, nullable=False),
)

feedback_table = Table(
    "feedback",
    metadata,
    Column("feedback_id", Integer, primary_key=True, autoincrement=True),
    Column(
        "session_id",
        Integer,
        ForeignKey("sessions.session_id"),
        nullable=False,
    ),
    Column("timestamp", String, nullable=False),
    Column("favorite_name", String),
    Column("helpful_questions", JSON),
    Column("unhelpful_questions", JSON),
    Column("suggested_questions", String),
    Column("self_suggested_name", String),
)


@event.listens_for(Engine, "connect")
def _set_sqlite_wal(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()


class SessionLogger:
    """Logs nickname generation sessions to a database."""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize the session logger.

        Args:
            db_path: Path to the SQLite database. Defaults to ./logs/sessions.db
                     relative to the project root. Ignored when DATABASE_URL is set.
        """
        if db_path is None:
            db_path = Path(__file__).parent.parent.parent / "logs" / "sessions.db"
        self.db_path = db_path
        self.process_id = str(uuid.uuid4())
        self.engine = self._create_engine(db_path)
        self._init_db()

    @staticmethod
    def _create_engine(db_path: Path) -> Engine:
        database_url = os.environ.get("DATABASE_URL")
        if database_url:
            return create_engine(database_url)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return create_engine(f"sqlite:///{db_path}")

    def _init_db(self) -> None:
        """Create tables if they don't exist."""
        try:
            metadata.create_all(self.engine)
        except Exception:
            pass

    def log_session(
        self,
        style: str,
        qa_transcript: list[dict],
        nicknames: list[str],
        llm_response_raw: str,
    ) -> Optional[int]:
        """Log a nickname generation session.

        Args:
            style: The style selected for generation.
            qa_transcript: List of Q&A dicts with 'q' and 'a' keys.
            nicknames: List of generated nicknames.
            llm_response_raw: Raw LLM response string.

        Returns:
            The session_id of the logged session, or None if logging failed.
        """
        try:
            timestamp = datetime.now(timezone.utc).isoformat()
            with self.engine.connect() as conn:
                result = conn.execute(
                    sessions_table.insert().values(
                        process_id=self.process_id,
                        timestamp=timestamp,
                        style=style,
                        qa_transcript=qa_transcript,
                        nicknames=nicknames,
                        llm_response_raw=llm_response_raw,
                    )
                )
                conn.commit()
                return result.inserted_primary_key[0]
        except Exception:
            return None

    def log_feedback(
        self,
        session_id: int,
        favorite_name: Optional[str],
        helpful_questions: list[str],
        unhelpful_questions: list[str],
        suggested_questions: str,
        self_suggested_name: str,
    ) -> Optional[int]:
        """Log feedback for a nickname generation session.

        Returns:
            The feedback_id, or None if logging failed.
        """
        try:
            timestamp = datetime.now(timezone.utc).isoformat()
            with self.engine.connect() as conn:
                result = conn.execute(
                    feedback_table.insert().values(
                        session_id=session_id,
                        timestamp=timestamp,
                        favorite_name=favorite_name,
                        helpful_questions=helpful_questions,
                        unhelpful_questions=unhelpful_questions,
                        suggested_questions=suggested_questions,
                        self_suggested_name=self_suggested_name,
                    )
                )
                conn.commit()
                return result.inserted_primary_key[0]
        except Exception:
            return None

    def dump_sessions(self, session_id: Optional[int] = None) -> str:
        """Return sessions as pretty-printed JSON.

        Args:
            session_id: If provided, dump only that session. Otherwise dump all.

        Returns:
            Pretty-printed JSON string.
        """
        query = (
            select(
                sessions_table,
                feedback_table.c.feedback_id,
                feedback_table.c.favorite_name,
                feedback_table.c.helpful_questions,
                feedback_table.c.unhelpful_questions,
                feedback_table.c.suggested_questions,
                feedback_table.c.self_suggested_name,
            )
            .select_from(
                sessions_table.outerjoin(
                    feedback_table,
                    sessions_table.c.session_id == feedback_table.c.session_id,
                )
            )
        )

        if session_id is not None:
            query = query.where(sessions_table.c.session_id == session_id)
        else:
            query = query.order_by(sessions_table.c.session_id)

        with self.engine.connect() as conn:
            rows = conn.execute(query).fetchall()

        sessions = []
        for row in rows:
            row_map = row._mapping
            qa = row_map["qa_transcript"]
            nicks = row_map["nicknames"]
            # Handle both raw JSON strings (legacy SQLite data) and
            # already-deserialized objects (SQLAlchemy JSON type)
            if isinstance(qa, str):
                qa = json.loads(qa)
            if isinstance(nicks, str):
                nicks = json.loads(nicks)

            session = {
                "session_id": row_map["session_id"],
                "process_id": row_map["process_id"],
                "timestamp": row_map["timestamp"],
                "style": row_map["style"],
                "qa_transcript": qa,
                "nicknames": nicks,
            }
            if row_map["feedback_id"] is not None:
                helpful = row_map["helpful_questions"]
                unhelpful = row_map["unhelpful_questions"]
                if isinstance(helpful, str):
                    helpful = json.loads(helpful)
                if isinstance(unhelpful, str):
                    unhelpful = json.loads(unhelpful)
                session["feedback"] = {
                    "favorite_name": row_map["favorite_name"],
                    "helpful_questions": helpful,
                    "unhelpful_questions": unhelpful,
                    "suggested_questions": row_map["suggested_questions"],
                    "self_suggested_name": row_map["self_suggested_name"],
                }
            else:
                session["feedback"] = None
            sessions.append(session)

        return json.dumps(sessions, indent=2)

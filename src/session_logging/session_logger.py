"""Session logger for tracking nickname generation sessions."""

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


class SessionLogger:
    """Logs nickname generation sessions to SQLite database."""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize the session logger.

        Args:
            db_path: Path to the SQLite database. Defaults to ./logs/sessions.db
                     relative to the project root.
        """
        if db_path is None:
            db_path = Path(__file__).parent.parent.parent / "logs" / "sessions.db"
        self.db_path = db_path
        self.process_id = str(uuid.uuid4())
        self._init_db()

    def _init_db(self) -> None:
        """Create the database and sessions table if they don't exist."""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        process_id TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        style TEXT NOT NULL,
                        qa_transcript TEXT NOT NULL,
                        nicknames TEXT NOT NULL,
                        llm_response_raw TEXT NOT NULL
                    )
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS feedback (
                        feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id INTEGER NOT NULL,
                        timestamp TEXT NOT NULL,
                        favorite_name TEXT,
                        helpful_questions TEXT,
                        unhelpful_questions TEXT,
                        suggested_questions TEXT,
                        self_suggested_name TEXT,
                        FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                    )
                """)
                conn.commit()
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
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO sessions (
                        process_id, timestamp, style, qa_transcript, nicknames, llm_response_raw
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        self.process_id,
                        timestamp,
                        style,
                        json.dumps(qa_transcript),
                        json.dumps(nicknames),
                        llm_response_raw,
                    ),
                )
                conn.commit()
                return cursor.lastrowid
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
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO feedback (
                        session_id, timestamp, favorite_name,
                        helpful_questions, unhelpful_questions,
                        suggested_questions, self_suggested_name
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        session_id,
                        timestamp,
                        favorite_name,
                        json.dumps(helpful_questions),
                        json.dumps(unhelpful_questions),
                        suggested_questions,
                        self_suggested_name,
                    ),
                )
                conn.commit()
                return cursor.lastrowid
        except Exception:
            return None

    def dump_sessions(self, session_id: Optional[int] = None) -> str:
        """Return sessions as pretty-printed JSON.

        Args:
            session_id: If provided, dump only that session. Otherwise dump all.

        Returns:
            Pretty-printed JSON string.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            query = """
                SELECT s.*, f.feedback_id, f.favorite_name,
                       f.helpful_questions, f.unhelpful_questions,
                       f.suggested_questions, f.self_suggested_name
                FROM sessions s
                LEFT JOIN feedback f ON s.session_id = f.session_id
            """
            if session_id is not None:
                rows = conn.execute(
                    query + " WHERE s.session_id = ?", (session_id,)
                ).fetchall()
            else:
                rows = conn.execute(
                    query + " ORDER BY s.session_id"
                ).fetchall()

        sessions = []
        for row in rows:
            row_dict = dict(row)
            session = {
                "session_id": row_dict["session_id"],
                "process_id": row_dict["process_id"],
                "timestamp": row_dict["timestamp"],
                "style": row_dict["style"],
                "qa_transcript": json.loads(row_dict["qa_transcript"]),
                "nicknames": json.loads(row_dict["nicknames"]),
            }
            if row_dict["feedback_id"] is not None:
                session["feedback"] = {
                    "favorite_name": row_dict["favorite_name"],
                    "helpful_questions": json.loads(row_dict["helpful_questions"]),
                    "unhelpful_questions": json.loads(row_dict["unhelpful_questions"]),
                    "suggested_questions": row_dict["suggested_questions"],
                    "self_suggested_name": row_dict["self_suggested_name"],
                }
            else:
                session["feedback"] = None
            sessions.append(session)

        return json.dumps(sessions, indent=2)



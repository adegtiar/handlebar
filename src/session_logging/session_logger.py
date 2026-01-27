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

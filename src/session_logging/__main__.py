"""Dump sessions as pretty-printed JSON.

Usage:
    python -m session_logging          # all sessions
    python -m session_logging 5        # session 5 only
"""

import sys

from session_logging.session_logger import SessionLogger

logger = SessionLogger()
sid = int(sys.argv[1]) if len(sys.argv) > 1 else None
print(logger.dump_sessions(sid))

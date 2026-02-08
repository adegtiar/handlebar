#!/usr/bin/env python3
"""Dump sessions as pretty-printed JSON.

Usage:
    ./scripts/dump_logs.py          # all sessions
    ./scripts/dump_logs.py 5        # session 5 only
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from session_logging.session_logger import SessionLogger

logger = SessionLogger()
sid = int(sys.argv[1]) if len(sys.argv) > 1 else None
print(logger.dump_sessions(sid))

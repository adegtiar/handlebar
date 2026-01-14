#!/bin/bash
cd "$CLAUDE_PROJECT_DIR" && python3 -m pytest --tb=short -q
exit 0

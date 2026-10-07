#!/usr/bin/env python3
"""Build-time patch: keep SQLAlchemy statement logging off in the app server.

SQLAlchemy sets its "sqlalchemy" logger to WARNING on import. When the
OpenHands SDK is imported afterwards, its setup_logging() raises the root
logger to INFO and also raises every existing logger whose level equals the
root's previous level (WARNING), which includes "sqlalchemy". Every SQL
statement is then logged at INFO through rich, ~50 lines per query, on the
single event-loop thread. Under streamed webhook load this made the app fall
behind, leak connections, and exhaust its file descriptors.

The fix resets "sqlalchemy" to WARNING at the end of the uvicorn entry module,
after the SDK import has run. App and access logs keep their levels.

Fails loudly if the upstream anchor moves, so an image version bump breaks the
build instead of silently restoring SQL logging.
"""

from __future__ import annotations

import sys
from pathlib import Path

TARGET = Path("/app/openhands/server/listen.py")

OLD_CODE = """from openhands.app_server.app import app

__all__ = ['app']
"""

NEW_CODE = """from openhands.app_server.app import app

__all__ = ['app']

# Patched: the SDK's setup_logging() promotes the "sqlalchemy" logger to INFO;
# reset it so SQL statements are not logged per query.
import logging as _logging

_logging.getLogger('sqlalchemy').setLevel(_logging.WARNING)
"""


def main() -> int:
    if not TARGET.exists():
        print(f"FATAL: patch target missing: {TARGET}", file=sys.stderr)
        return 1

    source = TARGET.read_text()

    if NEW_CODE in source:
        print("Patch already applied; nothing to do.")
        return 0

    if OLD_CODE not in source:
        print(
            f"FATAL: upstream anchor not found in {TARGET}.\n"
            "The vendored file changed upstream; re-derive the patch.",
            file=sys.stderr,
        )
        return 1

    source = source.replace(OLD_CODE, NEW_CODE, 1)
    TARGET.write_text(source)

    print("Patched: sqlalchemy logger reset to WARNING after SDK logging setup.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

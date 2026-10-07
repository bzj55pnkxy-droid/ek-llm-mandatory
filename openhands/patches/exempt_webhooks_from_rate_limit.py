#!/usr/bin/env python3
"""Build-time patch: exempt sandbox webhook callbacks from the per-IP rate limiter.

The app rate-limits every request by client IP (10/s, 429 above 20/s). All
Docker traffic reaches the app from one gateway IP, so sandbox event webhooks
(one event per streamed token), the browser UI, and API clients share that
budget. During a streamed LLM turn the sandbox exceeds it, gets 429s, retries,
and the held connections exhaust the app's file descriptors; the accept loop
then logs a traceback per failed accept and pins the CPU.

Webhook endpoints already require a valid sandbox X-Session-API-Key, so they
are exempted the same way upstream exempts sandbox resume requests.

Fails loudly if the upstream anchor moves, so an image version bump breaks the
build instead of silently restoring the rate limit on webhooks.
"""

from __future__ import annotations

import sys
from pathlib import Path

TARGET = Path("/app/openhands/app_server/middleware.py")

OLD_CODE = """        return not (
            request.url.path.startswith('/assets')
            or self._is_sandbox_resume_request(request)
        )"""

NEW_CODE = """        return not (
            request.url.path.startswith('/assets')
            or request.url.path.startswith('/api/v1/webhooks/')
            or self._is_sandbox_resume_request(request)
        )"""


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

    print("Patched: sandbox webhooks exempted from per-IP rate limiting.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

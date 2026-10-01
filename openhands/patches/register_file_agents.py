#!/usr/bin/env python3
"""Build-time patch: make the GUI load file-based sub-agents.

The GUI conversation path calls ``register_builtins_agents()`` but never
``register_file_agents()``, so Markdown agent definitions in
``~/.openhands/agents`` are never discovered. Everything downstream of the
registry already works -- the harvested definitions are forwarded to the
agent-server as ``agent_definitions`` and registered there on arrival -- so
this only needs to populate the app-server's own registry.

Fails loudly if the upstream anchors move, so an image version bump breaks
the build instead of silently reverting to built-in agents only.
"""

from __future__ import annotations

import sys
from pathlib import Path

TARGET = Path("/app/openhands/app_server/app_conversation/live_status_app_conversation_service.py")

IMPORT_OLD = "from openhands.sdk.subagent import get_registered_agent_definitions"
IMPORT_NEW = (
    "from openhands.sdk.subagent import (\n"
    "    get_registered_agent_definitions,\n"
    "    register_file_agents,\n"
    ")"
)

# Register file agents *before* built-ins so a user definition wins a name
# collision, matching the documented precedence order.
CALL_OLD = """            register_builtins_agents(enable_browser=True)
            tools = get_default_tools("""
CALL_NEW = """            register_file_agents(project_dir)
            register_builtins_agents(enable_browser=True)
            tools = get_default_tools("""


def main() -> int:
    if not TARGET.exists():
        print(f"FATAL: patch target missing: {TARGET}", file=sys.stderr)
        return 1

    source = TARGET.read_text()

    if "register_file_agents" in source:
        print("Patch already applied; nothing to do.")
        return 0

    for name, old in (("import", IMPORT_OLD), ("call site", CALL_OLD)):
        if old not in source:
            print(
                f"FATAL: upstream {name} anchor not found in {TARGET}.\n"
                "The vendored file changed upstream; re-derive the patch.",
                file=sys.stderr,
            )
            return 1

    source = source.replace(IMPORT_OLD, IMPORT_NEW, 1)
    source = source.replace(CALL_OLD, CALL_NEW, 1)
    TARGET.write_text(source)

    print("Patched: register_file_agents() added to GUI conversation path.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build-time patch: allow GUI main agent system prompt override from file.

When /.openhands/prompts/system_prompt.txt exists and is non-empty, load its
content and set agent.system_prompt verbatim, bypassing the default template.
Falls back to stock template behavior when the file is absent or empty.

Fails loudly if the upstream anchors move, so an image version bump breaks
the build instead of silently reverting to the default prompt.
"""

from __future__ import annotations

import sys
from pathlib import Path

TARGET = Path(
    "/app/openhands/app_server/app_conversation/live_status_app_conversation_service.py"
)

OLD_CODE = """        if agent_type == AgentType.PLAN:
            overrides['system_prompt_filename'] = 'system_prompt_planning.j2'
            overrides['system_prompt_kwargs'] = {
                'plan_structure': format_plan_structure()
            }
        else:
            overrides['system_prompt_kwargs'] = {'cli_mode': False}"""

NEW_CODE = """        if agent_type == AgentType.PLAN:
            overrides['system_prompt_filename'] = 'system_prompt_planning.j2'
            overrides['system_prompt_kwargs'] = {
                'plan_structure': format_plan_structure()
            }
        else:
            overrides['system_prompt_kwargs'] = {'cli_mode': False}
            prompt_path = '/.openhands/prompts/system_prompt.txt'
            if os.path.isfile(prompt_path) and os.path.getsize(prompt_path) > 0:
                with open(prompt_path, encoding='utf-8') as f:
                    custom_prompt = f.read().strip()
                if custom_prompt:
                    overrides['system_prompt'] = custom_prompt
                    _logger.info('Loaded custom system prompt override from %s', prompt_path)"""


def main() -> int:
    if not TARGET.exists():
        print(f"FATAL: patch target missing: {TARGET}", file=sys.stderr)
        return 1

    source = TARGET.read_text()

    if "/.openhands/prompts/system_prompt.txt" in source:
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

    print("Patched: custom system_prompt override added to GUI conversation path.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

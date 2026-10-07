# Patched OpenHands app image.
#
# Upstream GUI gaps patched at build time:
# 1. register_file_agents.py: The stock GUI never calls register_file_agents(),
#    so Markdown sub-agent definitions in ~/.openhands/agents are silently ignored.
# 2. override_system_prompt.py: Loads verbatim system prompt override from
#    /.openhands/prompts/system_prompt.txt for the main agent when present.
# 3. exempt_webhooks_from_rate_limit.py: Sandbox event webhooks share the
#    per-IP rate limit with the UI (all Docker traffic has one gateway IP);
#    streamed turns trip it and the retry storm pins the app's CPU.
# 4. quiet_sqlalchemy_logging.py: The SDK's logging setup promotes the
#    "sqlalchemy" logger to INFO, logging every SQL statement through rich;
#    under webhook load that stalls the single event-loop thread.
#
# The patch scripts abort the build if upstream anchors are missing, so an
# image version bump fails loudly here rather than silently reverting to
# stock behavior. Pin OPENHANDS_IMAGE when bumping.
ARG OPENHANDS_IMAGE=docker.openhands.dev/openhands/openhands:1.8
FROM ${OPENHANDS_IMAGE}

COPY patches/ /tmp/patches/

RUN python3 /tmp/patches/register_file_agents.py \
 && python3 /tmp/patches/override_system_prompt.py \
 && python3 /tmp/patches/exempt_webhooks_from_rate_limit.py \
 && python3 /tmp/patches/quiet_sqlalchemy_logging.py \
 && rm -rf /tmp/patches

# Patched OpenHands app image.
#
# The stock GUI never calls register_file_agents(), so Markdown sub-agent
# definitions in ~/.openhands/agents are silently ignored -- only the four
# built-in agents register. This layer applies patches/register_file_agents.py
# at build time.
#
# The patch script aborts the build if its upstream anchors are missing, so an
# image version bump fails loudly here rather than silently reverting to
# built-in agents only. Pin OPENHANDS_IMAGE when bumping.
ARG OPENHANDS_IMAGE=docker.openhands.dev/openhands/openhands:1.8
FROM ${OPENHANDS_IMAGE}

COPY patches/register_file_agents.py /tmp/patches/register_file_agents.py

RUN python3 /tmp/patches/register_file_agents.py && rm -rf /tmp/patches

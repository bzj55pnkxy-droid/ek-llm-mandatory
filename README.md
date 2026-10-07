# llm-mandatory

Two coding agents — [OpenHands](https://docs.openhands.dev) and [Pi](https://pi.dev) — configured with local dependencies and connected to local Ollama endpoints.

---

## Directory Layout

```text
openhands/
  pyproject.toml / uv.lock    local OpenHands SDK (v1.27.0) and uv (v0.12.21)
  config/settings.example.json  OpenHands model profiles template (copied to gitignored settings.json)
  prompts/
    system_prompt.txt         main agent (orchestrator) system prompt (full verbatim override)
  agents/
    architect.md, tech-lead.md, coder.md, tester.md, documenter.md, deployer.md
                              role sub-agents the orchestrator delegates to
    scout.md                  read-only exploration sub-agent
  tools/
    custom_tool.py            custom Python tools using openhands-sdk
  sandbox/chromium.d/webgl-swiftshader  Chromium flags mounted into every sandbox (software WebGL for screenshots)
pi/
  package.json / package-lock.json   local Pi SDK and CLI dependency (@earendil-works/pi-coding-agent v0.99.1)
  .pi/                        custom extensions, subagents, commands, and models
    models.json               local model provider definitions
    settings.json             project settings
    extensions/               custom tools and TypeScript modules
    agents/                   custom subagent definitions (.md files)
    prompts/                  custom slash commands (.md files)
```

*(Note: `docker-compose.yml` and `Makefile` provide host-agnostic orchestration for running OpenHands in Docker with bind mounts).*

---

## Local Dependencies

### 1. Prerequisites

#### Unix (macOS / Linux / WSL)
- **uv**: Install via the standalone script or Homebrew:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # or on macOS: brew install uv
  ```
- **Node.js (>= 22.19.0) & npm**: Install via your system package manager (e.g., `brew install node` on macOS, NodeSource/nvm on Linux).
- **Python 3.12+**: `uv` automatically downloads and manages a compatible Python version if one is not detected.

#### Windows (Native PowerShell)
- **uv**: Install via PowerShell or winget:
  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  # or via winget:
  # winget install --id=astral-sh.uv -e
  ```
- **Node.js (>= 22.19.0) & npm**: Install via winget or the official installer:
  ```powershell
  winget install OpenJS.NodeJS.LTS
  ```
- **Git for Windows** (recommended): Provides Git Bash, which Pi's built-in bash execution tool requires on native Windows:
  ```powershell
  winget install Git.Git
  ```
- **Python 3.12+**: Handled automatically by `uv`.

> **Note on WSL**: If developing on Windows via WSL2 (`wsl --install`), follow the Unix instructions inside your Linux distribution terminal.

---

### 2. Install Project Dependencies

From the repository root, install dependencies for both agents:

**Unix (macOS / Linux / WSL):**
```bash
uv sync --locked --project openhands
npm --prefix pi ci --ignore-scripts
```

**Windows (PowerShell / Command Prompt):**
```powershell
uv sync --locked --project openhands
npm --prefix pi ci --ignore-scripts
```

- OpenHands installs into `openhands/.venv/` (gitignored).
- Pi installs into `pi/node_modules/` (gitignored).
---

## LLM Endpoints (Ollama)

Both agents connect to Ollama instances (defaulting to `localhost` ports `11434` and `11435`) without requiring an API key.

Configure the endpoints via environment variables in `.env`:

```bash
# In .env (copied from .env.example)
OLLAMA_HOST=localhost                       # Host IP or hostname
OLLAMA_BASE_URL=http://localhost:11434/v1   # Instance 1 (port 11434)
OLLAMA_BASE_URL_11435=http://localhost:11435/v1 # Instance 2 (port 11435)
LLM_BASE_URL=http://localhost:11434/v1      # OpenHands base URL
```

- **Instance 1:** `OLLAMA_BASE_URL` (default: `http://localhost:11434/v1`)
- **Instance 2:** `OLLAMA_BASE_URL_11435` (default: `http://localhost:11435/v1`)

Available models on both ports:
- `qwen3.5-9b-openhands:latest`
- `ornith-1.5-openhands:latest`
- `qwen3.5:9b`
- `ornith-1.5:9b`

`pi/.pi/models.json` automatically interpolates `${OLLAMA_BASE_URL}` and `${OLLAMA_BASE_URL_11435}` from your environment without hardcoded IPs or arbitrary context limits.

---

## Usage

### 1. Pi (Interactive TUI / CLI)

Run Pi with `PI_CODING_AGENT_DIR=.pi` so it loads the project's `.pi/models.json` and local extensions:

**Unix (macOS / Linux / WSL):**
```bash
cd pi
PI_CODING_AGENT_DIR=.pi ./node_modules/.bin/pi --provider ollama-11434 --model "qwen3.5-9b-openhands:latest" -a
```

**Windows (PowerShell):**
```powershell
cd pi
$env:PI_CODING_AGENT_DIR = ".pi"
.\node_modules\.bin\pi.cmd --provider ollama-11434 --model "qwen3.5-9b-openhands:latest" -a
```

**Windows (Command Prompt):**
```cmd
cd pi
set PI_CODING_AGENT_DIR=.pi
.\node_modules\.bin\pi.cmd --provider ollama-11434 --model "qwen3.5-9b-openhands:latest" -a
```

*(The `-a` / `--approve` flag trusts project-local `.pi/` extensions and models).*

To target the second instance on port 11435, pass `--provider ollama-11435`.
### 2. OpenHands (Docker Web GUI)

To launch OpenHands with the browser GUI and your custom work bind-mounted:

```bash
make up
```

Once started:
- Open your browser to **`http://localhost:8000`**.
- **Workspace bind mount**: The `./workspace` directory on your host is mounted to `/opt/workspace_base` in the app container, and to `/workspace/project` (the agent's working directory) in every sandbox container via `SANDBOX_VOLUMES` in `docker-compose.yml`. Files the agent writes appear in `./workspace`. `WORKSPACE_DIR` must be an absolute host path because the host Docker daemon resolves it; sandboxes started before this mount existed keep their files inside the container.
- **Custom work bind mounts**:
  - `./openhands/config`: Persistent state, SQLite database (`openhands.db`), and the gitignored `settings.json` (created from `settings.example.json` on `make up`).
  - `./openhands/prompts`: Custom system prompts (`system_prompt.txt` overrides the main agent's prompt verbatim).
  - `./openhands/agents`: Custom subagent definitions (`architect.md`, `tech-lead.md`, `coder.md`, `tester.md`, `documenter.md`, `deployer.md`, `scout.md`). Mounted at `/root/.openhands/agents` — the container's `HOME` is `/root`, and the SDK resolves user-level agent directories from `Path.home()`. Mounting anywhere else silently loads nothing.
  - `./openhands/tools`: Custom tools.


#### Custom main agent system prompt

The main agent's system prompt is controlled via `./openhands/prompts/system_prompt.txt` (bind-mounted to `/.openhands/prompts/system_prompt.txt:ro`).

- **Verbatim override:** `system_prompt.txt` holds the orchestrator prompt and replaces the main agent's default static system prompt verbatim.
- **Fallback:** If `system_prompt.txt` is empty or deleted, OpenHands falls back to the default Jinja2 template (`system_prompt.j2`).
- **The `override_system_prompt.py` patch:** Stock OpenHands ignores custom prompt files for the main agent in the GUI conversation service. `openhands/Dockerfile` applies `patches/override_system_prompt.py` at build time to read this file and set `agent.system_prompt`.
- **Reloading:** Edit `openhands/prompts/system_prompt.txt` and run `make restart` (or `docker compose restart openhands`) to apply changes.

Verify that your custom prompt loaded:
```bash
docker compose logs openhands | grep "Loaded custom system prompt override"
```

#### Custom sub-agents

Sub-agents are Markdown files with YAML frontmatter. Discovery order (first match wins):

1. Programmatic `register_agent()`
2. Plugin agents
3. `{project}/.agents/agents/*.md`
4. `{project}/.openhands/agents/*.md`
5. `~/.agents/agents/*.md`
6. `~/.openhands/agents/*.md`

Only top-level `.md` files load; `README.md` is skipped. This repo uses the user-level path (6), bind-mounted from `./openhands/agents`; keep definitions there.

```markdown
---
name: scout
description: >
  Read-only codebase exploration specialist.
  <example>Where is auth handled?</example>
tools:
  - terminal
model: inherit
---

# Scout

You are a read-only exploration agent. Never create or modify anything.
```

Two required pieces beyond the Markdown file:

- **`enable_sub_agents: true`** in `agent_settings` (settings.json, or the GUI settings page). When false, the app skips `agent_definitions` entirely and omits the task tool, so registered agents are unusable. It defaults to `false`.
- **The `register_file_agents()` patch.** The stock GUI calls `register_builtins_agents()` but never `register_file_agents()`, so only the four built-ins (`general-purpose`, `code-explorer`, `bash-runner`, `web-researcher`) ever register. `openhands/Dockerfile` patches the vendored conversation service at build time to close that gap; `docker compose` builds it automatically.

Verify what registered:

```bash
docker compose logs openhands | grep "Registered file-based agent"
```

Registration is first-wins per process, so this logs once at first conversation start. Edit a definition and restart the container to pick up changes — sub-agents have no hot-reload.

> **Upgrades:** the patch script aborts the build if its upstream anchors are missing, so bumping `OPENHANDS_IMAGE` fails loudly rather than silently reverting to built-ins only. Re-derive `openhands/patches/register_file_agents.py` when that happens.
>
> **No GUI list:** the frontend never surfaces sub-agents — the string `subagent` does not appear in the bundle, and no endpoint exposes the registry. Delegation shows up in the transcript only after the main agent invokes it. Skills, by contrast, load into a browsable, searchable GUI surface.

**LLM streaming:** `openhands/config/settings.example.json` sets `"stream": true` for `agent_settings.llm` and both named profiles (`qwen3.5-9b-openhands` and `ornith-1.5-openhands`). `make up` copies the template only when `openhands/config/settings.json` is absent; existing saved settings are not overwritten. For an existing installation, set those same three `stream` fields to `true` in `openhands/config/settings.json` in place, preserving the models, credentials, and active profile rather than replacing the file with the template.

**Useful Make shortcuts:**
```bash
make up        # Start OpenHands in background and display GUI URL
make down      # Stop OpenHands
make restart   # Restart OpenHands container
make logs      # Follow container logs
make status    # Check container status
make shell     # Open interactive bash shell in the container
make clean     # Stop containers and remove orphans
```

*(Alternatively, using Docker Compose directly: `docker compose up -d` / `docker compose down`).*

### 3. OpenHands (Python SDK)

Run SDK scripts locally against the environment:

```bash
uv run --locked --project openhands python your_script.py
```
Model profiles live in `openhands/config/settings.example.json` and contain no endpoint URLs; the Ollama host comes from `OLLAMA_HOST` / `LLM_BASE_URL` in `.env` (forwarded as `OLLAMA_API_BASE`).

Models use the `ollama_chat/` provider prefix (Ollama `/api/chat`, native tool calling). Avoid `ollama/`: LiteLLM routes it to `/api/generate` and fakes tool calls with a JSON-mode prompt, which makes models like `ornith-1.5-openhands` invent tool names (e.g. `function_name`) or leak `{}` into the chat.

**Vision (images):** OpenHands decides vision support from LiteLLM's model registry, which has no entry for local Ollama models, so it silently strips images before they reach the model even though Ollama reports `vision` for both `qwen3.5-9b-openhands` and `ornith-1.5-openhands` (both `qwen35` family). Both profiles therefore set `"model_canonical_name": "dashscope/qwen3.5-plus"` (a registry entry for the same Qwen3.5 family flagged `supports_vision`) only for capability lookups; requests still go to the configured `ollama_chat/...` model. Because the canonical entry also carries a ~1M-token context window, the profiles pin `max_input_tokens` to `102400`, the models' Ollama `num_ctx`, and cap `max_output_tokens` at `32768`. For an existing installation, add those three fields to each profile (and to `agent_settings.llm`) in `openhands/config/settings.json`, then start a new conversation (existing conversations keep their stored LLM config).

**Context window:** both Ollama models run with `num_ctx 102400` (the model supports 262144). OpenHands alone spends ~22k tokens on the system prompt and tool definitions before any work, so the old 32k window left the main agent ~10k tokens and it could run out before answering. Each model then uses ~9 GB VRAM (KV cache: 8 full-attention layers × 32 KiB per token ≈ 3.1 GiB at 100K); the Ollama host holds one of the two at a time and swaps in ~3s. The value lives on the Ollama host, not in this repo; to change it, recreate the model in place over the API (Ollama has no auth, so anything that can reach the port can do this). Pass every existing parameter explicitly so none are lost, then check the result with `/api/show`:

```bash
curl http://<ollama-host>:11434/api/create -d '{"model":"qwen3.5-9b-openhands","from":"qwen3.5-9b-openhands","parameters":{"num_ctx":102400,"temperature":0.6,"top_p":0.95,"top_k":20,"min_p":0,"presence_penalty":0,"repeat_penalty":1},"stream":false}'
curl http://<ollama-host>:11434/api/create -d '{"model":"ornith-1.5-openhands","from":"ornith-1.5-openhands","parameters":{"num_ctx":102400,"temperature":1,"top_p":0.95,"top_k":20,"min_p":0,"presence_penalty":1.5,"repeat_penalty":1},"stream":false}'
```

Then set `max_input_tokens` to the same value in `settings.json`.

**Sampling:** set on the Ollama models, not in OpenHands (the SDK sends `temperature`/`top_p`/`top_k` only when set in `settings.json`, which would override them). Values are Qwen's Qwen3.5 thinking-mode recommendations: `qwen3.5-9b-openhands` uses the precise-coding set (temperature 0.6, presence_penalty 0), `ornith-1.5-openhands` the general-tasks set (temperature 1.0, presence_penalty 1.5); both top_p 0.95, top_k 20.

**Streaming and webhook batching:** with `"stream": true` every generated token becomes a `StreamingDeltaEvent` (~1 token, ~33/s, 99% of a conversation's events) that the sandbox posts back to the app (`/api/v1/webhooks/events/...`). At the sandbox's default batch of 5 that is ~7 posts/s; each post triggers SQL lookups that the app logged at INFO through `rich` (~50 lines per query), so it fell behind, held abandoned connections (`CLOSE_WAIT`) until it hit the 1024 file limit (`Errno 24`), and then spun at 100% CPU logging accept errors with the GUI unresponsive. Three fixes: `docker-compose.yml` sets `OH_WEBHOOKS_0_EVENT_BUFFER_SIZE=200` in `OH_AGENT_SERVER_ENV` (~40× fewer posts; the GUI streams tokens live from the sandbox websocket, so batching only delays the app's stored copy, flushed at 200 events or every 30s); `patches/quiet_sqlalchemy_logging.py` resets the `sqlalchemy` logger to WARNING, because the SDK's `setup_logging()` promotes every logger at root's old level (WARNING) to INFO; and `patches/exempt_webhooks_from_rate_limit.py` exempts webhooks from stock OpenHands' per-IP rate limit (10/s), which all Docker traffic shares through one gateway IP (webhooks already require the sandbox's `X-Session-API-Key`). Patch changes need `docker compose build openhands && make up`.

**Screenshots of web/WebGL apps:** agents with `browser_tool_set` (main agent, coder, tester, deployer) can call `browser_get_state` with `include_screenshot: true`; with vision active the screenshot reaches the model as an image. The prompts tell each role when to use it: the orchestrator (`system_prompt.txt`, § Verification and Phase 3 wave review) screenshots visual tickets, tech-lead writes concrete screenshot-checkable visual acceptance criteria, coder iterates on screenshots until they match, tester records a "Visual check" table in the quality report, and deployer confirms a web UI actually renders. Two pieces make canvas/WebGL (e.g. Three.js) render instead of a blank page: `docker-compose.yml` sets `OH_ENABLE_VNC=true` in `OH_AGENT_SERVER_ENV`, which starts the sandbox's X desktop (noVNC on sandbox port 8002) and makes the browser tool run headful; and `SANDBOX_VOLUMES` mounts `openhands/sandbox/chromium.d/webgl-swiftshader` into `/etc/chromium.d/`, switching Chromium to ANGLE/SwiftShader software WebGL. Headless Chromium cannot initialise GL in the arm64 sandbox, so both are required. The desktop makes sandbox startup take ~21s, past OpenHands' 15s default grace period, so compose sets `SANDBOX_STARTUP_GRACE_SECONDS=90`; without it new conversations fail with "Sandbox entered error state". The mount needs `REPO_DIR` (absolute repo path; `make up` sets it, set it in `.env` for plain `docker compose`). Applies to sandboxes created after `make up`; already-running sandboxes keep their old config.

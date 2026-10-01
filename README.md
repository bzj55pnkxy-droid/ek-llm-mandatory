# llm-mandatory

Two coding agents — [OpenHands](https://docs.openhands.dev) and [Pi](https://pi.dev) — configured with local dependencies and connected to local Ollama endpoints.

---

## Directory Layout

```text
openhands/
  pyproject.toml / uv.lock    local OpenHands SDK (v1.27.0) and uv (v0.12.21)
  config/settings.json        OpenHands LLM endpoint and model settings
  prompts/
    system_prompt.txt         custom system prompt (full verbatim override)
  agents/
    scout.md / worker.md      custom subagent definitions (.md files)
  tools/
    custom_tool.py            custom Python tools using openhands-sdk
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
- **Workspace bind mount**: The `./workspace` directory on your host is mounted to `/opt/workspace_base` (and passed to spawned sandbox containers via the host Docker daemon).
- **Custom work bind mounts**:
  - `./openhands/config`: Persistent state, SQLite database (`openhands.db`), and `settings.json`.
  - `./openhands/prompts`: Custom system prompts.
  - `./openhands/agents`: Custom subagent definitions (`scout.md`, `worker.md`).
  - `./openhands/tools`: Custom tools.

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
The default model and endpoint fallback are in `openhands/config/settings.json`, and can be overridden via `LLM_BASE_URL` or `OLLAMA_BASE_URL` in `.env`.

# Move the agent from Claude to ChatGPT

| Claude | ChatGPT / Codex equivalent | How |
|---|---|---|
| Personal preferences (identity) | Custom instructions | §1: paste [`instructions.md`](instructions.md) |
| Extended thinking | **Thinking** model (Pro if your plan has it) | model picker |
| Project (instructions + files) | ChatGPT **Project** | §2 |
| GitHub, Gmail, Google Drive connectors | Same apps: Settings → Apps | connect each one |
| PubMed connector | No verified first-party equivalent | web search / Deep research |
| NotebookLM MCP (this repo) | Developer-mode connector | §4 |
| Memory | ChatGPT Memory | send "Remember the following about me: …" with what Claude remembers |
| Claude Code + `CLAUDE.md` | **Codex CLI** + `AGENTS.md` | §3 |

The identity text asks for private step-by-step reasoning instead of a printed `<thinking>` block: ChatGPT's Thinking models do this natively.

## 1. Identity in every ChatGPT chat

Settings → Personalization → Custom instructions → paste all of `instructions.md` (~2.4k characters). Paid plans allow 5,000; Free/Go allow 1,500, so on those plans use a Project (§2, 8,000) instead.

## 2. This project in the ChatGPT app

Create a Project named `sprint-lm`. In its instructions, paste `instructions.md`, then this block:

```
## Project: sprint-lm
Repository: benhuezo2-tech/sprint-lm (TypeScript MCP server "notebooklm-mcp" that drives Chrome against Google NotebookLM).
Read code through the GitHub app. Project conventions: AGENTS.md at the repo root.
ChatGPT-compatibility work lives on branch claude/friendly-feynman-nj0w72.
```

Then connect the GitHub app and give it access to `benhuezo2-tech/sprint-lm`.

## 3. Terminal: Codex CLI (while Claude Code waits on usage)

```bash
npm install -g @openai/codex
mkdir -p ~/.codex && cat chatgpt/instructions.md >> ~/.codex/AGENTS.md   # identity in every repo
cd sprint-lm && codex                                                  # choose "Sign in with ChatGPT"
```

Codex reads `./AGENTS.md` for the repo rules. Add to `~/.codex/config.toml`:

```toml
model_reasoning_effort = "high"

[mcp_servers.notebooklm]
command = "node"
args = ["/absolute/path/to/sprint-lm/dist/index.js"]
tool_timeout_sec = 600   # default 60 s is too short for ask_question
```

**Hand off a stalled Claude Code task.** In the waiting Claude Code session run `/export handoff.md` (a local command; it needs no usage). Then tell Codex, in the same directory:

> Read handoff.md, run `git status` and `git diff`, and continue the task from where it stopped.

Codex sees Claude's uncommitted edits because it works on the same files. To keep both agents on one rulebook, make `@AGENTS.md` the first line of your local `CLAUDE.md`.

## 4. NotebookLM tools inside the ChatGPT app

Use this branch's build (`npx notebooklm-mcp@latest` is the upstream package without the fixes):

```bash
npm install                                  # builds dist/
node dist/index.js auth                      # one-time Google login
export NOTEBOOKLM_HTTP_TOKEN=$(openssl rand -hex 32)
node dist/index.js --transport http --port 3000
ngrok http 3000                              # public https URL
```

ChatGPT → Settings → Apps & Connectors → Advanced → turn on **Developer mode** → create a connector with URL `https://<ngrok-host>/mcp/<token>` and **No authentication** (the token in the URL is the password; make a new one if it leaks). Menu labels move between ChatGPT releases.

ChatGPT gives up on a tool after ~60 s: reuse `session_id` between questions and set `STEALTH_HUMAN_TYPING=false` to stay under it.

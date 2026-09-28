# AGENTS.md

Project rules for coding agents (Codex; Claude Code via `@AGENTS.md` in `CLAUDE.md`).

## Project

`notebooklm-mcp`: an MCP server that drives a real Chrome (Patchright) against Google NotebookLM (chat with citations, source ingestion, Audio Overviews, local notebook library). TypeScript, ESM, Node ≥ 18. Transports: stdio (default) and Streamable HTTP (`--transport http`).

## Commands

| Task | Command |
|---|---|
| Install (also builds via `prepare`) | `npm install` |
| Build (`tsc` → `dist/`) | `npm run build` |
| Lint | `npm run lint` |
| Format what you touched | `npx prettier --write <files>` |

- There is **no test suite**. `npm test` starts the server on stdio and blocks; it is not a check.
- `npm run check` fails at `format:check` on six files that predate current work. Do not mass-reformat unrelated files; format only what you change, then run `npm run lint && npm run build`. The lint warning in `src/transport/http.ts` about type-only imports is also pre-existing.
- Smoke test without a Google login (library and health tools need no browser). Use a temp `HOME` so the real profile and library stay untouched:
  ```bash
  T=$(mktemp -d); printf '%s\n' \
    '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"smoke","version":"0"}}}' \
    '{"jsonrpc":"2.0","method":"notifications/initialized"}' \
    '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' \
  | HOME=$T XDG_DATA_HOME=$T/data XDG_CONFIG_HOME=$T/config timeout 10 node dist/index.js 2>/dev/null
  ```

## Layout

- `src/index.ts`: CLI entry, per-session MCP `Server` factory, tool dispatch `switch`, transport selection
- `src/transport/http.ts`: Streamable-HTTP routing, sessions, token auth (`NOTEBOOKLM_HTTP_TOKEN`)
- `src/tools/definitions/*.ts`: tool schemas + annotations; `src/tools/handlers.ts`: implementations
- `src/notebooklm/selectors.ts`: the only place NotebookLM CSS/aria selectors live
- `src/auth/`, `src/session/`, `src/library/`, `src/utils/`: auth, browser sessions, `library.json`, settings/logging

## Rules

- **Never write to stdout** in server code: stdio mode carries JSON-RPC there. Log through `log.*` (`src/utils/logger.ts`, stderr). Only `src/utils/cli-handler.ts` may `console.log`.
- ESLint enforces: no `any`, `import type` for type-only imports, `===`.
- A new tool touches three places: schema in `src/tools/definitions/`, handler in `src/tools/handlers.ts`, `case` in the `switch` in `src/index.ts`. Add it to the `minimal`/`standard` lists in `src/utils/settings-manager.ts` if it belongs there. Keep MCP annotations honest: ChatGPT asks for confirmation on every tool without `readOnlyHint: true`.
- Over HTTP each MCP session needs its **own** SDK `Server` (`createMcpServer()`); sharing one across transports makes older sessions hang. Browser sessions, auth and the library are shared on purpose.
- ChatGPT times out tool calls at about 60 s. Long operations return immediately and expose a status tool (`generate_audio` → `get_audio_status`).
- The version string is duplicated: `package.json` plus three places in `src/index.ts`.
- Never commit `.env`, tokens, Chrome profiles, or `library.json`.

/**
 * Streamable-HTTP transport for the MCP server (issue #4).
 *
 * Hosts the MCP protocol over HTTP using the SDK's
 * `StreamableHTTPServerTransport`. Built on Node's stdlib `http` module so we
 * don't pull in Express just to forward requests. Two operations:
 *
 *   POST /mcp        — JSON-RPC requests/responses
 *   GET  /healthz    — liveness probe (200 OK with version)
 *
 * Multiple sessions are supported via the `Mcp-Session-Id` header — each
 * session keeps its own transport so concurrent clients don't tread on each
 * other. Session lifecycle is fully owned by the SDK; we just route.
 *
 * Optional shared-secret auth (`authToken`) for servers reachable from the
 * internet, e.g. through a tunnel for ChatGPT. The token is accepted either
 * as `Authorization: Bearer <token>` on `/mcp` (Codex, API clients) or as a
 * path segment, `/mcp/<token>`, for clients such as ChatGPT that can only be
 * given a URL.
 */

import {
  createServer,
  IncomingMessage,
  type Server as HttpServer,
  ServerResponse,
} from "node:http";
import { createHash, randomUUID, timingSafeEqual } from "node:crypto";
import type { Server as McpServer } from "@modelcontextprotocol/sdk/server/index.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { isInitializeRequest } from "@modelcontextprotocol/sdk/types.js";
import { log } from "../utils/logger.js";

export interface HttpTransportOptions {
  port: number;
  host?: string;
  /**
   * Shared secret required on every `/mcp` request when set. Must pass
   * `validateAuthToken`. Unset keeps the endpoint open (loopback use only).
   */
  authToken?: string;
  /** Connect callback invoked once per new session — wires the McpServer to the transport. */
  connect: (transport: StreamableHTTPServerTransport) => Promise<void>;
}

export interface HttpTransportHandle {
  server: HttpServer;
  close: () => Promise<void>;
}

const SESSION_HEADER = "mcp-session-id";
const MCP_PATH = "/mcp";

/**
 * The token doubles as a URL path segment, so it is restricted to RFC 3986
 * unreserved characters. The length floor keeps it out of brute-force range:
 * anyone holding it can drive the signed-in Google browser session.
 */
const AUTH_TOKEN_RE = /^[A-Za-z0-9._~-]{32,}$/;

export function validateAuthToken(token: string): void {
  if (!AUTH_TOKEN_RE.test(token)) {
    throw new Error(
      "NOTEBOOKLM_HTTP_TOKEN must be at least 32 characters of [A-Za-z0-9._~-]. " +
        "Generate one with: openssl rand -hex 32"
    );
  }
}

export async function startHttpTransport(opts: HttpTransportOptions): Promise<HttpTransportHandle> {
  if (opts.authToken !== undefined) validateAuthToken(opts.authToken);
  const transports = new Map<string, StreamableHTTPServerTransport>();

  const server = createServer((req, res) => {
    void handleRequest(req, res, transports, opts).catch((err) => {
      log.error(`❌ [HTTP] Unhandled request error: ${err}`);
      if (!res.headersSent) {
        res.writeHead(500, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: "internal server error" }));
      }
    });
  });

  await new Promise<void>((resolve, reject) => {
    server.once("error", reject);
    server.listen(opts.port, opts.host ?? "127.0.0.1", () => {
      server.off("error", reject);
      log.success(
        `🌐 HTTP transport listening on http://${opts.host ?? "127.0.0.1"}:${opts.port}/mcp`
      );
      if (opts.authToken) {
        log.info(
          "🔐 Token auth on: use https://<public-host>/mcp/<token> (ChatGPT) " +
            "or send `Authorization: Bearer <token>` to /mcp"
        );
      } else {
        log.warning(
          "⚠️  No NOTEBOOKLM_HTTP_TOKEN set — anyone who can reach this port can " +
            "use your Google session. Set one before exposing the server (tunnel, 0.0.0.0)."
        );
      }
      resolve();
    });
  });

  return {
    server,
    close: async () => {
      for (const t of transports.values()) {
        try {
          await t.close();
        } catch {
          /* ignore — best-effort shutdown */
        }
      }
      transports.clear();
      await new Promise<void>((resolve, reject) =>
        server.close((err) => (err ? reject(err) : resolve()))
      );
    },
  };
}

/**
 * Use the McpServer high-level Server class — it accepts any Transport.
 * Bridge helper kept for callers wiring an existing McpServer instance.
 */
export async function bindMcpServer(
  mcpServer: McpServer,
  transport: StreamableHTTPServerTransport
): Promise<void> {
  await mcpServer.connect(transport);
}

async function handleRequest(
  req: IncomingMessage,
  res: ServerResponse,
  transports: Map<string, StreamableHTTPServerTransport>,
  opts: HttpTransportOptions
): Promise<void> {
  const url = new URL(req.url ?? "/", `http://${req.headers.host ?? "localhost"}`);
  // Tolerate a pasted trailing slash (`/mcp/`).
  const pathname = url.pathname.length > 1 ? url.pathname.replace(/\/+$/, "") : url.pathname;

  if (pathname === "/healthz" && req.method === "GET") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ status: "ok", protocol: "mcp-streamable-http" }));
    return;
  }

  const access = checkAccess(pathname, req, opts.authToken);
  if (access === "not-found") {
    // Also covers a wrong path token, so the response is no oracle for it.
    res.writeHead(404, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ error: "not found", expected: "/mcp" }));
    return;
  }
  if (access === "unauthorized") {
    res.writeHead(401, {
      "Content-Type": "application/json",
      "WWW-Authenticate": 'Bearer realm="notebooklm-mcp"',
    });
    res.end(
      JSON.stringify({
        error: "unauthorized — send `Authorization: Bearer <token>` or use /mcp/<token>",
      })
    );
    return;
  }

  const sessionId = headerString(req.headers[SESSION_HEADER]);

  if (req.method === "GET" || req.method === "DELETE") {
    // SSE streams + session termination — both routed by session.
    const transport = sessionId ? transports.get(sessionId) : undefined;
    if (!transport) {
      res.writeHead(404, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ error: "unknown session" }));
      return;
    }
    await transport.handleRequest(req, res);
    return;
  }

  if (req.method !== "POST") {
    res.writeHead(405, { "Content-Type": "application/json", Allow: "POST, GET, DELETE" });
    res.end(JSON.stringify({ error: "method not allowed" }));
    return;
  }

  const body = await readJsonBody(req);

  // Re-use existing session, or initialise a new one when the client says so.
  let transport = sessionId ? transports.get(sessionId) : undefined;
  if (!transport && isInitializeRequest(body)) {
    transport = new StreamableHTTPServerTransport({
      sessionIdGenerator: () => randomUUID(),
      onsessioninitialized: (sid) => {
        transports.set(sid, transport!);
      },
    });
    transport.onclose = () => {
      if (transport!.sessionId) transports.delete(transport!.sessionId);
    };
    await opts.connect(transport);
  }

  if (!transport) {
    if (sessionId) {
      // Expired or pre-restart session. The spec mandates 404 here: it is the
      // signal for clients (ChatGPT included) to re-initialize on their own.
      res.writeHead(404, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ error: "unknown session — send `initialize` to start a new one" }));
      return;
    }
    res.writeHead(400, { "Content-Type": "application/json" });
    res.end(
      JSON.stringify({
        error: "no transport for request — pass an `Mcp-Session-Id` header or send `initialize`",
      })
    );
    return;
  }

  await transport.handleRequest(req, res, body);
}

type Access = "ok" | "unauthorized" | "not-found";

function checkAccess(pathname: string, req: IncomingMessage, token: string | undefined): Access {
  if (!token) return pathname === MCP_PATH ? "ok" : "not-found";

  if (pathname.startsWith(`${MCP_PATH}/`)) {
    return secretEquals(pathname.slice(MCP_PATH.length + 1), token) ? "ok" : "not-found";
  }
  if (pathname !== MCP_PATH) return "not-found";

  const presented = headerString(req.headers.authorization)?.match(/^Bearer\s+(\S+)\s*$/i)?.[1];
  return presented !== undefined && secretEquals(presented, token) ? "ok" : "unauthorized";
}

/** Constant-time comparison; hashing first hides the token length too. */
function secretEquals(presented: string, expected: string): boolean {
  const a = createHash("sha256").update(presented).digest();
  const b = createHash("sha256").update(expected).digest();
  return timingSafeEqual(a, b);
}

async function readJsonBody(req: IncomingMessage): Promise<unknown> {
  const chunks: Buffer[] = [];
  for await (const chunk of req) {
    chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
  }
  if (chunks.length === 0) return undefined;
  const raw = Buffer.concat(chunks).toString("utf8");
  if (!raw.trim()) return undefined;
  try {
    return JSON.parse(raw);
  } catch {
    throw new Error("Invalid JSON request body");
  }
}

function headerString(value: string | string[] | undefined): string | undefined {
  if (Array.isArray(value)) return value[0];
  return value;
}

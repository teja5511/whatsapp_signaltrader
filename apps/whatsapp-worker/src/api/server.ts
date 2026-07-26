import http from "http";
import { URL } from "url";
import { WorkerConfig } from "../config/schema";
import { globalWorkerState } from "../state/worker-state";
import { verifyLocalApiToken } from "./auth";
import { WHATSAPP_WORKER_VERSION, OPENWA_ADAPTER_VERSION, RESET_CONFIRMATION_PHRASE, ConnectionState, QrState } from "../constants";
import { OpenWAAdapterInterface } from "../openwa/adapter";
import { FileSpool } from "../openwa/spool";
import { QuarantineManager } from "../openwa/quarantine";
import { SessionManager } from "../openwa/session";
import { saveLocalConfig } from "../config/loader";
import { globalEventBus, WorkerEvent } from "../state/event-bus";

export function createWorkerApiServer(
  config: WorkerConfig,
  adapter: OpenWAAdapterInterface,
  spool: FileSpool,
  quarantineMgr: QuarantineManager,
  sessionMgr: SessionManager
): http.Server {
  const server = http.createServer(async (req, res) => {
    const parsedUrl = new URL(req.url || "/", `http://${req.headers.host || "127.0.0.1"}`);
    const pathname = parsedUrl.pathname;
    const method = (req.method || "GET").toUpperCase();

    // Helper for sending JSON
    const sendJson = (statusCode: number, data: any) => {
      res.writeHead(statusCode, { "Content-Type": "application/json" });
      res.end(JSON.stringify(data));
    };

    // Require local auth helper
    const requireAuth = (): boolean => {
      if (!verifyLocalApiToken(req, config.localApiToken)) {
        sendJson(401, { error: "Unauthorized local API token.", code: "UNAUTHORIZED_LOCAL_API" });
        return false;
      }
      return true;
    };

    // Helper for parsing JSON body
    const parseBody = (): Promise<any> => {
      return new Promise((resolve) => {
        let body = "";
        req.on("data", chunk => { body += chunk; });
        req.on("end", () => {
          try {
            resolve(body ? JSON.parse(body) : {});
          } catch {
            resolve({});
          }
        });
      });
    };

    try {
      // Unauthenticated Endpoints
      if (method === "GET" && pathname === "/health") {
        const counts = spool.getSpoolCounts();
        return sendJson(200, {
          service: "whatsapp-worker",
          status: "ok",
          worker_version: WHATSAPP_WORKER_VERSION,
          adapter_mode: adapter.mode,
          connection_state: globalWorkerState.connectionState,
          session_authenticated: globalWorkerState.sessionAuthenticated,
          approved_group_configured: !!globalWorkerState.approvedGroupId,
          approved_admin_configured: !!globalWorkerState.approvedAdminId,
          admin_role_verified: globalWorkerState.adminRoleVerified,
          trading_service_reachable: globalWorkerState.tradingServiceReachable,
          spool_pending: counts.pending,
          spool_quarantined: counts.quarantined,
          whatsapp_integration_enabled: adapter.mode === "real" && globalWorkerState.connectionState === ConnectionState.READY
        });
      }

      if (method === "GET" && pathname === "/ready") {
        const isReady = globalWorkerState.isReady();
        return sendJson(isReady ? 200 : 503, {
          ready: isReady,
          connection_state: globalWorkerState.connectionState,
          process_lock_owned: globalWorkerState.processLockOwned
        });
      }

      if (method === "GET" && pathname === "/version") {
        return sendJson(200, {
          worker_version: WHATSAPP_WORKER_VERSION,
          openwa_adapter_version: OPENWA_ADAPTER_VERSION,
          adapter_mode: adapter.mode
        });
      }

      if (method === "GET" && pathname === "/groups") {
        const groups = await adapter.listGroups();
        return sendJson(200, groups);
      }

      if (method === "POST" && pathname === "/groups/resolve-link") {
        const body = await parseBody();
        if (!body.invite_link) return sendJson(422, { error: "invite_link is required." });
        if (!adapter.getGroupFromInviteLink) return sendJson(400, { error: "Invite link resolution not supported in current mode." });
        const summary = await adapter.getGroupFromInviteLink(body.invite_link);
        if (!summary) return sendJson(404, { error: "Failed to resolve WhatsApp group from invite link." });
        return sendJson(200, summary);
      }

      if (method === "GET" && pathname === "/configuration") {
        return sendJson(200, {
          adapter_mode: config.adapterMode,
          approved_group_id: globalWorkerState.approvedGroupId,
          approved_admin_id: globalWorkerState.approvedAdminId,
          require_admin_role: config.requireAdminRole,
          trading_service_url: config.tradingServiceUrl
        });
      }

      // Authenticated Read & Mutating Endpoints
      if (!requireAuth()) return;

      if (method === "GET" && pathname === "/status") {
        return sendJson(200, {
          connection_state: globalWorkerState.connectionState,
          qr_state: globalWorkerState.qrState,
          session_authenticated: globalWorkerState.sessionAuthenticated,
          approved_group_id: globalWorkerState.approvedGroupId,
          approved_admin_id: globalWorkerState.approvedAdminId,
          admin_role_verified: globalWorkerState.adminRoleVerified,
          spool_counts: spool.getSpoolCounts()
        });
      }

      if (method === "GET" && pathname === "/metrics") {
        return sendJson(200, {
          ...globalWorkerState.metrics,
          spool_counts: spool.getSpoolCounts()
        });
      }

      if (method === "GET" && pathname === "/configuration") {
        return sendJson(200, {
          adapter_mode: config.adapterMode,
          approved_group_id: globalWorkerState.approvedGroupId,
          approved_admin_id: globalWorkerState.approvedAdminId,
          require_admin_role: config.requireAdminRole,
          trading_service_url: config.tradingServiceUrl
        });
      }

      if (method === "GET" && pathname === "/session") {
        return sendJson(200, {
          session_name: config.sessionName,
          session_authenticated: globalWorkerState.sessionAuthenticated,
          connection_state: globalWorkerState.connectionState
        });
      }

      if (method === "GET" && pathname === "/session/qr") {
        if (!config.qrExposeOverLocalApi) {
          return sendJson(403, { error: "QR API exposition disabled by configuration." });
        }
        return sendJson(200, {
          qr_state: globalWorkerState.qrState,
          qr_payload: globalWorkerState.qrPayload,
          qr_expires_at: globalWorkerState.qrExpiresAt
        });
      }

      if (method === "GET" && pathname === "/groups") {
        const groups = await adapter.listGroups();
        return sendJson(200, groups);
      }

      if (method === "GET" && pathname.startsWith("/groups/") && pathname.endsWith("/admins")) {
        const groupId = pathname.split("/")[2];
        const admins = await adapter.getGroupAdmins(groupId);
        return sendJson(200, admins);
      }

      if (method === "GET" && pathname === "/spool") {
        return sendJson(200, spool.getSpoolCounts());
      }

      if (method === "GET" && pathname === "/quarantine") {
        const items = quarantineMgr.listQuarantinedItems();
        return sendJson(200, items);
      }

      if (method === "GET" && pathname === "/events") {
        res.writeHead(200, {
          "Content-Type": "text/event-stream",
          "Cache-Control": "no-cache",
          "Connection": "keep-alive"
        });
        const listener = (event: WorkerEvent) => {
          res.write(`data: ${JSON.stringify(event)}\n\n`);
        };
        globalEventBus.on("event", listener);
        req.on("close", () => {
          globalEventBus.removeListener("event", listener);
        });
        return;
      }

      // Mutating Endpoints
      if (method === "POST" && pathname === "/start") {
        await adapter.initialize();
        globalWorkerState.sessionAuthenticated = true;
        globalWorkerState.setConnectionState(ConnectionState.READY);
        return sendJson(200, { status: "started", connection_state: globalWorkerState.connectionState });
      }

      if (method === "POST" && pathname === "/stop") {
        await adapter.shutdown();
        globalWorkerState.setConnectionState(ConnectionState.STOPPED);
        return sendJson(200, { status: "stopped", connection_state: globalWorkerState.connectionState });
      }

      if (method === "POST" && pathname === "/session/logout") {
        await adapter.logout();
        globalWorkerState.sessionAuthenticated = false;
        globalWorkerState.setConnectionState(ConnectionState.LOGGED_OUT);
        return sendJson(200, { status: "logged_out" });
      }

      if (method === "POST" && pathname === "/session/reset") {
        const body = await parseBody();
        if (body.confirmation_phrase !== RESET_CONFIRMATION_PHRASE) {
          return sendJson(422, { error: "Invalid confirmation phrase.", code: "INVALID_RESET_CONFIRMATION" });
        }
        await adapter.shutdown();
        sessionMgr.resetSession(RESET_CONFIRMATION_PHRASE, config.dataDir || "./data");
        globalWorkerState.sessionAuthenticated = false;
        globalWorkerState.setConnectionState(ConnectionState.LOGGED_OUT);
        return sendJson(200, { status: "session_reset_complete" });
      }

      if (method === "POST" && pathname === "/configuration/group") {
        const body = await parseBody();
        if (!body.approved_group_id) {
          return sendJson(422, { error: "approved_group_id is required." });
        }
        globalWorkerState.approvedGroupId = body.approved_group_id;
        globalWorkerState.approvedGroupDisplayName = body.approved_group_display_name || body.approved_group_id;
        saveLocalConfig({
          approved_group_id: globalWorkerState.approvedGroupId || undefined,
          approved_group_display_name: globalWorkerState.approvedGroupDisplayName || undefined,
          approved_admin_id: globalWorkerState.approvedAdminId || undefined,
          approved_admin_display_name: globalWorkerState.approvedAdminDisplayName || undefined,
          selected_at: new Date().toISOString()
        }, config.dataDir);
        return sendJson(200, { status: "group_configured", approved_group_id: globalWorkerState.approvedGroupId });
      }

      if (method === "POST" && pathname === "/configuration/admin") {
        const body = await parseBody();
        if (!body.approved_admin_id) {
          return sendJson(422, { error: "approved_admin_id is required." });
        }
        globalWorkerState.approvedAdminId = body.approved_admin_id;
        globalWorkerState.approvedAdminDisplayName = body.approved_admin_display_name || body.approved_admin_id;
        saveLocalConfig({
          approved_group_id: globalWorkerState.approvedGroupId || undefined,
          approved_group_display_name: globalWorkerState.approvedGroupDisplayName || undefined,
          approved_admin_id: globalWorkerState.approvedAdminId || undefined,
          approved_admin_display_name: globalWorkerState.approvedAdminDisplayName || undefined,
          selected_at: new Date().toISOString()
        }, config.dataDir);
        return sendJson(200, { status: "admin_configured", approved_admin_id: globalWorkerState.approvedAdminId });
      }

      if (method === "POST" && pathname.startsWith("/quarantine/") && pathname.endsWith("/requeue")) {
        const itemId = pathname.split("/")[2];
        const ok = quarantineMgr.requeueQuarantinedItem(itemId);
        if (!ok) return sendJson(404, { error: "Quarantined item not found or failed to requeue." });
        return sendJson(200, { status: "requeued", item_id: itemId });
      }

      return sendJson(404, { error: "Endpoint not found." });
    } catch (err: any) {
      return sendJson(500, { error: err.message || "Internal worker server error." });
    }
  });

  return server;
}

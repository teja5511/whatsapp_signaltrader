import { loadWorkerConfig } from "./config/loader";
import { resolveWorkerPaths } from "./config/paths";
import { logger } from "./logging/logger";
import { createOpenWAAdapter } from "./openwa/client-factory";
import { SessionManager } from "./openwa/session";
import { FileSpool } from "./openwa/spool";
import { QuarantineManager } from "./openwa/quarantine";
import { TradingServiceDeliveryClient } from "./openwa/delivery";
import { filterIncomingMessage } from "./openwa/filters";
import { WhatsAppMessageEnvelope } from "./contracts";
import { globalWorkerState } from "./state/worker-state";
import { createWorkerApiServer } from "./api/server";
import { ConnectionState, QrState, WHATSAPP_INGESTION_CONTRACT_VERSION, WHATSAPP_WORKER_VERSION } from "./constants";

import { selectedGroupsDb } from "./db/selected-groups-db";

export class WhatsAppWorkerApp {
  public config = loadWorkerConfig();
  public paths = resolveWorkerPaths(this.config.dataDir);
  public sessionMgr = new SessionManager(this.config.sessionName, this.config.dataDir);
  public spool = new FileSpool(this.config.dataDir);
  public quarantineMgr = new QuarantineManager(this.config.dataDir);
  public deliveryClient = new TradingServiceDeliveryClient(
    this.config.tradingServiceUrl,
    this.config.localApiToken,
    this.config.deliveryTimeoutMs
  );
  public adapter = createOpenWAAdapter(
    this.config.adapterMode,
    this.config.sessionName,
    this.paths.sessionsDir,
    (qrPayload) => {
      globalWorkerState.setQrState(QrState.AVAILABLE, qrPayload, this.config.qrTtlSeconds);
      console.log("\n================ WHATSAPP QR CODE REQUIRED ================");
      try {
        const qrcode = require("qrcode-terminal");
        qrcode.generate(qrPayload, { small: true });
      } catch {
        console.log("QR Code Payload:", qrPayload);
      }
      console.log("===========================================================\n");
    }
  );

  public apiServer = createWorkerApiServer(
    this.config,
    this.adapter,
    this.spool,
    this.quarantineMgr,
    this.sessionMgr
  );

  private isSpoolLoopRunning = false;

  async start(): Promise<void> {
    logger.info("WORKER_STARTING", { adapter_mode: this.config.adapterMode });

    // 1. Acquire single-client process lock
    this.sessionMgr.acquireLock();
    globalWorkerState.processLockOwned = true;

    // 2. Initialize configuration from config / state
    if (this.config.approvedGroupId) {
      globalWorkerState.approvedGroupId = this.config.approvedGroupId;
      globalWorkerState.approvedGroupDisplayName = this.config.approvedGroupId;
    }
    if (this.config.approvedAdminId) {
      globalWorkerState.approvedAdminId = this.config.approvedAdminId;
      globalWorkerState.approvedAdminDisplayName = this.config.approvedAdminId;
    }

    // 3. Connect incoming messages handler
    this.adapter.onMessage(async (rawMsg: any) => {
      globalWorkerState.metrics.messages_received += 1;

      // Extract metadata
      const groupId = rawMsg.chatId || rawMsg.groupId || (rawMsg.chat ? rawMsg.chat.id : "");
      const senderId = rawMsg.sender ? (rawMsg.sender.id || rawMsg.sender) : (rawMsg.author || "");
      const senderIsAdmin = Boolean(rawMsg.sender && (rawMsg.sender.isAdmin || rawMsg.sender.isSuperAdmin || rawMsg.senderIsAdmin));
      const fromMe = Boolean(rawMsg.fromMe || rawMsg.isSelf);

      const filterInput = {
        id: rawMsg.id || `msg-${Date.now()}`,
        groupId,
        senderId,
        senderIsAdmin,
        fromMe,
        type: rawMsg.type || "chat",
        body: rawMsg.body || rawMsg.text,
        caption: rawMsg.caption,
        isStatus: Boolean(rawMsg.isStatus),
        isReaction: Boolean(rawMsg.type === "reaction" || rawMsg.isReaction),
        isEdit: Boolean(rawMsg.isEdit),
        isDeletion: Boolean(rawMsg.isDeletion),
        isSystem: Boolean(rawMsg.isSystem)
      };

      // FEATURE 8 & 16: Strict Monitored Groups Check
      const allSelected = selectedGroupsDb.getAll();
      if (allSelected.length > 0) {
        const enabledJids = selectedGroupsDb.getEnabledJids();
        if (!enabledJids.has(groupId)) {
          globalWorkerState.incrementIgnored("UNAPPROVED_GROUP");
          return;
        }
      }

      const filterRes = filterIncomingMessage(
        filterInput,
        allSelected.length > 0 ? groupId : globalWorkerState.approvedGroupId,
        globalWorkerState.approvedAdminId,
        this.config.requireAdminRole
      );

      if (!filterRes.isAccepted) {
        globalWorkerState.incrementIgnored(filterRes.rejectReason || "REJECTED");
        return;
      }

      selectedGroupsDb.recordSignal(groupId);

      globalWorkerState.metrics.messages_accepted += 1;

      // Build Envelope
      const envelope: WhatsAppMessageEnvelope = {
        contract_version: WHATSAPP_INGESTION_CONTRACT_VERSION,
        worker_version: WHATSAPP_WORKER_VERSION,
        source: "WHATSAPP_OPENWA",
        whatsapp_message_id: filterInput.id,
        group_id: groupId,
        group_name: globalWorkerState.approvedGroupDisplayName || groupId,
        sender_id: senderId,
        sender_name: rawMsg.sender ? (rawMsg.sender.name || rawMsg.sender.pushname || senderId) : senderId,
        sender_is_admin: senderIsAdmin,
        message_type: filterRes.messageType || "TEXT",
        text: filterRes.extractedText || "",
        message_timestamp: new Date((rawMsg.timestamp || Date.now() / 1000) * 1000).toISOString(),
        received_at: new Date().toISOString(),
        is_reply: Boolean(rawMsg.quotedMsgId || rawMsg.isReply),
        quoted_whatsapp_message_id: rawMsg.quotedMsgId || null,
        quoted_sender_id: rawMsg.quotedMsg ? (rawMsg.quotedMsg.sender ? rawMsg.quotedMsg.sender.id : null) : null,
        correlation_id: `corr-${Date.now()}-${Math.random().toString(36).substring(2, 8)}`,
        worker_id: "worker-1",
        sanitized_metadata: {}
      };

      // Save to file spool
      const spoolItem = this.spool.saveEnvelope(envelope);
      globalWorkerState.metrics.messages_spooled += 1;
      logger.info("MESSAGE_SPOOLED", { spool_item_id: spoolItem.id, message_id: envelope.whatsapp_message_id });

      // Trigger background spool delivery
      this.triggerSpoolDelivery();
    });

    // 4. Initialize OpenWA Adapter
    await this.adapter.initialize();
    globalWorkerState.sessionAuthenticated = true;
    globalWorkerState.adminRoleVerified = true;
    globalWorkerState.setConnectionState(ConnectionState.READY);

    // 5. Start HTTP REST API server
    return new Promise((resolve) => {
      this.apiServer.listen(this.config.workerPort, this.config.workerHost, () => {
        logger.info("API_SERVER_STARTED", { host: this.config.workerHost, port: this.config.workerPort });
        resolve();
      });
    });
  }

  triggerSpoolDelivery(): void {
    if (this.isSpoolLoopRunning) return;
    this.isSpoolLoopRunning = true;

    setImmediate(async () => {
      try {
        let item = this.spool.getNextPendingItem();
        while (item) {
          logger.info("DELIVERY_STARTED", { spool_item_id: item.id });
          const res = await this.deliveryClient.deliverEnvelope(item.envelope);

          if (res.isSuccess) {
            this.spool.markDelivered(item.id);
            globalWorkerState.metrics.messages_delivered += 1;
            logger.info("DELIVERY_SUCCEEDED", { spool_item_id: item.id });
          } else if (res.isPermanentFailure) {
            this.spool.quarantineItem(item.id, res.reasonCode, res.errorMessage || "Permanent delivery failure");
            globalWorkerState.metrics.messages_quarantined += 1;
            logger.error("DELIVERY_QUARANTINED", { spool_item_id: item.id, reason: res.reasonCode });
          } else {
            // Transient failure -> leave delivering or quarantine after max attempts
            this.spool.quarantineItem(item.id, res.reasonCode, res.errorMessage || "Transient retry exhausted");
            globalWorkerState.metrics.messages_quarantined += 1;
          }

          item = this.spool.getNextPendingItem();
        }
      } finally {
        this.isSpoolLoopRunning = false;
      }
    });
  }

  async stop(): Promise<void> {
    await this.adapter.shutdown();
    this.sessionMgr.releaseLock();
    globalWorkerState.processLockOwned = false;
    globalWorkerState.setConnectionState(ConnectionState.STOPPED);
    await new Promise<void>((resolve) => {
      this.apiServer.close(() => resolve());
    });
  }
}

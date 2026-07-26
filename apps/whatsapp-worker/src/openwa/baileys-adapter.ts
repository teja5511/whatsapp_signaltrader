import { OpenWAAdapterInterface } from "./adapter";
import { GroupSummary, GroupAdminSummary } from "../contracts";
import { ConnectionState, QrState } from "../constants";

export class BaileysOpenWAAdapter implements OpenWAAdapterInterface {
  public readonly mode = "real";
  public connectionState: ConnectionState = ConnectionState.STOPPED;
  public qrState: QrState = QrState.NOT_REQUIRED;

  private sock: any = null;
  private messageCallback: ((msg: any) => void) | null = null;

  constructor(
    private sessionName: string = "xauusd-bot",
    private sessionDir?: string,
    private qrCallback?: (qrPayload: string) => void
  ) {}

  async initialize(): Promise<boolean> {
    try {
      this.connectionState = ConnectionState.STARTING;
      console.log("[WhatsApp Worker] Initializing Baileys Direct Connection (No Chrome browser required)...");

      let baileys: any;
      let qrcode: any;
      try {
        baileys = require("@whiskeysockets/baileys");
        qrcode = require("qrcode-terminal");
      } catch (err) {
        console.error("[Baileys Import Error]", err);
        this.connectionState = ConnectionState.ERROR;
        return false;
      }

      const makeWASocket = baileys.default || baileys.makeWASocket || baileys;
      const { useMultiFileAuthState, fetchLatestBaileysVersion } = baileys;

      const authPath = this.sessionDir || `./data/sessions/${this.sessionName}_baileys`;
      const { state, saveCreds } = await useMultiFileAuthState(authPath);
      const { version } = await fetchLatestBaileysVersion().catch(() => ({ version: [2, 3000, 1015901307] }));

      // Disable verbose pino logging
      const logger = require("pino")({ level: "silent" });

      this.sock = makeWASocket({
        version,
        auth: state,
        printQRInTerminal: false,
        logger,
        browser: ["WhatsApp Trade Bot", "Chrome", "132.0.0.0"]
      });

      this.sock.ev.on("creds.update", saveCreds);

      this.sock.ev.on("connection.update", (update: any) => {
        const { connection, lastDisconnect, qr } = update;

        if (qr) {
          this.qrState = QrState.AVAILABLE;
          console.log("\n=================== SCAN WHATSAPP QR CODE ===================");
          qrcode.generate(qr, { small: true });
          console.log("=============================================================\n");
          if (this.qrCallback) this.qrCallback(qr);
        }

        if (connection === "open") {
          this.connectionState = ConnectionState.READY;
          this.qrState = QrState.AUTHENTICATED;
          console.log("\n✅ [WhatsApp Worker] Connected to WhatsApp Web successfully!");
        } else if (connection === "close") {
          const statusCode = (lastDisconnect?.error as any)?.output?.statusCode;
          const DisconnectReason = baileys.DisconnectReason;
          const shouldReconnect = statusCode !== DisconnectReason?.loggedOut;
          this.connectionState = ConnectionState.ERROR;
          if (shouldReconnect) {
            console.log("[WhatsApp Worker] Connection closed, reconnecting...");
            setTimeout(() => this.initialize(), 3000);
          }
        }
      });

      this.sock.ev.on("messages.upsert", (m: any) => {
        if (!this.messageCallback || !m.messages || m.messages.length === 0) return;
        for (const rawMsg of m.messages) {
          if (rawMsg.key.fromMe) continue;
          
          const text = rawMsg.message?.conversation ||
                       rawMsg.message?.extendedTextMessage?.text ||
                       rawMsg.message?.imageMessage?.caption ||
                       "";

          const normalizedMsg = {
            id: rawMsg.key.id,
            chatId: rawMsg.key.remoteJid,
            groupId: rawMsg.key.remoteJid,
            sender: {
              id: rawMsg.key.participant || rawMsg.key.remoteJid,
              isAdmin: false
            },
            fromMe: Boolean(rawMsg.key.fromMe),
            type: "chat",
            body: text,
            text,
            timestamp: rawMsg.messageTimestamp
          };

          this.messageCallback(normalizedMsg);
        }
      });

      return true;
    } catch (err: any) {
      console.error("[Baileys Adapter Error]", err);
      this.connectionState = ConnectionState.ERROR;
      return false;
    }
  }

  async shutdown(): Promise<void> {
    if (this.sock) {
      try {
        this.sock.end(undefined);
      } catch {}
    }
    this.connectionState = ConnectionState.STOPPED;
  }

  async listGroups(): Promise<GroupSummary[]> {
    if (!this.sock) return [];
    try {
      const chats = await this.sock.groupFetchAllParticipating();
      return Object.values(chats).map((c: any) => ({
        group_id: c.id,
        display_name: c.subject || "Group",
        participant_count: c.participants?.length || 0,
        is_read_only: Boolean(c.announce),
        is_community: Boolean(c.isCommunity),
        is_announcement: Boolean(c.announce),
        is_archived: false
      }));
    } catch {
      return [];
    }
  }

  async getGroupAdmins(groupId: string): Promise<GroupAdminSummary[]> {
    if (!this.sock) return [];
    try {
      const metadata = await this.sock.groupMetadata(groupId);
      const admins = metadata.participants.filter((p: any) => p.admin === "admin" || p.admin === "superadmin");
      return admins.map((a: any) => ({
        admin_id: a.id,
        display_name: a.id,
        is_admin: true,
        is_super_admin: a.admin === "superadmin",
        is_group_member: true
      }));
    } catch {
      return [];
    }
  }

  onMessage(callback: (msg: any) => void): void {
    this.messageCallback = callback;
  }

  async logout(): Promise<void> {
    if (this.sock) {
      try {
        await this.sock.logout();
      } catch {}
    }
    this.connectionState = ConnectionState.LOGGED_OUT;
  }
}

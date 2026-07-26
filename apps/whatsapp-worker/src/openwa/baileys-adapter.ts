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

  private knownGroups = new Map<string, GroupSummary>();

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

      // Disable verbose pino logging with silent fallback logger
      let logger: any;
      try {
        logger = require("pino")({ level: "silent" });
      } catch {
        const dummyFn = () => {};
        logger = {
          level: "silent",
          child: () => logger,
          trace: dummyFn,
          debug: dummyFn,
          info: dummyFn,
          warn: dummyFn,
          error: dummyFn,
          fatal: dummyFn
        };
      }

      this.sock = makeWASocket({
        version,
        auth: state,
        printQRInTerminal: false,
        logger,
        browser: ["WhatsApp Trade Bot", "Chrome", "132.0.0.0"]
      });

      this.sock.ev.on("creds.update", saveCreds);

      this.sock.ev.on("connection.update", async (update: any) => {
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
          
          // Eagerly pre-fetch groups on connection
          try {
            const chats = await this.sock.groupFetchAllParticipating();
            for (const [id, c] of Object.entries(chats as Record<string, any>)) {
              this.knownGroups.set(id, {
                group_id: id,
                display_name: c.subject || c.name || "WhatsApp Group",
                participant_count: c.participants?.length || 0,
                is_read_only: Boolean(c.announce),
                is_community: Boolean(c.isCommunity),
                is_announcement: Boolean(c.announce),
                is_archived: false
              });
            }
            console.log(`[WhatsApp Worker] Pre-loaded ${this.knownGroups.size} participating groups.`);
          } catch {}
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

      // Track group events
      this.sock.ev.on("groups.update", (updates: any[]) => {
        for (const u of updates) {
          if (u.id) {
            const existing = this.knownGroups.get(u.id);
            this.knownGroups.set(u.id, {
              group_id: u.id,
              display_name: u.subject || existing?.display_name || "WhatsApp Group",
              participant_count: existing?.participant_count || 0,
              is_read_only: u.announce !== undefined ? Boolean(u.announce) : (existing?.is_read_only || false),
              is_community: existing?.is_community || false,
              is_announcement: u.announce !== undefined ? Boolean(u.announce) : (existing?.is_announcement || false),
              is_archived: false
            });
          }
        }
      });

      this.sock.ev.on("messages.upsert", (m: any) => {
        if (!m.messages || m.messages.length === 0) return;
        for (const rawMsg of m.messages) {
          const jid = rawMsg.key?.remoteJid;
          if (jid && jid.endsWith("@g.us") && !this.knownGroups.has(jid)) {
            this.knownGroups.set(jid, {
              group_id: jid,
              display_name: rawMsg.pushName ? `Group (${rawMsg.pushName})` : "WhatsApp Group",
              participant_count: 0,
              is_read_only: false,
              is_community: false,
              is_announcement: false,
              is_archived: false
            });
          }

          if (rawMsg.key.fromMe || !this.messageCallback) continue;

          const text = rawMsg.message?.conversation ||
                       rawMsg.message?.extendedTextMessage?.text ||
                       rawMsg.message?.imageMessage?.caption ||
                       "";

          const normalizedMsg = {
            id: rawMsg.key.id,
            chatId: jid,
            groupId: jid,
            sender: {
              id: rawMsg.key.participant || jid,
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
    if (this.sock) {
      try {
        const chats = await this.sock.groupFetchAllParticipating();
        for (const [id, c] of Object.entries(chats as Record<string, any>)) {
          this.knownGroups.set(id, {
            group_id: id,
            display_name: c.subject || c.name || "WhatsApp Group",
            participant_count: c.participants?.length || 0,
            is_read_only: Boolean(c.announce),
            is_community: Boolean(c.isCommunity),
            is_announcement: Boolean(c.announce),
            is_archived: false
          });
        }
      } catch (err) {
        console.log("[Baileys listGroups fallback to knownGroups cache]");
      }
    }
    return Array.from(this.knownGroups.values());
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

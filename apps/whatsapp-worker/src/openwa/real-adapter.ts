import { OpenWAAdapterInterface } from "./adapter";
import { GroupSummary, GroupAdminSummary } from "../contracts";
import { ConnectionState, QrState } from "../constants";

export class RealOpenWAAdapter implements OpenWAAdapterInterface {
  public readonly mode = "real";
  public connectionState: ConnectionState = ConnectionState.STOPPED;
  public qrState: QrState = QrState.NOT_REQUIRED;

  private client: any = null;
  private messageCallback: ((msg: any) => void) | null = null;

  constructor(
    private sessionName: string = "xauusd-bot",
    private sessionDir?: string,
    private qrCallback?: (qrPayload: string) => void
  ) {}

  async initialize(): Promise<boolean> {
    try {
      this.connectionState = ConnectionState.STARTING;
      console.log("[WhatsApp Worker] Initializing Real WhatsApp Web Connection...");
      let wa: any;
      try {
        wa = require("@open-wa/wa-automate");
      } catch {
        this.connectionState = ConnectionState.ERROR;
        console.error("\n❌ [@open-wa/wa-automate is not installed]");
        console.error("To use real WhatsApp web automation with QR code, run:\n");
        console.error("  pnpm --filter @whatsapp-bot/whatsapp-worker add @open-wa/wa-automate qrcode-terminal\n");
        console.error("Otherwise, keep WHATSAPP_ADAPTER_MODE=fake for simulation mode.\n");
        return false;
      }

      this.connectionState = ConnectionState.WAITING_FOR_QR;
      console.log("[WhatsApp Worker] Creating WA Automate client session...");
      this.client = await wa.create({
        sessionId: this.sessionName,
        multiDevice: true,
        useChrome: true,
        headless: false,
        popup: true,
        qrTimeout: 120,
        qrRefreshS: 15,
        qrLogSkip: false,
        authTimeout: 120,
        blockCrashLogs: true,
        disableSpins: true,
        killProcessOnBrowserClose: false,
        userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        chromiumArgs: [
          "--no-sandbox",
          "--disable-setuid-sandbox",
          "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
        ],
        sessionDataPath: this.sessionDir,
        qrCallback: (base64Qr: string, asciiQR: string) => {
          this.qrState = QrState.AVAILABLE;
          console.log("\n=================== SCAN WHATSAPP QR CODE ===================");
          if (asciiQR) {
            console.log(asciiQR);
          } else {
            try {
              const qrcode = require("qrcode-terminal");
              qrcode.generate(base64Qr, { small: true });
            } catch {
              console.log("QR String:", base64Qr);
            }
          }
          console.log("=============================================================\n");
          if (this.qrCallback) this.qrCallback(base64Qr);
        }
      });

      this.connectionState = ConnectionState.CONNECTED;
      this.qrState = QrState.AUTHENTICATED;

      if (this.client && this.messageCallback) {
        this.client.onAnyMessage((msg: any) => {
          if (this.messageCallback) this.messageCallback(msg);
        });
      }

      this.connectionState = ConnectionState.READY;
      return true;
    } catch (err: any) {
      this.connectionState = ConnectionState.ERROR;
      this.qrState = QrState.FAILED;
      return false;
    }
  }

  async shutdown(): Promise<void> {
    if (this.client) {
      try {
        await this.client.kill();
      } catch {}
    }
    this.connectionState = ConnectionState.STOPPED;
  }

  async listGroups(): Promise<GroupSummary[]> {
    if (!this.client) return [];
    try {
      const chats = await this.client.getAllGroups();
      return chats.map((c: any) => ({
        group_id: c.id._serialized || c.id,
        display_name: c.formattedTitle || c.name || "Group",
        participant_count: c.groupMetadata?.participants?.length || 0,
        is_read_only: Boolean(c.isReadOnly),
        is_community: Boolean(c.isParentGroup),
        is_announcement: Boolean(c.isAnnounceGrpServ),
        is_archived: Boolean(c.archive)
      }));
    } catch {
      return [];
    }
  }

  async getGroupAdmins(groupId: string): Promise<GroupAdminSummary[]> {
    if (!this.client) return [];
    try {
      const members = await this.client.getGroupAdmins(groupId);
      return members.map((m: any) => {
        const idStr = typeof m === "string" ? m : m._serialized || m.id;
        return {
          admin_id: idStr,
          display_name: idStr,
          is_admin: true,
          is_super_admin: false,
          is_group_member: true
        };
      });
    } catch {
      return [];
    }
  }

  onMessage(callback: (msg: any) => void): void {
    this.messageCallback = callback;
    if (this.client) {
      this.client.onAnyMessage((msg: any) => callback(msg));
    }
  }

  async logout(): Promise<void> {
    if (this.client) {
      try {
        await this.client.logout();
      } catch {}
    }
    this.connectionState = ConnectionState.LOGGED_OUT;
  }
}

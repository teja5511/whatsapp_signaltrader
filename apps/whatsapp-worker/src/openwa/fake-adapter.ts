import { OpenWAAdapterInterface } from "./adapter";
import { GroupSummary, GroupAdminSummary } from "../contracts";
import { ConnectionState, QrState } from "../constants";

export class FakeOpenWAAdapter implements OpenWAAdapterInterface {
  public readonly mode = "fake";
  public connectionState: ConnectionState = ConnectionState.STOPPED;
  public qrState: QrState = QrState.NOT_REQUIRED;

  private messageCallback: ((msg: any) => void) | null = null;

  public mockGroups: GroupSummary[] = [
    {
      group_id: "group-xauusd-vip",
      display_name: "XAUUSD Trading VIP Signals",
      participant_count: 25,
      is_read_only: false,
      is_community: false,
      is_announcement: false,
      is_archived: false
    },
    {
      group_id: "group-forex-chat",
      display_name: "Forex Discussion Group",
      participant_count: 150,
      is_read_only: false,
      is_community: false,
      is_announcement: false,
      is_archived: false
    }
  ];

  public mockAdmins: Record<string, GroupAdminSummary[]> = {
    "group-xauusd-vip": [
      {
        admin_id: "admin-master-1",
        display_name: "Master Trader Admin",
        is_admin: true,
        is_super_admin: true,
        is_group_member: true
      },
      {
        admin_id: "admin-secondary-2",
        display_name: "Secondary Admin",
        is_admin: true,
        is_super_admin: false,
        is_group_member: true
      }
    ]
  };

  async initialize(): Promise<boolean> {
    this.connectionState = ConnectionState.READY;
    this.qrState = QrState.NOT_REQUIRED;
    return true;
  }

  async shutdown(): Promise<void> {
    this.connectionState = ConnectionState.STOPPED;
    this.qrState = QrState.NOT_REQUIRED;
  }

  async listGroups(): Promise<GroupSummary[]> {
    return this.mockGroups;
  }

  async getGroupAdmins(groupId: string): Promise<GroupAdminSummary[]> {
    return this.mockAdmins[groupId] || [];
  }

  onMessage(callback: (msg: any) => void): void {
    this.messageCallback = callback;
  }

  simulateIncomingMessage(msgObj: any): void {
    if (this.messageCallback) {
      this.messageCallback(msgObj);
    }
  }

  async logout(): Promise<void> {
    this.connectionState = ConnectionState.LOGGED_OUT;
  }
}

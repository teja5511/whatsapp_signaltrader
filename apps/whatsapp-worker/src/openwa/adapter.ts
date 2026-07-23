import { GroupSummary, GroupAdminSummary } from "../contracts";
import { ConnectionState, QrState } from "../constants";

export interface OpenWAAdapterInterface {
  readonly mode: "fake" | "real";
  readonly connectionState: ConnectionState;
  readonly qrState: QrState;

  initialize(): Promise<boolean>;
  shutdown(): Promise<void>;
  listGroups(): Promise<GroupSummary[]>;
  getGroupAdmins(groupId: string): Promise<GroupAdminSummary[]>;
  onMessage(callback: (msg: any) => void): void;
  logout(): Promise<void>;
}

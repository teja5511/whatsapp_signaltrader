import { ConnectionState, QrState } from "../constants";
import { globalEventBus } from "./event-bus";

export interface WorkerMetrics {
  messages_received: number;
  messages_accepted: number;
  messages_ignored: number;
  messages_spooled: number;
  messages_delivered: number;
  messages_quarantined: number;
  ignored_reasons: Record<string, number>;
}

export class WorkerStateStore {
  public connectionState: ConnectionState = ConnectionState.DISABLED;
  public qrState: QrState = QrState.NOT_REQUIRED;
  public qrPayload: string | null = null;
  public qrExpiresAt: Date | null = null;

  public sessionAuthenticated: boolean = false;
  public approvedGroupId: string | null = null;
  public approvedGroupDisplayName: string | null = null;
  public approvedAdminId: string | null = null;
  public approvedAdminDisplayName: string | null = null;
  public adminRoleVerified: boolean = false;
  public tradingServiceReachable: boolean = true;
  public processLockOwned: boolean = false;

  public metrics: WorkerMetrics = {
    messages_received: 0,
    messages_accepted: 0,
    messages_ignored: 0,
    messages_spooled: 0,
    messages_delivered: 0,
    messages_quarantined: 0,
    ignored_reasons: {}
  };

  setConnectionState(newState: ConnectionState, reason?: string): void {
    const oldState = this.connectionState;
    this.connectionState = newState;
    globalEventBus.emitEvent("WORKER_STATE_CHANGED", { oldState, newState, reason });
  }

  setQrState(state: QrState, payload?: string, ttlSeconds: number = 60): void {
    this.qrState = state;
    if (state === QrState.AVAILABLE && payload) {
      this.qrPayload = payload;
      this.qrExpiresAt = new Date(Date.now() + ttlSeconds * 1000);
    } else if (state === QrState.AUTHENTICATED || state === QrState.EXPIRED || state === QrState.NOT_REQUIRED) {
      this.qrPayload = null;
      this.qrExpiresAt = null;
    }
    globalEventBus.emitEvent("QR_STATE_CHANGED", { qrState: state });
  }

  incrementIgnored(reason: string): void {
    this.metrics.messages_received += 1;
    this.metrics.messages_ignored += 1;
    this.metrics.ignored_reasons[reason] = (this.metrics.ignored_reasons[reason] || 0) + 1;
    globalEventBus.emitEvent("MESSAGE_IGNORED", { reason });
  }

  isReady(): boolean {
    return (
      this.connectionState === ConnectionState.READY &&
      this.sessionAuthenticated &&
      !!this.approvedGroupId &&
      !!this.approvedAdminId &&
      this.adminRoleVerified &&
      this.processLockOwned
    );
  }
}

export const globalWorkerState = new WorkerStateStore();

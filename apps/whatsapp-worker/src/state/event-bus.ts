import { EventEmitter } from "events";

export type WorkerEventType =
  | "WORKER_STATE_CHANGED"
  | "QR_STATE_CHANGED"
  | "SESSION_AUTHENTICATED"
  | "SESSION_LOGGED_OUT"
  | "GROUP_CONFIGURED"
  | "ADMIN_CONFIGURED"
  | "ADMIN_ROLE_CHANGED"
  | "MESSAGE_ACCEPTED"
  | "MESSAGE_IGNORED"
  | "MESSAGE_SPOOLED"
  | "DELIVERY_STARTED"
  | "DELIVERY_SUCCEEDED"
  | "DELIVERY_RETRY_SCHEDULED"
  | "DELIVERY_QUARANTINED"
  | "TRADING_SERVICE_STATE_CHANGED"
  | "SPOOL_LIMIT_WARNING";

export interface WorkerEvent {
  type: WorkerEventType;
  timestamp: string;
  payload: Record<string, any>;
}

export class WorkerEventBus extends EventEmitter {
  emitEvent(type: WorkerEventType, payload: Record<string, any>): void {
    const event: WorkerEvent = {
      type,
      timestamp: new Date().toISOString(),
      payload
    };
    this.emit("event", event);
    this.emit(type, event);
  }
}

export const globalEventBus = new WorkerEventBus();

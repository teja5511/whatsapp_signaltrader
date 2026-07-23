import { maskId, redactSensitiveObject } from "./redaction";

export interface LogContext {
  service?: string;
  worker_version?: string;
  adapter_mode?: string;
  event?: string;
  worker_id?: string;
  connection_state?: string;
  message_id?: string;
  group_id_masked?: string;
  sender_id_masked?: string;
  correlation_id?: string;
  spool_item_id?: string;
  attempt_count?: number;
  duration_ms?: number;
  [key: string]: any;
}

export class Logger {
  constructor(private readonly serviceName: string = "whatsapp-worker") {}

  info(event: string, ctx: LogContext = {}): void {
    this.log("INFO", event, ctx);
  }

  warn(event: string, ctx: LogContext = {}): void {
    this.log("WARN", event, ctx);
  }

  error(event: string, ctx: LogContext = {}): void {
    this.log("ERROR", event, ctx);
  }

  private log(level: string, event: string, ctx: LogContext): void {
    const payload = redactSensitiveObject({
      timestamp: new Date().toISOString(),
      level,
      service: this.serviceName,
      event,
      ...ctx
    });
    console.log(JSON.stringify(payload));
  }
}

export const logger = new Logger();

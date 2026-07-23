import { apiClient } from "../api/apiClient";
import { RealtimeStatus, DomainEvent } from "../types";

export type EventListener = (event: DomainEvent) => void;
export type StatusListener = (status: RealtimeStatus) => void;

export class RealtimeEventClient {
  private status: RealtimeStatus = "DISCONNECTED";
  private lastSequence: number = 0;
  private processedEventIds = new Set<string>();
  private maxBufferSize = 500;
  private ws: WebSocket | null = null;
  private sse: EventSource | null = null;
  private pollingTimer: any = null;
  private eventListeners: Set<EventListener> = new Set();
  private statusListeners: Set<StatusListener> = new Set();
  private isDestroyed = false;

  public getStatus(): RealtimeStatus {
    return this.status;
  }

  public getLastSequence(): number {
    return this.lastSequence;
  }

  public subscribe(onEvent: EventListener, onStatus?: StatusListener): () => void {
    this.eventListeners.add(onEvent);
    if (onStatus) this.statusListeners.add(onStatus);

    return () => {
      this.eventListeners.delete(onEvent);
      if (onStatus) this.statusListeners.delete(onStatus);
    };
  }

  private setStatus(newStatus: RealtimeStatus) {
    if (this.status !== newStatus) {
      this.status = newStatus;
      this.statusListeners.forEach((fn) => fn(newStatus));
    }
  }

  public async connect(): Promise<void> {
    if (this.isDestroyed) return;
    this.setStatus("CONNECTING");

    try {
      // 1. Fetch short-lived ticket
      const ticketRes = await apiClient.createEventTicket();
      const ticket = ticketRes.ticket;

      // 2. Replay missing events if reconnecting with lastSequence > 0
      if (this.lastSequence > 0) {
        await this.replayEvents();
      } else {
        const seqRes = await apiClient.getLatestEventSequence();
        this.lastSequence = seqRes.latest_sequence || 0;
      }

      // 3. Attempt WebSocket connection
      const wsUrl = apiClient.getBaseUrl().replace(/^http/, "ws") + `/api/v1/events/ws?ticket=${ticket}`;
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        this.setStatus("CONNECTED_WS");
      };

      this.ws.onmessage = (event) => {
        try {
          const domainEvent: DomainEvent = JSON.parse(event.data);
          this.handleIncomingEvent(domainEvent);
        } catch {
          // Ignore invalid message
        }
      };

      this.ws.onerror = () => {
        this.ws?.close();
      };

      this.ws.onclose = () => {
        if (!this.isDestroyed) {
          // Fallback to SSE
          this.connectSSE(ticket);
        }
      };
    } catch {
      // Direct fallback to SSE or Polling
      this.connectSSE();
    }
  }

  private connectSSE(existingTicket?: string): void {
    if (this.isDestroyed) return;
    this.setStatus("CONNECTING");

    const startSSE = (t?: string) => {
      const sseUrl = apiClient.getBaseUrl() + `/api/v1/events/sse${t ? `?ticket=${t}` : ""}`;
      this.sse = new EventSource(sseUrl);

      this.sse.onopen = () => {
        this.setStatus("CONNECTED_SSE");
      };

      this.sse.onmessage = (msg) => {
        try {
          const domainEvent: DomainEvent = JSON.parse(msg.data);
          this.handleIncomingEvent(domainEvent);
        } catch {
          // Ignore invalid msg
        }
      };

      this.sse.onerror = () => {
        this.sse?.close();
        if (!this.isDestroyed) {
          this.startPolling();
        }
      };
    };

    if (existingTicket) {
      startSSE(existingTicket);
    } else {
      apiClient.createEventTicket()
        .then((res) => startSSE(res.ticket))
        .catch(() => this.startPolling());
    }
  }

  private startPolling(): void {
    if (this.isDestroyed) return;
    this.setStatus("POLLING");

    if (this.pollingTimer) clearInterval(this.pollingTimer);

    this.pollingTimer = setInterval(async () => {
      try {
        await this.replayEvents();
      } catch {
        this.setStatus("DEGRADED");
      }
    }, 3000);
  }

  private async replayEvents(): Promise<void> {
    this.setStatus("REPLAYING");
    try {
      const events = await apiClient.listDomainEvents(this.lastSequence, 200);
      for (const e of events) {
        this.handleIncomingEvent(e);
      }
      this.setStatus(this.ws ? "CONNECTED_WS" : this.sse ? "CONNECTED_SSE" : "POLLING");
    } catch {
      this.setStatus("DEGRADED");
    }
  }

  private handleIncomingEvent(event: DomainEvent): void {
    if (!event || !event.event_id) return;

    // Event ID Deduplication & Gap Handling
    if (this.processedEventIds.has(event.event_id)) return;

    this.processedEventIds.add(event.event_id);
    if (this.processedEventIds.size > this.maxBufferSize) {
      const iterator = this.processedEventIds.values();
      const first = iterator.next().value;
      if (first) this.processedEventIds.delete(first);
    }

    if (event.sequence) {
      if (this.lastSequence > 0 && event.sequence > this.lastSequence + 1) {
        // Gap detected! Replay missing sequence gap
        this.replayEvents().catch(() => {});
      }
      if (event.sequence > this.lastSequence) {
        this.lastSequence = event.sequence;
      }
    }

    // Broadcast to listeners
    this.eventListeners.forEach((listener) => {
      try {
        listener(event);
      } catch {
        // Listener error safety block
      }
    });
  }

  public disconnect(): void {
    this.isDestroyed = true;
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    if (this.sse) {
      this.sse.close();
      this.sse = null;
    }
    if (this.pollingTimer) {
      clearInterval(this.pollingTimer);
      this.pollingTimer = null;
    }
    this.setStatus("DISCONNECTED");
  }
}

export const globalEventClient = new RealtimeEventClient();

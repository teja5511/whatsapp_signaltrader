import { secureApiRequest } from "./tauriClient";
import { DEFAULT_FASTAPI_URL, DEFAULT_WORKER_URL } from "../lib/constants";
import { SystemStatus, ControlState, DomainEvent, CampaignConfirmation, AmbiguousCommandConfirmation, CampaignSummary, Mt5Order, Mt5Position, ExecutionJob } from "../types";

export class ApiError extends Error {
  constructor(
    public category: string,
    public status: number,
    message: string,
    public correlationId?: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export class ApiClient {
  private baseUrl: string = DEFAULT_FASTAPI_URL;
  private workerUrl: string = DEFAULT_WORKER_URL;

  setUrls(fastApiUrl: string, workerUrl: string) {
    this.baseUrl = fastApiUrl.replace(/\/$/, "");
    this.workerUrl = workerUrl.replace(/\/$/, "");
  }

  getBaseUrl() { return this.baseUrl; }
  getWorkerUrl() { return this.workerUrl; }

  private async request<T>(
    endpoint: string,
    method: string = "GET",
    body?: any,
    target: "fastapi" | "worker" = "fastapi"
  ): Promise<T> {
    const base = target === "fastapi" ? this.baseUrl : this.workerUrl;
    const url = `${base}${endpoint}`;
    const correlationId = `req-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`;
    const headers: Record<string, string> = {
      "X-Correlation-ID": correlationId,
    };

    try {
      const res = await secureApiRequest(url, method, body, headers);
      if (!res.ok) {
        let errMsg = `HTTP Error ${res.status}`;
        try {
          const parsed = JSON.parse(res.body);
          errMsg = parsed.detail || parsed.message || errMsg;
        } catch {
          if (res.body) errMsg = res.body;
        }

        let cat = "UNKNOWN";
        if (res.status === 401) cat = "AUTHENTICATION";
        else if (res.status === 403) cat = "SAFETY_BLOCK";
        else if (res.status === 404) cat = "NOT_FOUND";
        else if (res.status === 409) cat = "STATE_CONFLICT";
        else if (res.status === 422) cat = "VALIDATION";
        else if (res.status >= 500) cat = "SERVICE_UNAVAILABLE";

        throw new ApiError(cat, res.status, errMsg, correlationId);
      }

      if (!res.body) return {} as T;
      return JSON.parse(res.body) as T;
    } catch (err: any) {
      if (err instanceof ApiError) throw err;
      throw new ApiError("NETWORK", 0, err.message || "Network request failed", correlationId);
    }
  }

  // System Status & Versions
  async getSystemStatus(): Promise<SystemStatus> {
    return this.request<SystemStatus>("/api/v1/system/status");
  }

  async getControlState(): Promise<ControlState> {
    return this.request<ControlState>("/api/v1/control/state");
  }

  async getSystemVersions(): Promise<Record<string, string>> {
    return this.request<Record<string, string>>("/api/v1/system/versions");
  }

  // Automation Controls
  async pauseAutomation(): Promise<ControlState> {
    return this.request<ControlState>("/api/v1/control/automation/pause", "POST");
  }

  async resumeAutomation(): Promise<ControlState> {
    return this.request<ControlState>("/api/v1/control/automation/resume", "POST");
  }

  async triggerEmergencyStop(): Promise<ControlState> {
    return this.request<ControlState>("/api/v1/control/emergency-stop", "POST");
  }

  async resetEmergencyStop(phrase: string): Promise<ControlState> {
    return this.request<ControlState>("/api/v1/control/emergency-stop/reset", "POST", { confirmation_phrase: phrase });
  }

  async enableDemoTrading(phrase: string): Promise<ControlState> {
    return this.request<ControlState>("/api/v1/control/trading/enable-demo", "POST", { confirmation_phrase: phrase });
  }

  async disableTrading(): Promise<ControlState> {
    return this.request<ControlState>("/api/v1/control/trading/disable", "POST");
  }

  // Campaigns & Confirmations
  async listCampaigns(): Promise<CampaignSummary[]> {
    return this.request<CampaignSummary[]>("/api/v1/campaigns");
  }

  async getCampaignDetail(id: string): Promise<any> {
    return this.request<any>(`/api/v1/campaigns/${id}`);
  }

  async approveCampaign(id: string, expectedVersion: number): Promise<any> {
    return this.request<any>(`/api/v1/orchestration/campaigns/${id}/approve?expected_version=${expectedVersion}`, "POST");
  }

  async rejectCampaign(id: string, expectedVersion: number): Promise<any> {
    return this.request<any>(`/api/v1/campaigns/${id}/reject`, "POST", { expected_version: expectedVersion });
  }

  async listConfirmations(): Promise<{ campaign_confirmations: CampaignConfirmation[]; ambiguous_command_confirmations: AmbiguousCommandConfirmation[] }> {
    return this.request<{ campaign_confirmations: CampaignConfirmation[]; ambiguous_command_confirmations: AmbiguousCommandConfirmation[] }>("/api/v1/confirmations");
  }

  async resolveAmbiguousCommand(id: string, action: string): Promise<any> {
    return this.request<any>(`/api/v1/confirmations/ambiguous/${id}/resolve`, "POST", { action });
  }

  // MT5 Status & Trade Actions
  async getMt5Status(): Promise<any> {
    return this.request<any>("/api/v1/mt5/status");
  }

  async getMt5Account(): Promise<any> {
    return this.request<any>("/api/v1/mt5/account");
  }

  async getMt5Symbol(): Promise<any> {
    return this.request<any>("/api/v1/mt5/symbol");
  }

  async getMt5Orders(): Promise<Mt5Order[]> {
    return this.request<Mt5Order[]>("/api/v1/mt5/orders");
  }

  async getMt5Positions(): Promise<Mt5Position[]> {
    return this.request<Mt5Position[]>("/api/v1/mt5/positions");
  }

  async getMt5History(): Promise<any[]> {
    return this.request<any[]>("/api/v1/mt5/history");
  }

  async getExecutionBatches(): Promise<any[]> {
    return this.request<any[]>("/api/v1/mt5/execution/batches");
  }

  async listExecutionJobs(): Promise<ExecutionJob[]> {
    return this.request<ExecutionJob[]>("/api/v1/mt5/execution/jobs");
  }

  async initializeMt5(): Promise<any> {
    return this.request<any>("/api/v1/mt5/initialize", "POST");
  }

  async shutdownMt5(): Promise<any> {
    return this.request<any>("/api/v1/mt5/shutdown", "POST");
  }

  async emergencyCloseAll(phrase: string, scope: string = "APPLICATION_OWNED"): Promise<any> {
    return this.request<any>("/api/v1/mt5/emergency/close-all-xauusd", "POST", { confirmation_phrase: phrase, scope });
  }

  // WhatsApp Worker Status & Session
  async getWhatsAppStatus(): Promise<any> {
    return this.request<any>("/api/v1/whatsapp/status", "GET", undefined, "worker");
  }

  async getWhatsAppSession(): Promise<any> {
    return this.request<any>("/api/v1/whatsapp/session", "GET", undefined, "worker");
  }

  async getWhatsAppSpool(): Promise<any> {
    return this.request<any>("/api/v1/whatsapp/spool", "GET", undefined, "worker");
  }

  async resetWhatsAppSession(phrase: string): Promise<any> {
    return this.request<any>("/api/v1/whatsapp/session/reset", "POST", { confirmation_phrase: phrase }, "worker");
  }

  async listWhatsAppGroups(): Promise<any[]> {
    return this.request<any[]>("/groups", "GET", undefined, "worker");
  }

  async resolveGroupInviteLink(inviteLink: string): Promise<any> {
    return this.request<any>("/groups/resolve-link", "POST", { invite_link: inviteLink }, "worker");
  }

  async setWhatsAppGroup(groupId: string, groupDisplayName?: string): Promise<any> {
    return this.request<any>("/configuration/group", "POST", { approved_group_id: groupId, approved_group_display_name: groupDisplayName }, "worker");
  }

  async setWhatsAppAdmin(adminId: string, adminDisplayName?: string): Promise<any> {
    return this.request<any>("/configuration/admin", "POST", { approved_admin_id: adminId, approved_admin_display_name: adminDisplayName }, "worker");
  }

  async getWhatsAppConfiguration(): Promise<any> {
    return this.request<any>("/configuration", "GET", undefined, "worker");
  }

  // Selected Groups SQLite Endpoints
  async getSelectedGroups(): Promise<any[]> {
    return this.request<any[]>("/selected-groups", "GET", undefined, "worker");
  }

  async addSelectedGroup(jid: string, name?: string): Promise<any> {
    return this.request<any>("/selected-groups", "POST", { jid, name }, "worker");
  }

  async deleteSelectedGroup(jid: string): Promise<any> {
    return this.request<any>(`/selected-groups/${encodeURIComponent(jid)}`, "DELETE", undefined, "worker");
  }

  async patchSelectedGroup(jid: string, enabled: boolean): Promise<any> {
    return this.request<any>(`/selected-groups/${encodeURIComponent(jid)}`, "PATCH", { enabled }, "worker");
  }

  // Realtime Ticket & Event Replay
  async createEventTicket(): Promise<{ ticket: string; expires_in_seconds: number }> {
    return this.request<{ ticket: string; expires_in_seconds: number }>("/api/v1/events/ticket", "POST");
  }

  async listDomainEvents(afterSequence?: number, limit: number = 100): Promise<DomainEvent[]> {
    const query = afterSequence !== undefined ? `?after_sequence=${afterSequence}&limit=${limit}` : `?limit=${limit}`;
    return this.request<DomainEvent[]>(`/api/v1/events${query}`);
  }

  async getLatestEventSequence(): Promise<{ latest_sequence: number }> {
    return this.request<{ latest_sequence: number }>("/api/v1/events/latest-sequence");
  }
}

export const apiClient = new ApiClient();

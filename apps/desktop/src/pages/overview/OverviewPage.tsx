import React from "react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../../api/apiClient";
import { Card, CardHeader, CardTitle, CardDescription } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { useUiStore } from "../../stores/uiStore";
import { CONTROL_PHRASES } from "../../lib/constants";
import { Play, Pause, AlertOctagon, CheckCircle2, RefreshCw, Zap, Shield, Lock } from "lucide-react";

export const OverviewPage: React.FC = () => {
  const { openConfirmModal } = useUiStore();

  const { data: status, refetch } = useQuery({
    queryKey: ["systemStatus"],
    queryFn: () => apiClient.getSystemStatus(),
    refetchInterval: 3000,
  });

  const { data: campaigns } = useQuery({
    queryKey: ["campaigns"],
    queryFn: () => apiClient.listCampaigns(),
    refetchInterval: 5000,
  });

  const { data: confirmations } = useQuery({
    queryKey: ["confirmations"],
    queryFn: () => apiClient.listConfirmations(),
    refetchInterval: 5000,
  });

  const { data: events } = useQuery({
    queryKey: ["recentEvents"],
    queryFn: () => apiClient.listDomainEvents(undefined, 10),
    refetchInterval: 3000,
  });

  // Action Handlers
  const handlePause = async () => {
    await apiClient.pauseAutomation();
    refetch();
  };

  const handleResume = async () => {
    await apiClient.resumeAutomation();
    refetch();
  };

  const handleEnableDemo = () => {
    openConfirmModal({
      type: "ENABLE_DEMO",
      title: "Enable Demo XAUUSD Trading",
      description: "This unlocks automated demo order execution on Exness MT5 Hedging Demo Account. Max total exposure is capped at 2.00 lots.",
      phrase: CONTROL_PHRASES.ENABLE_DEMO,
      action: async () => {
        await apiClient.enableDemoTrading(CONTROL_PHRASES.ENABLE_DEMO);
        refetch();
      },
    });
  };

  const handleDisableTrading = async () => {
    await apiClient.disableTrading();
    refetch();
  };

  const handleEmergencyStop = () => {
    openConfirmModal({
      type: "EMERGENCY_STOP",
      title: "Trigger Emergency System Stop",
      description: "Immediately halts all background automation and blocks pending trade execution. Does NOT automatically close open positions.",
      phrase: CONTROL_PHRASES.EMERGENCY_STOP,
      action: async () => {
        await apiClient.triggerEmergencyStop();
        refetch();
      },
    });
  };

  const handleResetEmergencyStop = () => {
    openConfirmModal({
      type: "RESET_EMERGENCY_STOP",
      title: "Reset Emergency Stop",
      description: "Clears the EMERGENCY_STOPPED state and returns system to PAUSED. Does NOT automatically enable trading.",
      phrase: CONTROL_PHRASES.RESET_EMERGENCY_STOP,
      action: async () => {
        await apiClient.resetEmergencyStop(CONTROL_PHRASES.RESET_EMERGENCY_STOP);
        refetch();
      },
    });
  };

  // Campaign Counters
  const cList = campaigns || [];
  const countAwaiting = cList.filter((c) => c.state === "AWAITING_CONFIRMATION").length;
  const countPlanned = cList.filter((c) => c.state === "PLANNED").length;
  const countPlacing = cList.filter((c) => c.state === "PLACING_ORDERS").length;
  const countPending = cList.filter((c) => c.state === "PENDING").length;
  const countOpen = cList.filter((c) => c.state === "OPEN").length;
  const countFailed = cList.filter((c) => c.state === "FAILED").length;

  return (
    <div className="space-y-6">
      {/* Header Bar */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold font-mono text-slate-100">System Overview & Command Center</h1>
          <p className="text-xs text-slate-400 mt-1">Real-time status monitoring and execution controls for XAUUSD trading bot.</p>
        </div>
        <Button variant="secondary" size="sm" onClick={() => refetch()} className="gap-2 font-mono">
          <RefreshCw className="w-3.5 h-3.5" /> Refresh
        </Button>
      </div>

      {/* System Readiness Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <Card className="p-4">
          <CardDescription>FastAPI Service</CardDescription>
          <div className="mt-2 flex items-center justify-between">
            <CardTitle>FastAPI</CardTitle>
            <Badge status={status?.overall_state === "HEALTHY" ? "HEALTHY" : "DEGRADED"} />
          </div>
        </Card>

        <Card className="p-4">
          <CardDescription>Database (SQLite)</CardDescription>
          <div className="mt-2 flex items-center justify-between">
            <CardTitle>Database</CardTitle>
            <Badge status={status?.database?.connected ? "CONNECTED" : "OFFLINE"} />
          </div>
        </Card>

        <Card className="p-4">
          <CardDescription>WhatsApp Worker</CardDescription>
          <div className="mt-2 flex items-center justify-between">
            <CardTitle>WhatsApp</CardTitle>
            <Badge status={status?.whatsapp_worker?.connected ? "CONNECTED" : "OFFLINE"} />
          </div>
        </Card>

        <Card className="p-4">
          <CardDescription>MT5 Terminal IPC</CardDescription>
          <div className="mt-2 flex items-center justify-between">
            <CardTitle>MT5 Adapter</CardTitle>
            <Badge status={status?.mt5_adapter?.initialized ? "INITIALIZED" : "UNINITIALIZED"} />
          </div>
        </Card>

        <Card className="p-4">
          <CardDescription>Execution Worker</CardDescription>
          <div className="mt-2 flex items-center justify-between">
            <CardTitle>Worker</CardTitle>
            <Badge status={status?.mt5_adapter?.initialized ? "RUNNING" : "STOPPED"} />
          </div>
        </Card>

        <Card className="p-4">
          <CardDescription>Event Stream</CardDescription>
          <div className="mt-2 flex items-center justify-between">
            <CardTitle>Outbox SSE</CardTitle>
            <Badge status="ACTIVE" />
          </div>
        </Card>
      </div>

      {/* Trading Control Panel */}
      <Card className="border-sky-900/40">
        <CardHeader>
          <div>
            <CardTitle className="text-sky-400 flex items-center gap-2">
              <Zap className="w-4 h-4" /> Operational Controls & Safety Gating
            </CardTitle>
            <CardDescription>Manage automation state and demo trade execution permissions.</CardDescription>
          </div>
          <Badge status={status?.automation_state || "PAUSED"} className="text-sm px-3 py-1" />
        </CardHeader>

        <div className="flex flex-wrap items-center gap-3 pt-2">
          {status?.automation_state === "RUNNING" ? (
            <Button variant="warning" onClick={handlePause} className="gap-2">
              <Pause className="w-4 h-4" /> Pause Automation
            </Button>
          ) : (
            <Button variant="primary" onClick={handleResume} disabled={status?.automation_state === "EMERGENCY_STOPPED"} className="gap-2">
              <Play className="w-4 h-4" /> Resume Automation
            </Button>
          )}

          {status?.trading_enabled ? (
            <Button variant="secondary" onClick={handleDisableTrading} className="gap-2">
              <Lock className="w-4 h-4" /> Lock Demo Trading
            </Button>
          ) : (
            <Button variant="primary" onClick={handleEnableDemo} className="gap-2 bg-emerald-600 hover:bg-emerald-500">
              <Shield className="w-4 h-4" /> Enable Demo Trading
            </Button>
          )}

          {status?.automation_state === "EMERGENCY_STOPPED" ? (
            <Button variant="secondary" onClick={handleResetEmergencyStop} className="gap-2 border-amber-600 text-amber-300">
              <RefreshCw className="w-4 h-4" /> Reset Emergency Stop
            </Button>
          ) : (
            <Button variant="danger" onClick={handleEmergencyStop} className="gap-2 ml-auto">
              <AlertOctagon className="w-4 h-4" /> EMERGENCY STOP
            </Button>
          )}
        </div>
      </Card>

      {/* Campaign Status Counters */}
      <div className="grid grid-cols-2 md:grid-cols-6 gap-4 font-mono">
        <Card className="text-center p-4">
          <span className="text-2xl font-bold text-amber-400">{countAwaiting}</span>
          <CardDescription className="mt-1">Awaiting Confirmation</CardDescription>
        </Card>
        <Card className="text-center p-4">
          <span className="text-2xl font-bold text-sky-400">{countPlanned}</span>
          <CardDescription className="mt-1">Planned</CardDescription>
        </Card>
        <Card className="text-center p-4">
          <span className="text-2xl font-bold text-indigo-400">{countPlacing}</span>
          <CardDescription className="mt-1">Placing Orders</CardDescription>
        </Card>
        <Card className="text-center p-4">
          <span className="text-2xl font-bold text-slate-300">{countPending}</span>
          <CardDescription className="mt-1">Pending Orders</CardDescription>
        </Card>
        <Card className="text-center p-4">
          <span className="text-2xl font-bold text-emerald-400">{countOpen}</span>
          <CardDescription className="mt-1">Open Positions</CardDescription>
        </Card>
        <Card className="text-center p-4">
          <span className="text-2xl font-bold text-rose-400">{countFailed}</span>
          <CardDescription className="mt-1">Failed</CardDescription>
        </Card>
      </div>

      {/* Safety Summary Card */}
      <Card className="bg-slate-950/60 font-mono text-xs space-y-3">
        <CardTitle className="text-slate-300">Safety & Execution Parameters</CardTitle>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-slate-400 border-t border-slate-800/80 pt-3">
          <div>
            <span className="text-slate-500 block">Instrument:</span>
            <span className="text-slate-200 font-bold">XAUUSD</span>
          </div>
          <div>
            <span className="text-slate-500 block">Max Exposure Volume:</span>
            <span className="text-slate-200 font-bold">2.0000 Lots</span>
          </div>
          <div>
            <span className="text-slate-500 block">Max Entries per Signal:</span>
            <span className="text-slate-200 font-bold">8 Entries</span>
          </div>
          <div>
            <span className="text-slate-500 block">Live Trade Execution:</span>
            <span className="text-emerald-400 font-bold uppercase">BLOCKED (DEMO ONLY)</span>
          </div>
        </div>
      </Card>
    </div>
  );
};

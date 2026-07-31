import React from "react";
import { Badge } from "./ui/Badge";
import { SystemStatus, RealtimeStatus } from "../types";
import { Lock, AlertTriangle } from "lucide-react";

interface TopbarProps {
  systemStatus?: SystemStatus;
  realtimeStatus?: RealtimeStatus;
  fastApiHealthy?: boolean;
}

export const Topbar: React.FC<TopbarProps> = ({
  systemStatus,
  realtimeStatus = "DISCONNECTED",
  fastApiHealthy = true,
}) => {
  const isDemo = systemStatus?.mt5_adapter?.account_environment === "DEMO";
  const liveBlocked = systemStatus?.mt5_adapter?.live_blocked ?? true;

  return (
    <header className="h-16 bg-slate-950/90 border-b border-slate-800/80 px-6 flex items-center justify-between shrink-0 font-mono text-xs z-20 backdrop-blur-sm">
      {/* Account Safety Badge */}
      <div className="flex items-center gap-3">
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-md bg-emerald-950/90 text-emerald-400 border border-emerald-800 font-bold tracking-wider uppercase text-xs">
          <Lock className="w-3.5 h-3.5" />
          DEMO ONLY (EXNESS MT5)
        </span>
        {liveBlocked && (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-slate-900 text-slate-400 border border-slate-800 text-[11px]">
            REAL ACCOUNT BLOCKED
          </span>
        )}
      </div>

      {/* Realtime Indicators */}
      <div className="flex items-center gap-2 overflow-x-auto no-scrollbar scrollbar-none [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden">
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-900/90 border border-slate-800">
          <span className="text-slate-500 font-semibold">AUTO:</span>
          <Badge status={systemStatus?.automation_state || "PAUSED"} />
        </div>

        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-900/90 border border-slate-800">
          <span className="text-slate-500 font-semibold">MODE:</span>
          <Badge status={systemStatus?.execution_mode || "CONFIRMATION"} />
        </div>

        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-900/90 border border-slate-800">
          <span className="text-slate-500 font-semibold">TRADING:</span>
          <Badge status={systemStatus?.trading_enabled ? "ENABLED" : "DISABLED"} />
        </div>

        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-900/90 border border-slate-800">
          <span className="text-slate-500 font-semibold">WA:</span>
          <Badge status={systemStatus?.whatsapp_worker?.connected ? "CONNECTED" : "OFFLINE"} />
        </div>

        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-900/90 border border-slate-800">
          <span className="text-slate-500 font-semibold">MT5:</span>
          <Badge status={systemStatus?.mt5_adapter?.initialized ? "INITIALIZED" : "UNINITIALIZED"} />
        </div>

        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-900/90 border border-slate-800">
          <span className="text-slate-500 font-semibold">API:</span>
          <Badge status={fastApiHealthy ? "HEALTHY" : "OFFLINE"} />
        </div>

        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-900/90 border border-slate-800">
          <span className="text-slate-500 font-semibold">EVENT:</span>
          <Badge status={realtimeStatus} />
        </div>
      </div>
    </header>
  );
};

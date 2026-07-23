import React from "react";
import { AlertTriangle, ShieldAlert, ZapOff } from "lucide-react";
import { SystemStatus } from "../types";
import { useUiStore } from "../stores/uiStore";

interface SafetyBannerProps {
  systemStatus?: SystemStatus;
  fastApiOffline?: boolean;
}

export const SafetyBanner: React.FC<SafetyBannerProps> = ({ systemStatus, fastApiOffline }) => {
  const { mockMode } = useUiStore();

  const isEmergencyStopped = systemStatus?.automation_state === "EMERGENCY_STOPPED";
  const isRealAccountDetected = systemStatus?.mt5_adapter?.is_live_account || systemStatus?.mt5_adapter?.account_environment === "REAL";

  if (!isEmergencyStopped && !isRealAccountDetected && !fastApiOffline && !mockMode) {
    return null;
  }

  return (
    <div className="space-y-2 select-none">
      {mockMode && (
        <div className="bg-amber-950/90 border-b border-amber-800 text-amber-200 px-6 py-2 flex items-center justify-between font-mono text-xs shadow-md">
          <div className="flex items-center gap-2 font-bold tracking-wide">
            <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
            <span>MOCK MODE ENABLED — Using local mock fixtures. No live network trade execution.</span>
          </div>
          <span className="text-[10px] bg-amber-900/80 px-2 py-0.5 rounded border border-amber-700">VITE_DESKTOP_MOCK_MODE=true</span>
        </div>
      )}

      {isEmergencyStopped && (
        <div className="bg-rose-950/95 border-b border-rose-800 text-rose-100 px-6 py-3 flex items-center justify-between font-mono text-xs shadow-lg animate-pulse">
          <div className="flex items-center gap-3 font-bold tracking-wide">
            <ZapOff className="w-5 h-5 text-rose-400 shrink-0" />
            <div>
              <span className="text-sm uppercase font-extrabold text-rose-300">EMERGENCY STOP ACTIVE</span>
              <p className="text-[11px] text-rose-200 font-normal mt-0.5">
                All automated trading actions & new campaign submissions are halted. Reset requires typing &quot;RESET EMERGENCY STOP&quot;.
              </p>
            </div>
          </div>
        </div>
      )}

      {isRealAccountDetected && (
        <div className="bg-rose-950/95 border-b border-rose-800 text-rose-100 px-6 py-3 flex items-center justify-between font-mono text-xs shadow-lg">
          <div className="flex items-center gap-3 font-bold tracking-wide">
            <ShieldAlert className="w-5 h-5 text-rose-400 shrink-0" />
            <div>
              <span className="text-sm uppercase font-extrabold text-rose-300">REAL ACCOUNT DETECTED — EXECUTION BLOCKED</span>
              <p className="text-[11px] text-rose-200 font-normal mt-0.5">
                System is restricted to Exness MT5 Hedging Demo accounts only. Live trading is strictly impossible.
              </p>
            </div>
          </div>
        </div>
      )}

      {fastApiOffline && (
        <div className="bg-slate-900 border-b border-rose-900/60 text-slate-200 px-6 py-2.5 flex items-center justify-between font-mono text-xs shadow-md">
          <div className="flex items-center gap-2 font-semibold text-rose-400">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>FastAPI Backend Offline (http://127.0.0.1:8000) — UI operating in degraded view mode.</span>
          </div>
          <span className="text-[10px] text-slate-400">Check server process</span>
        </div>
      )}
    </div>
  );
};

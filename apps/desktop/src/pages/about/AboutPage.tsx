import React from "react";
import { Card, CardHeader, CardTitle, CardDescription } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { ShieldCheck, Info, Lock } from "lucide-react";
import { DESKTOP_VERSION, DASHBOARD_CONTRACT_VERSION, DESKTOP_EVENT_CLIENT_VERSION } from "../../lib/constants";

export const AboutPage: React.FC = () => {
  return (
    <div className="space-y-6 font-mono max-w-4xl">
      <div>
        <h1 className="text-xl font-bold text-slate-100 font-mono">About WhatsApp MT5 Trading Bot</h1>
        <p className="text-xs text-slate-400 mt-1">System architecture, version manifests, and strict safety assurances.</p>
      </div>

      {/* Safety Assurances Card */}
      <Card className="border-emerald-800/60 bg-emerald-950/20">
        <CardHeader>
          <CardTitle className="text-emerald-400 flex items-center gap-2">
            <ShieldCheck className="w-5 h-5" /> Safety & Execution Mandate
          </CardTitle>
        </CardHeader>
        <div className="space-y-2 text-xs text-slate-300 font-mono leading-relaxed p-2">
          <p>✔ <strong>Demo-only execution:</strong> Restricted exclusively to Exness MT5 Hedging Demo accounts.</p>
          <p>✔ <strong>Single Instrument:</strong> XAUUSD (Gold vs US Dollar) only.</p>
          <p>✔ <strong>Live-account block:</strong> Hardcoded check strictly blocks any real-money live account login.</p>
          <p>✔ <strong>No LLMs / AI:</strong> 100% deterministic regex parsing and state machine rules.</p>
        </div>
      </Card>

      {/* System Version Manifest */}
      <Card>
        <CardHeader>
          <CardTitle className="text-slate-200 flex items-center gap-2">
            <Info className="w-4 h-4 text-sky-400" /> Component & Contract Versions
          </CardTitle>
        </CardHeader>

        <div className="grid grid-cols-2 gap-4 text-xs font-mono border-t border-slate-800 pt-4">
          <div><span className="text-slate-400">Desktop Application:</span> <span className="text-slate-100 font-bold">v{DESKTOP_VERSION}</span></div>
          <div><span className="text-slate-400">Dashboard Contract:</span> <span className="text-slate-100 font-bold">v{DASHBOARD_CONTRACT_VERSION}</span></div>
          <div><span className="text-slate-400">Event Client:</span> <span className="text-slate-100 font-bold">v{DESKTOP_EVENT_CLIENT_VERSION}</span></div>
          <div><span className="text-slate-400">Tauri Shell:</span> <span className="text-slate-100 font-bold">v2.0.0</span></div>
          <div><span className="text-slate-400">React Framework:</span> <span className="text-slate-100 font-bold">v18.2.0</span></div>
          <div><span className="text-slate-400">TypeScript:</span> <span className="text-slate-100 font-bold">v5.4.0</span></div>
          <div><span className="text-slate-400">Backend Orchestrator:</span> <span className="text-slate-100 font-bold">v1.0.0</span></div>
          <div><span className="text-slate-400">Event Contract:</span> <span className="text-slate-100 font-bold">v1.0.0</span></div>
        </div>
      </Card>
    </div>
  );
};

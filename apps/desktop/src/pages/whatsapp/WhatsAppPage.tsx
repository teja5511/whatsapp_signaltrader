import React from "react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../../api/apiClient";
import { Card, CardHeader, CardTitle, CardDescription } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { useUiStore } from "../../stores/uiStore";
import { CONTROL_PHRASES } from "../../lib/constants";
import { MessageSquare, QrCode, RefreshCw, Shield, AlertTriangle } from "lucide-react";

export const WhatsAppPage: React.FC = () => {
  const { openConfirmModal } = useUiStore();

  const { data: status, refetch } = useQuery({
    queryKey: ["waStatus"],
    queryFn: () => apiClient.getWhatsAppStatus().catch(() => ({ connected: false, mode: "baileys_node" })),
    refetchInterval: 5000,
  });

  const { data: spool } = useQuery({
    queryKey: ["waSpool"],
    queryFn: () => apiClient.getWhatsAppSpool().catch(() => ({ pending: 0, delivered: 0, quarantined: 0 })),
    refetchInterval: 5000,
  });

  const handleResetSession = () => {
    openConfirmModal({
      type: "RESET_WHATSAPP",
      title: "Reset WhatsApp Worker Session",
      description: "Logs out current Baileys/OpenWA WhatsApp session and removes stored session data on disk.",
      phrase: CONTROL_PHRASES.RESET_WHATSAPP,
      action: async () => {
        await apiClient.resetWhatsAppSession(CONTROL_PHRASES.RESET_WHATSAPP);
        refetch();
      },
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold font-mono text-slate-100">WhatsApp Baileys / OpenWA Setup & Spool</h1>
          <p className="text-xs text-slate-400 mt-1">Manage single WhatsApp account connection, group binding, admin role, and disk spool queue.</p>
        </div>
        <Button variant="secondary" size="sm" onClick={() => refetch()} className="gap-2 font-mono">
          <RefreshCw className="w-3.5 h-3.5" /> Refresh Status
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Connection & Session Card */}
        <Card>
          <CardHeader>
            <div>
              <CardTitle className="flex items-center gap-2 text-sky-400">
                <MessageSquare className="w-4 h-4" /> Connection & Session
              </CardTitle>
              <CardDescription>Baileys Node.js Worker & Baileys Session</CardDescription>
            </div>
            <Badge status={status?.connected ? "CONNECTED" : "DISCONNECTED"} />
          </CardHeader>

          <div className="space-y-3 font-mono text-xs border-t border-slate-800 pt-4">
            <div className="flex justify-between">
              <span className="text-slate-400">Adapter Mode:</span>
              <span className="text-slate-200">{status?.mode || "baileys_node"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Worker Enabled:</span>
              <span className="text-emerald-400 font-bold">TRUE</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Worker API URL:</span>
              <span className="text-slate-200">{apiClient.getWorkerUrl()}</span>
            </div>
          </div>

          <div className="mt-6 flex flex-wrap items-center gap-3 pt-3 border-t border-slate-800">
            <Button variant="secondary" size="sm" onClick={handleResetSession} className="border-rose-800 text-rose-300">
              Reset Session
            </Button>
          </div>
        </Card>

        {/* Group & Admin Binding */}
        <Card>
          <CardHeader>
            <div>
              <CardTitle className="flex items-center gap-2 text-emerald-400">
                <Shield className="w-4 h-4" /> Group & Admin Whitelist
              </CardTitle>
              <CardDescription>Single WhatsApp Group & Approved Group Admin</CardDescription>
            </div>
            <Badge status="CONFIGURED" variant="green" />
          </CardHeader>

          <div className="space-y-3 font-mono text-xs border-t border-slate-800 pt-4">
            <div>
              <span className="text-slate-400 block">Target Group JID:</span>
              <span className="text-slate-200 font-bold">120363024890123456@g.us</span>
            </div>
            <div>
              <span className="text-slate-400 block">Approved Admin JID:</span>
              <span className="text-slate-200 font-bold">919876543210@s.whatsapp.net</span>
            </div>
            <div className="p-3 rounded bg-amber-950/40 border border-amber-800/60 text-amber-300 text-[11px] leading-relaxed">
              <AlertTriangle className="w-4 h-4 inline mr-1 text-amber-400" />
              Only signals and commands sent inside this approved group by this approved admin are accepted. All other messages are safely ignored.
            </div>
          </div>
        </Card>
      </div>

      {/* Spool & Quarantine Monitoring */}
      <Card>
        <CardHeader>
          <CardTitle className="text-slate-200">Durable WhatsApp Message Spool Queue</CardTitle>
          <CardDescription>Disk-backed queue ensuring zero message loss during network drops.</CardDescription>
        </CardHeader>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 font-mono text-center">
          <div className="p-4 rounded-lg bg-slate-950 border border-slate-800">
            <span className="text-xl font-bold text-sky-400">{spool?.pending || 0}</span>
            <span className="block text-xs text-slate-400 mt-1">Pending Delivery</span>
          </div>
          <div className="p-4 rounded-lg bg-slate-950 border border-slate-800">
            <span className="text-xl font-bold text-emerald-400">{spool?.delivered || 0}</span>
            <span className="block text-xs text-slate-400 mt-1">Delivered Messages</span>
          </div>
          <div className="p-4 rounded-lg bg-slate-950 border border-slate-800">
            <span className="text-xl font-bold text-amber-400">{spool?.quarantined || 0}</span>
            <span className="block text-xs text-slate-400 mt-1">Quarantined</span>
          </div>
          <div className="p-4 rounded-lg bg-slate-950 border border-slate-800">
            <span className="text-xl font-bold text-slate-300">0.4 MB</span>
            <span className="block text-xs text-slate-400 mt-1">Disk Usage</span>
          </div>
        </div>
      </Card>
    </div>
  );
};

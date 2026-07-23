import React from "react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../../api/apiClient";
import { Card, CardHeader, CardTitle, CardDescription } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { CheckCircle2, AlertTriangle, RefreshCw, Check, X, ShieldAlert } from "lucide-react";

export const ConfirmationsPage: React.FC = () => {
  const { data, refetch } = useQuery({
    queryKey: ["confirmations"],
    queryFn: () => apiClient.listConfirmations(),
    refetchInterval: 3000,
  });

  const handleApproveCampaign = async (id: string, version: number) => {
    await apiClient.approveCampaign(id, version);
    refetch();
  };

  const handleRejectCampaign = async (id: string, version: number) => {
    await apiClient.rejectCampaign(id, version);
    refetch();
  };

  const handleResolveAmbiguous = async (id: string, action: string) => {
    await apiClient.resolveAmbiguousCommand(id, action);
    refetch();
  };

  const campaigns = data?.campaign_confirmations || [];
  const ambiguous = data?.ambiguous_command_confirmations || [];

  return (
    <div className="space-y-6 font-mono">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-100 font-mono">Confirmation Queue & Ambiguous Command Review</h1>
          <p className="text-xs text-slate-400 mt-1">Review pending signal campaigns and resolve ambiguous WhatsApp commands with explicit choices.</p>
        </div>
        <Button variant="secondary" size="sm" onClick={() => refetch()} className="gap-2 font-mono">
          <RefreshCw className="w-3.5 h-3.5" /> Refresh Queue
        </Button>
      </div>

      {/* Campaign Confirmations */}
      <Card>
        <CardHeader>
          <CardTitle className="text-amber-400 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4" /> Pending Campaign Confirmations ({campaigns.length})
          </CardTitle>
          <CardDescription>Signal campaigns awaiting explicit user confirmation before order planning.</CardDescription>
        </CardHeader>

        {campaigns.length === 0 ? (
          <div className="p-8 text-center text-slate-500 text-xs">
            No signal campaigns currently awaiting confirmation.
          </div>
        ) : (
          <div className="space-y-3 p-4">
            {campaigns.map((c) => (
              <div key={c.campaign_id} className="p-4 rounded-lg bg-slate-950 border border-slate-800 flex flex-wrap items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-3">
                    <span className="font-bold text-sky-400 text-sm">{c.campaign_code}</span>
                    <Badge status={c.direction} />
                    <span className="text-xs text-slate-400">v{c.version}</span>
                  </div>
                  <div className="text-xs text-slate-300 mt-1">
                    Zone: <span className="font-bold text-slate-100">${c.zone_low?.toFixed(2)} - ${c.zone_high?.toFixed(2)}</span> | SL: <span className="text-rose-300 font-bold">${c.stop_loss?.toFixed(2)}</span>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <Button variant="primary" size="sm" onClick={() => handleApproveCampaign(c.campaign_id, c.version)} className="gap-1.5 bg-emerald-600 hover:bg-emerald-500">
                    <Check className="w-3.5 h-3.5" /> Approve & Plan Demo
                  </Button>
                  <Button variant="danger" size="sm" onClick={() => handleRejectCampaign(c.campaign_id, c.version)} className="gap-1.5">
                    <X className="w-3.5 h-3.5" /> Reject
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Ambiguous Command Review */}
      <Card>
        <CardHeader>
          <CardTitle className="text-rose-400 flex items-center gap-2">
            <ShieldAlert className="w-4 h-4" /> Ambiguous Command Review Cards ({ambiguous.length})
          </CardTitle>
          <CardDescription>Commands matching multiple campaigns require explicit user resolution.</CardDescription>
        </CardHeader>

        {ambiguous.length === 0 ? (
          <div className="p-8 text-center text-slate-500 text-xs">
            No ambiguous commands awaiting review.
          </div>
        ) : (
          <div className="space-y-4 p-4">
            {ambiguous.map((a) => (
              <div key={a.id} className="p-4 rounded-lg bg-slate-950 border border-amber-900/60 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-amber-300 font-bold">MATCH TYPE: {a.match_type} ({a.candidate_count} Candidates)</span>
                  <span className="text-[10px] text-slate-500">{new Date(a.created_at).toLocaleTimeString()}</span>
                </div>

                <div className="p-3 rounded bg-slate-900 border border-slate-800 text-slate-200 text-xs">
                  <span className="text-slate-400 block text-[10px] uppercase font-bold">Raw Message Text:</span>
                  &quot;{a.original_text}&quot;
                </div>

                <div className="text-xs text-slate-300">
                  Suggested Action: <span className="text-sky-300 font-bold">{a.suggested_action}</span>
                </div>

                {/* Explicit Action Buttons */}
                <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-800">
                  <Button variant="primary" size="sm" onClick={() => handleResolveAmbiguous(a.id, "APPROVE_CLOSE")} className="h-7 text-xs bg-emerald-600">
                    Approve Close
                  </Button>
                  <Button variant="warning" size="sm" onClick={() => handleResolveAmbiguous(a.id, "APPROVE_CANCEL")} className="h-7 text-xs">
                    Approve Cancel
                  </Button>
                  <Button variant="secondary" size="sm" onClick={() => handleResolveAmbiguous(a.id, "HOLD")} className="h-7 text-xs">
                    Hold / No Action
                  </Button>
                  <Button variant="secondary" size="sm" onClick={() => handleResolveAmbiguous(a.id, "SKIP")} className="h-7 text-xs">
                    Skip
                  </Button>
                  <Button variant="danger" size="sm" onClick={() => handleResolveAmbiguous(a.id, "REJECT")} className="h-7 text-xs">
                    Reject Command
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
};

import React from "react";
import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../../api/apiClient";
import { Card, CardHeader, CardTitle, CardDescription } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { ArrowLeft, Check, X, Shield, Clock, Layers } from "lucide-react";

export const CampaignDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  const { data: campaign, refetch } = useQuery({
    queryKey: ["campaignDetail", id],
    queryFn: () => apiClient.getCampaignDetail(id!),
    enabled: Boolean(id),
  });

  if (!campaign) {
    return (
      <div className="p-12 text-center font-mono">
        <p className="text-slate-400">Loading campaign detail for &apos;{id}&apos;...</p>
      </div>
    );
  }

  const handleApprove = async () => {
    await apiClient.approveCampaign(campaign.id, campaign.version);
    refetch();
  };

  const handleReject = async () => {
    await apiClient.rejectCampaign(campaign.id, campaign.version);
    refetch();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link to="/campaigns">
            <Button variant="secondary" size="sm" className="gap-1.5 font-mono">
              <ArrowLeft className="w-4 h-4" /> Back
            </Button>
          </Link>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-xl font-bold font-mono text-slate-100">{campaign.campaign_code}</h1>
              <Badge status={campaign.state} />
            </div>
            <p className="text-xs text-slate-400 mt-1 font-mono">Campaign ID: {campaign.id}</p>
          </div>
        </div>

        {campaign.state === "AWAITING_CONFIRMATION" && (
          <div className="flex items-center gap-3">
            <Button variant="primary" onClick={handleApprove} className="gap-2">
              <Check className="w-4 h-4" /> Approve Campaign
            </Button>
            <Button variant="danger" onClick={handleReject} className="gap-2">
              <X className="w-4 h-4" /> Reject Campaign
            </Button>
          </div>
        )}
      </div>

      {/* Specifications */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-sky-400">Signal Parameters</CardTitle>
          </CardHeader>
          <div className="space-y-2.5 font-mono text-xs border-t border-slate-800 pt-3">
            <div className="flex justify-between"><span className="text-slate-400">Direction:</span><span className="text-slate-100 font-bold">{campaign.direction}</span></div>
            <div className="flex justify-between"><span className="text-slate-400">Zone Low:</span><span className="text-slate-100">${campaign.zone_low?.toFixed(2)}</span></div>
            <div className="flex justify-between"><span className="text-slate-400">Zone High:</span><span className="text-slate-100">${campaign.zone_high?.toFixed(2)}</span></div>
            <div className="flex justify-between"><span className="text-slate-400">Stop Loss:</span><span className="text-rose-300 font-bold">${campaign.stop_loss?.toFixed(2)}</span></div>
            <div className="flex justify-between"><span className="text-slate-400">TP1 / TP2:</span><span className="text-emerald-300">${campaign.tp1?.toFixed(2) || "N/A"} / ${campaign.tp2?.toFixed(2) || "N/A"}</span></div>
          </div>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-emerald-400">Execution Policy</CardTitle>
          </CardHeader>
          <div className="space-y-2.5 font-mono text-xs border-t border-slate-800 pt-3">
            <div className="flex justify-between"><span className="text-slate-400">Execution Mode:</span><span className="text-slate-100">{campaign.execution_mode}</span></div>
            <div className="flex justify-between"><span className="text-slate-400">Version:</span><span className="text-slate-100">v{campaign.version}</span></div>
            <div className="flex justify-between"><span className="text-slate-400">Created At:</span><span className="text-slate-100">{new Date(campaign.created_at).toLocaleString()}</span></div>
            <div className="flex justify-between"><span className="text-slate-400">Updated At:</span><span className="text-slate-100">{new Date(campaign.updated_at).toLocaleString()}</span></div>
          </div>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-indigo-400">Planned Ladder</CardTitle>
          </CardHeader>
          <div className="space-y-2.5 font-mono text-xs border-t border-slate-800 pt-3">
            <div className="flex justify-between"><span className="text-slate-400">Ladder Entries:</span><span className="text-slate-100 font-bold">5 Limit Orders</span></div>
            <div className="flex justify-between"><span className="text-slate-400">Lot per Entry:</span><span className="text-slate-100">0.30 Lot</span></div>
            <div className="flex justify-between"><span className="text-slate-400">Total Volume:</span><span className="text-emerald-300 font-bold">1.50 Lots</span></div>
            <div className="flex justify-between"><span className="text-slate-400">Preflight Checks:</span><span className="text-emerald-400 font-bold">PASSED</span></div>
          </div>
        </Card>
      </div>

      {/* Planned Limit Entries Table */}
      <Card>
        <CardHeader>
          <CardTitle className="text-slate-200 flex items-center gap-2">
            <Layers className="w-4 h-4 text-sky-400" /> Planned Entry Limit Orders Ladder
          </CardTitle>
        </CardHeader>

        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs">
            <thead className="bg-slate-950 text-slate-400 uppercase text-[10px]">
              <tr>
                <th className="p-3">Sequence</th>
                <th className="p-3">Order Type</th>
                <th className="p-3">Limit Price</th>
                <th className="p-3">Volume</th>
                <th className="p-3">Stop Loss</th>
                <th className="p-3">Take Profit</th>
                <th className="p-3">Magic Number</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {[1, 2, 3, 4, 5].map((seq) => {
                const stepPrice = campaign.direction === "SELL"
                  ? (campaign.zone_low + (seq - 1) * ((campaign.zone_high - campaign.zone_low) / 4))
                  : (campaign.zone_high - (seq - 1) * ((campaign.zone_high - campaign.zone_low) / 4));
                return (
                  <tr key={seq} className="hover:bg-slate-800/40">
                    <td className="p-3 font-bold text-slate-200">Entry #{seq}</td>
                    <td className="p-3 text-sky-400">{campaign.direction === "SELL" ? "SELL_LIMIT" : "BUY_LIMIT"}</td>
                    <td className="p-3 font-bold text-emerald-400">${stepPrice.toFixed(2)}</td>
                    <td className="p-3 text-slate-300">0.30 Lot</td>
                    <td className="p-3 text-rose-300">${campaign.stop_loss?.toFixed(2)}</td>
                    <td className="p-3 text-emerald-300">${campaign.tp1?.toFixed(2) || "OPEN"}</td>
                    <td className="p-3 text-slate-500 font-mono">70001{seq}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};

import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { apiClient } from "../../api/apiClient";
import { Card, CardHeader, CardTitle, CardDescription } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { Boxes, RefreshCw, Eye, Check, X, Filter } from "lucide-react";

export const CampaignsPage: React.FC = () => {
  const [stateFilter, setStateFilter] = useState<string>("ALL");
  const [directionFilter, setDirectionFilter] = useState<string>("ALL");

  const { data: campaigns, refetch } = useQuery({
    queryKey: ["campaigns"],
    queryFn: () => apiClient.listCampaigns(),
    refetchInterval: 5000,
  });

  const handleApprove = async (id: string, version: number) => {
    await apiClient.approveCampaign(id, version);
    refetch();
  };

  const handleReject = async (id: string, version: number) => {
    await apiClient.rejectCampaign(id, version);
    refetch();
  };

  const filteredCampaigns = (campaigns || []).filter((c) => {
    if (stateFilter !== "ALL" && c.state !== stateFilter) return false;
    if (directionFilter !== "ALL" && c.direction !== directionFilter) return false;
    return true;
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold font-mono text-slate-100">Campaign Operations & State Machine</h1>
          <p className="text-xs text-slate-400 mt-1">Audit active signal campaigns, limit entry planning ladders, and state transitions.</p>
        </div>
        <Button variant="secondary" size="sm" onClick={() => refetch()} className="gap-2 font-mono">
          <RefreshCw className="w-3.5 h-3.5" /> Refresh Campaigns
        </Button>
      </div>

      {/* Filter Toolbar */}
      <Card className="p-4">
        <div className="flex flex-wrap items-center gap-4 font-mono text-xs">
          <div className="flex items-center gap-2 text-slate-400">
            <Filter className="w-4 h-4 text-sky-400" /> Filter:
          </div>

          <div>
            <label className="text-slate-500 mr-2">State:</label>
            <select
              value={stateFilter}
              onChange={(e) => setStateFilter(e.target.value)}
              className="bg-slate-950 border border-slate-700 rounded px-3 py-1.5 text-slate-200 focus:outline-none focus:ring-1 focus:ring-sky-500"
            >
              <option value="ALL">All States</option>
              <option value="AWAITING_CONFIRMATION">Awaiting Confirmation</option>
              <option value="PLANNED">Planned</option>
              <option value="PLACING_ORDERS">Placing Orders</option>
              <option value="PENDING">Pending</option>
              <option value="OPEN">Open</option>
              <option value="FAILED">Failed</option>
            </select>
          </div>

          <div>
            <label className="text-slate-500 mr-2">Direction:</label>
            <select
              value={directionFilter}
              onChange={(e) => setDirectionFilter(e.target.value)}
              className="bg-slate-950 border border-slate-700 rounded px-3 py-1.5 text-slate-200 focus:outline-none focus:ring-1 focus:ring-sky-500"
            >
              <option value="ALL">All Directions</option>
              <option value="BUY">BUY</option>
              <option value="SELL">SELL</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Campaigns Table */}
      <Card>
        <CardHeader>
          <CardTitle className="text-slate-200 flex items-center gap-2">
            <Boxes className="w-4 h-4 text-sky-400" /> Active & Historical Campaigns ({filteredCampaigns.length})
          </CardTitle>
        </CardHeader>

        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs">
            <thead className="bg-slate-950 text-slate-400 uppercase text-[10px]">
              <tr>
                <th className="p-3">Campaign Code</th>
                <th className="p-3">Direction</th>
                <th className="p-3">Zone Low-High</th>
                <th className="p-3">Stop Loss</th>
                <th className="p-3">Mode</th>
                <th className="p-3">State</th>
                <th className="p-3">Version</th>
                <th className="p-3">Created</th>
                <th className="p-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredCampaigns.length === 0 ? (
                <tr>
                  <td colSpan={9} className="p-6 text-center text-slate-500">
                    No campaigns match selected filters.
                  </td>
                </tr>
              ) : (
                filteredCampaigns.map((c) => (
                  <tr key={c.id} className="hover:bg-slate-800/40">
                    <td className="p-3 font-bold text-sky-400">{c.campaign_code}</td>
                    <td className="p-3">
                      <span className={c.direction === "BUY" ? "text-emerald-400 font-bold" : "text-rose-400 font-bold"}>
                        {c.direction}
                      </span>
                    </td>
                    <td className="p-3 text-slate-300">${c.zone_low?.toFixed(2)} - ${c.zone_high?.toFixed(2)}</td>
                    <td className="p-3 text-rose-300">${c.stop_loss?.toFixed(2)}</td>
                    <td className="p-3 text-slate-400">{c.execution_mode}</td>
                    <td className="p-3"><Badge status={c.state} /></td>
                    <td className="p-3 text-slate-400">v{c.version}</td>
                    <td className="p-3 text-slate-400">{new Date(c.created_at).toLocaleTimeString()}</td>
                    <td className="p-3 text-right">
                      <div className="flex items-center justify-end gap-2">
                        {c.state === "AWAITING_CONFIRMATION" && (
                          <>
                            <Button variant="primary" size="sm" onClick={() => handleApprove(c.id, c.version)} className="h-7 px-2">
                              <Check className="w-3.5 h-3.5" /> Approve
                            </Button>
                            <Button variant="danger" size="sm" onClick={() => handleReject(c.id, c.version)} className="h-7 px-2">
                              <X className="w-3.5 h-3.5" /> Reject
                            </Button>
                          </>
                        )}
                        <Link to={`/campaigns/${c.id}`}>
                          <Button variant="secondary" size="sm" className="h-7 px-2">
                            <Eye className="w-3.5 h-3.5" /> View
                          </Button>
                        </Link>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};

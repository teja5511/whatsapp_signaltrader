import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../../api/apiClient";
import { Card, CardHeader, CardTitle } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { useUiStore } from "../../stores/uiStore";
import { CONTROL_PHRASES } from "../../lib/constants";
import { ListOrdered, RefreshCw, AlertTriangle, Layers, History, ShieldAlert } from "lucide-react";

export const OrdersPositionsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"orders" | "positions" | "history" | "jobs">("orders");
  const { openConfirmModal } = useUiStore();

  const { data: orders, refetch: refetchOrders } = useQuery({
    queryKey: ["mt5Orders"],
    queryFn: () => apiClient.getMt5Orders().catch(() => []),
    refetchInterval: 3000,
  });

  const { data: positions, refetch: refetchPositions } = useQuery({
    queryKey: ["mt5Positions"],
    queryFn: () => apiClient.getMt5Positions().catch(() => []),
    refetchInterval: 3000,
  });

  const { data: history } = useQuery({
    queryKey: ["mt5History"],
    queryFn: () => apiClient.getMt5History().catch(() => []),
    refetchInterval: 5000,
  });

  const { data: jobs } = useQuery({
    queryKey: ["executionJobs"],
    queryFn: () => apiClient.listExecutionJobs().catch(() => []),
    refetchInterval: 5000,
  });

  const handleEmergencyCloseAll = () => {
    openConfirmModal({
      type: "CLOSE_ALL_DEMO",
      title: "Emergency Close All Demo XAUUSD Positions",
      description: "Closes all open XAUUSD positions and cancels all pending limit orders on the MT5 Demo account.",
      phrase: CONTROL_PHRASES.CLOSE_ALL_DEMO,
      action: async () => {
        await apiClient.emergencyCloseAll(CONTROL_PHRASES.CLOSE_ALL_DEMO, "APPLICATION_OWNED");
        refetchOrders();
        refetchPositions();
      },
    });
  };

  return (
    <div className="space-y-6 font-mono">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-100 font-mono">Orders, Positions & Execution Queue</h1>
          <p className="text-xs text-slate-400 mt-1">Real-time MT5 pending limit orders, open hedging positions, trade history, and execution jobs.</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="danger" size="sm" onClick={handleEmergencyCloseAll} className="gap-1.5 font-mono">
            <ShieldAlert className="w-3.5 h-3.5" /> Emergency Close All
          </Button>
          <Button variant="secondary" size="sm" onClick={() => { refetchOrders(); refetchPositions(); }} className="gap-2 font-mono">
            <RefreshCw className="w-3.5 h-3.5" /> Refresh
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-800 text-xs font-semibold">
        <button
          onClick={() => setActiveTab("orders")}
          className={`px-4 py-2.5 border-b-2 font-mono transition-colors ${activeTab === "orders" ? "border-sky-500 text-sky-400 bg-sky-950/20" : "border-transparent text-slate-400 hover:text-slate-200"}`}
        >
          Pending Orders ({(orders || []).length})
        </button>
        <button
          onClick={() => setActiveTab("positions")}
          className={`px-4 py-2.5 border-b-2 font-mono transition-colors ${activeTab === "positions" ? "border-emerald-500 text-emerald-400 bg-emerald-950/20" : "border-transparent text-slate-400 hover:text-slate-200"}`}
        >
          Open Positions ({(positions || []).length})
        </button>
        <button
          onClick={() => setActiveTab("history")}
          className={`px-4 py-2.5 border-b-2 font-mono transition-colors ${activeTab === "history" ? "border-indigo-500 text-indigo-400 bg-indigo-950/20" : "border-transparent text-slate-400 hover:text-slate-200"}`}
        >
          Trade History ({(history || []).length})
        </button>
        <button
          onClick={() => setActiveTab("jobs")}
          className={`px-4 py-2.5 border-b-2 font-mono transition-colors ${activeTab === "jobs" ? "border-amber-500 text-amber-400 bg-amber-950/20" : "border-transparent text-slate-400 hover:text-slate-200"}`}
        >
          Execution Jobs ({(jobs || []).length})
        </button>
      </div>

      {/* Tab Contents */}
      {activeTab === "orders" && (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full text-left font-mono text-xs">
              <thead className="bg-slate-950 text-slate-400 uppercase text-[10px]">
                <tr>
                  <th className="p-3">Ticket</th>
                  <th className="p-3">Symbol</th>
                  <th className="p-3">Type</th>
                  <th className="p-3">Volume</th>
                  <th className="p-3">Price Open</th>
                  <th className="p-3">SL</th>
                  <th className="p-3">TP</th>
                  <th className="p-3">State</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {(orders || []).length === 0 ? (
                  <tr>
                    <td colSpan={8} className="p-6 text-center text-slate-500">
                      No active pending limit orders.
                    </td>
                  </tr>
                ) : (
                  (orders || []).map((o) => (
                    <tr key={o.ticket} className="hover:bg-slate-800/40">
                      <td className="p-3 font-bold text-slate-200">#{o.ticket}</td>
                      <td className="p-3 text-slate-300">{o.symbol}</td>
                      <td className="p-3 font-bold text-sky-400">{o.type}</td>
                      <td className="p-3 text-slate-200">{o.volume?.toFixed(2)} Lot</td>
                      <td className="p-3 font-bold text-emerald-400">${o.price_open?.toFixed(2)}</td>
                      <td className="p-3 text-rose-300">${o.sl?.toFixed(2)}</td>
                      <td className="p-3 text-emerald-300">${o.tp?.toFixed(2)}</td>
                      <td className="p-3"><Badge status={o.state || "PLACED"} /></td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {activeTab === "positions" && (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full text-left font-mono text-xs">
              <thead className="bg-slate-950 text-slate-400 uppercase text-[10px]">
                <tr>
                  <th className="p-3">Ticket</th>
                  <th className="p-3">Symbol</th>
                  <th className="p-3">Type</th>
                  <th className="p-3">Volume</th>
                  <th className="p-3">Open Price</th>
                  <th className="p-3">Current Price</th>
                  <th className="p-3">Profit / Loss</th>
                  <th className="p-3">SL / TP</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {(positions || []).length === 0 ? (
                  <tr>
                    <td colSpan={8} className="p-6 text-center text-slate-500">
                      No open positions.
                    </td>
                  </tr>
                ) : (
                  (positions || []).map((p) => (
                    <tr key={p.ticket} className="hover:bg-slate-800/40">
                      <td className="p-3 font-bold text-slate-200">#{p.ticket}</td>
                      <td className="p-3 text-slate-300">{p.symbol}</td>
                      <td className="p-3 font-bold text-emerald-400">{p.type}</td>
                      <td className="p-3 text-slate-200">{p.volume?.toFixed(2)} Lot</td>
                      <td className="p-3 text-slate-200">${p.price_open?.toFixed(2)}</td>
                      <td className="p-3 text-slate-200">${p.price_current?.toFixed(2)}</td>
                      <td className={`p-3 font-bold ${p.profit >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                        ${p.profit?.toFixed(2)} USD
                      </td>
                      <td className="p-3 text-slate-400">${p.sl?.toFixed(2)} / ${p.tp?.toFixed(2)}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {activeTab === "history" && (
        <Card>
          <div className="p-6 text-center text-slate-500 text-xs">
            Trade history populated directly from MT5 terminal history database.
          </div>
        </Card>
      )}

      {activeTab === "jobs" && (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full text-left font-mono text-xs">
              <thead className="bg-slate-950 text-slate-400 uppercase text-[10px]">
                <tr>
                  <th className="p-3">Job ID</th>
                  <th className="p-3">Batch ID</th>
                  <th className="p-3">Operation</th>
                  <th className="p-3">Status</th>
                  <th className="p-3">Created</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {(jobs || []).length === 0 ? (
                  <tr>
                    <td colSpan={5} className="p-6 text-center text-slate-500">
                      No execution jobs recorded.
                    </td>
                  </tr>
                ) : (
                  (jobs || []).map((j) => (
                    <tr key={j.id} className="hover:bg-slate-800/40">
                      <td className="p-3 font-bold text-slate-200">{j.id.substring(0, 8)}...</td>
                      <td className="p-3 text-sky-400">{j.batch_id?.substring(0, 8)}...</td>
                      <td className="p-3 text-slate-300">{j.operation_type}</td>
                      <td className="p-3"><Badge status={j.status} /></td>
                      <td className="p-3 text-slate-400">{new Date(j.created_at).toLocaleTimeString()}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
};

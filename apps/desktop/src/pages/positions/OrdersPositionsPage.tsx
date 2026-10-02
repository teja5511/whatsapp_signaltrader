import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../../api/apiClient";
import { Card } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { useUiStore } from "../../stores/uiStore";
import { CONTROL_PHRASES } from "../../lib/constants";
import { RefreshCw, ShieldAlert } from "lucide-react";

function asNumber(value: unknown): number | null {
  if (value == null || value === "") return null;
  const n = typeof value === "number" ? value : Number(value);
  return Number.isFinite(n) ? n : null;
}

function formatAmount(value: unknown, digits = 2): string {
  const n = asNumber(value);
  return n == null ? "-" : n.toFixed(digits);
}

function asList<T>(value: unknown): T[] {
  return Array.isArray(value) ? value : [];
}

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

  const orderRows = asList<any>(orders);
  const positionRows = asList<any>(positions);
  const historyRows = asList<any>(history);
  const jobRows = asList<any>(jobs);

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
          Pending Orders ({orderRows.length})
        </button>
        <button
          onClick={() => setActiveTab("positions")}
          className={`px-4 py-2.5 border-b-2 font-mono transition-colors ${activeTab === "positions" ? "border-emerald-500 text-emerald-400 bg-emerald-950/20" : "border-transparent text-slate-400 hover:text-slate-200"}`}
        >
          Open Positions ({positionRows.length})
        </button>
        <button
          onClick={() => setActiveTab("history")}
          className={`px-4 py-2.5 border-b-2 font-mono transition-colors ${activeTab === "history" ? "border-indigo-500 text-indigo-400 bg-indigo-950/20" : "border-transparent text-slate-400 hover:text-slate-200"}`}
        >
          Trade History ({historyRows.length})
        </button>
        <button
          onClick={() => setActiveTab("jobs")}
          className={`px-4 py-2.5 border-b-2 font-mono transition-colors ${activeTab === "jobs" ? "border-amber-500 text-amber-400 bg-amber-950/20" : "border-transparent text-slate-400 hover:text-slate-200"}`}
        >
          Execution Jobs ({jobRows.length})
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
                {orderRows.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="p-6 text-center text-slate-500">
                      No active pending orders.
                    </td>
                  </tr>
                ) : (
                  orderRows.map((o) => (
                    <tr key={o.ticket} className="hover:bg-slate-800/40">
                      <td className="p-3 font-bold text-slate-200">#{o.ticket}</td>
                      <td className="p-3 text-slate-300">{o.symbol}</td>
                      <td className="p-3 font-bold text-sky-400">{o.type || o.order_type}</td>
                      <td className="p-3 text-slate-200">{formatAmount(o.volume)} Lot</td>
                      <td className="p-3 font-bold text-emerald-400">${formatAmount(o.price_open ?? o.price)}</td>
                      <td className="p-3 text-rose-300">${formatAmount(o.sl ?? o.stop_loss)}</td>
                      <td className="p-3 text-emerald-300">${formatAmount(o.tp ?? o.take_profit)}</td>
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
                {positionRows.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="p-6 text-center text-slate-500">
                      No open positions.
                    </td>
                  </tr>
                ) : (
                  positionRows.map((p) => {
                    const profit = asNumber(p.profit) ?? 0;
                    return (
                    <tr key={p.ticket} className="hover:bg-slate-800/40">
                      <td className="p-3 font-bold text-slate-200">#{p.ticket}</td>
                      <td className="p-3 text-slate-300">{p.symbol}</td>
                      <td className="p-3 font-bold text-emerald-400">{p.type || p.position_type}</td>
                      <td className="p-3 text-slate-200">{formatAmount(p.volume)} Lot</td>
                      <td className="p-3 text-slate-200">${formatAmount(p.price_open ?? p.price)}</td>
                      <td className="p-3 text-slate-200">${formatAmount(p.price_current)}</td>
                      <td className={`p-3 font-bold ${profit >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                        ${formatAmount(profit)} USD
                      </td>
                      <td className="p-3 text-slate-400">${formatAmount(p.sl ?? p.stop_loss)} / ${formatAmount(p.tp ?? p.take_profit)}</td>
                    </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {activeTab === "history" && (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full text-left font-mono text-xs">
              <thead className="bg-slate-950 text-slate-400 uppercase text-[10px]">
                <tr>
                  <th className="p-3">Ticket</th>
                  <th className="p-3">Symbol</th>
                  <th className="p-3">Type</th>
                  <th className="p-3">Volume</th>
                  <th className="p-3">Price</th>
                  <th className="p-3">State</th>
                  <th className="p-3">Comment</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {historyRows.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="p-6 text-center text-slate-500">
                      No trade history yet.
                    </td>
                  </tr>
                ) : (
                  historyRows.map((h) => (
                    <tr key={h.ticket} className="hover:bg-slate-800/40">
                      <td className="p-3 font-bold text-slate-200">#{h.ticket}</td>
                      <td className="p-3 text-slate-300">{h.symbol}</td>
                      <td className="p-3 text-sky-400">{h.order_type || h.type}</td>
                      <td className="p-3">{formatAmount(h.volume)}</td>
                      <td className="p-3">${formatAmount(h.price ?? h.price_open)}</td>
                      <td className="p-3"><Badge status={h.state || "HISTORY"} /></td>
                      <td className="p-3 text-slate-400">{h.comment || "-"}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
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
                {jobRows.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="p-6 text-center text-slate-500">
                      No execution jobs recorded.
                    </td>
                  </tr>
                ) : (
                  jobRows.map((j) => (
                    <tr key={j.id} className="hover:bg-slate-800/40">
                      <td className="p-3 font-bold text-slate-200">{String(j.id).slice(0, 8)}...</td>
                      <td className="p-3 text-sky-400">{j.batch_id ? String(j.batch_id).slice(0, 8) : "-"}...</td>
                      <td className="p-3 text-slate-300">{j.operation_type}</td>
                      <td className="p-3"><Badge status={j.status} /></td>
                      <td className="p-3 text-slate-400">{j.created_at ? new Date(j.created_at).toLocaleTimeString() : "-"}</td>
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

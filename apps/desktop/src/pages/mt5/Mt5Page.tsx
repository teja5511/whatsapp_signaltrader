import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../../api/apiClient";
import { Card, CardHeader, CardTitle, CardDescription } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { useUiStore } from "../../stores/uiStore";
import { CONTROL_PHRASES } from "../../lib/constants";
import { TrendingUp, RefreshCw, Power, Lock, CheckCircle2, DollarSign, Wallet, Layers, AlertOctagon, XCircle, ArrowUpRight, ArrowDownRight } from "lucide-react";

export const Mt5Page: React.FC = () => {
  const { openConfirmModal } = useUiStore();
  const [closingTicket, setClosingTicket] = useState<string | null>(null);

  const { data: status, refetch: refetchStatus } = useQuery({
    queryKey: ["mt5Status"],
    queryFn: () => apiClient.getMt5Status().catch(() => ({ initialized: false, adapter_mode: "fake" })),
    refetchInterval: 3000,
  });

  const { data: account, refetch: refetchAccount } = useQuery({
    queryKey: ["mt5Account"],
    queryFn: () => apiClient.getMt5Account().catch(() => null),
    refetchInterval: 3000,
  });

  const { data: symbol } = useQuery({
    queryKey: ["mt5Symbol"],
    queryFn: () => apiClient.getMt5Symbol().catch(() => null),
    refetchInterval: 5000,
  });

  const { data: positions, refetch: refetchPositions } = useQuery({
    queryKey: ["mt5Positions"],
    queryFn: () => apiClient.getMt5Positions().catch(() => []),
    refetchInterval: 3000,
  });

  const { data: orders, refetch: refetchOrders } = useQuery({
    queryKey: ["mt5Orders"],
    queryFn: () => apiClient.getMt5Orders().catch(() => []),
    refetchInterval: 3000,
  });

  const { data: batches, refetch: refetchBatches } = useQuery({
    queryKey: ["executionBatches"],
    queryFn: () => apiClient.getExecutionBatches().catch(() => []),
    refetchInterval: 3000,
  });

  const handleInitialize = async () => {
    await apiClient.initializeMt5();
    refetchStatus();
    refetchAccount();
  };

  const handleShutdown = async () => {
    await apiClient.shutdownMt5();
    refetchStatus();
    refetchAccount();
  };

  const handleEmergencyCloseAll = () => {
    openConfirmModal({
      type: "CLOSE_ALL_DEMO",
      title: "Emergency Flatten All Positions",
      description: "Immediately closes all open XAUUSD positions and cancels pending limit orders.",
      phrase: CONTROL_PHRASES.CLOSE_ALL_DEMO,
      action: async () => {
        await apiClient.emergencyCloseAll(CONTROL_PHRASES.CLOSE_ALL_DEMO);
        refetchPositions();
        refetchOrders();
        refetchAccount();
      },
    });
  };

  const handleRefreshAll = () => {
    refetchStatus();
    refetchAccount();
    refetchPositions();
    refetchOrders();
    refetchBatches();
  };

  // Portfolio math calculation
  const totalProfit = (positions || []).reduce((acc: number, p: any) => acc + (p.profit || 0), 0);
  const totalVolume = (positions || []).reduce((acc: number, p: any) => acc + (p.volume || 0), 0);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold font-mono text-slate-100">MetaTrader 5 Account & Portfolio</h1>
          <p className="text-xs text-slate-400 mt-1">Live portfolio stats, active trades, pending limit orders, and execution batch queue.</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="danger" size="sm" onClick={handleEmergencyCloseAll} className="gap-1.5 font-mono">
            <AlertOctagon className="w-3.5 h-3.5" /> Emergency Flatten All
          </Button>
          <Button variant="secondary" size="sm" onClick={handleRefreshAll} className="gap-2 font-mono">
            <RefreshCw className="w-3.5 h-3.5" /> Refresh All
          </Button>
        </div>
      </div>

      {/* Portfolio Quick Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 font-mono">
        <Card className="p-4">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Balance</span>
            <DollarSign className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-xl font-bold text-slate-100 mt-2">
            ${(account?.balance || 10000.00).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <span className="text-[11px] text-slate-500 mt-1 block">Account Deposit</span>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Equity</span>
            <Wallet className="w-4 h-4 text-sky-400" />
          </div>
          <div className="text-xl font-bold text-sky-400 mt-2">
            ${(account?.equity || 10000.00).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <span className="text-[11px] text-slate-500 mt-1 block">Real-time Net Equity</span>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Open Floating P&L</span>
            <TrendingUp className={`w-4 h-4 ${totalProfit >= 0 ? "text-emerald-400" : "text-rose-400"}`} />
          </div>
          <div className={`text-xl font-bold mt-2 ${totalProfit >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
            {totalProfit >= 0 ? "+" : ""}${totalProfit.toFixed(2)} USD
          </div>
          <span className="text-[11px] text-slate-500 mt-1 block">{positions?.length || 0} active positions</span>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Total Exposure</span>
            <Layers className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-xl font-bold text-amber-300 mt-2">
            {totalVolume.toFixed(2)} / 2.00 Lots
          </div>
          <span className="text-[11px] text-slate-500 mt-1 block">Max Exposure Limit</span>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Adapter Status & Controls */}
        <Card>
          <CardHeader>
            <div>
              <CardTitle className="flex items-center gap-2 text-sky-400">
                <TrendingUp className="w-4 h-4" /> MT5 IPC Adapter
              </CardTitle>
              <CardDescription>Python `MetaTrader5` Binding</CardDescription>
            </div>
            <Badge status={status?.initialized ? "INITIALIZED" : "UNINITIALIZED"} />
          </CardHeader>

          <div className="space-y-3 font-mono text-xs border-t border-slate-800 pt-4">
            <div className="flex justify-between">
              <span className="text-slate-400">Adapter Mode:</span>
              <span className="text-slate-200 uppercase font-bold">{status?.adapter_mode || "fake"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Health State:</span>
              <span className="text-emerald-400 font-bold">{status?.health_state || "READY"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Environment:</span>
              <span className="text-emerald-300 font-bold">DEMO ONLY</span>
            </div>
          </div>

          <div className="mt-6 flex gap-3 border-t border-slate-800 pt-4">
            {status?.initialized ? (
              <Button variant="secondary" size="sm" onClick={handleShutdown} className="w-full gap-2">
                <Power className="w-4 h-4 text-rose-400" /> Shutdown IPC
              </Button>
            ) : (
              <Button variant="primary" size="sm" onClick={handleInitialize} className="w-full gap-2">
                <Power className="w-4 h-4 text-emerald-400" /> Initialize IPC
              </Button>
            )}
          </div>
        </Card>

        {/* Account Info */}
        <Card>
          <CardHeader>
            <div>
              <CardTitle className="flex items-center gap-2 text-emerald-400">
                <Lock className="w-4 h-4" /> Account Specifications
              </CardTitle>
              <CardDescription>Exness Demo Account Details</CardDescription>
            </div>
            <Badge status="DEMO" variant="green" />
          </CardHeader>

          <div className="space-y-3 font-mono text-xs border-t border-slate-800 pt-4">
            <div className="flex justify-between">
              <span className="text-slate-400">Login Masked:</span>
              <span className="text-slate-200">{account?.login_masked || "*****5678"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Server:</span>
              <span className="text-slate-200">{account?.server || "Exness-MT5Demo"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Free Margin:</span>
              <span className="text-emerald-400 font-bold">${(account?.margin_free || account?.balance || 10000.00).toFixed(2)} USD</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Leverage / Mode:</span>
              <span className="text-slate-200">1:{account?.leverage || 500} (Hedging)</span>
            </div>
          </div>
        </Card>

        {/* Symbol Specification */}
        <Card>
          <CardHeader>
            <div>
              <CardTitle className="flex items-center gap-2 text-indigo-400">
                <CheckCircle2 className="w-4 h-4" /> Symbol Specifications
              </CardTitle>
              <CardDescription>XAUUSD Contract Rules</CardDescription>
            </div>
            <Badge status="XAUUSD" variant="blue" />
          </CardHeader>

          <div className="space-y-3 font-mono text-xs border-t border-slate-800 pt-4">
            <div className="flex justify-between">
              <span className="text-slate-400">Canonical Symbol:</span>
              <span className="text-slate-200 font-bold">XAUUSD</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Broker Symbol:</span>
              <span className="text-slate-200">{symbol?.broker_symbol || "XAUUSDm"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Digits / Point:</span>
              <span className="text-slate-200">{symbol?.digits || 2} / {symbol?.point || 0.01}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Volume Limits:</span>
              <span className="text-slate-200">0.01 Min / 2.00 Max</span>
            </div>
          </div>
        </Card>
      </div>

      {/* Active Open Trades / Positions */}
      <Card>
        <CardHeader>
          <CardTitle className="text-emerald-400 flex items-center gap-2">
            <TrendingUp className="w-4 h-4" /> Open Positions ({positions?.length || 0})
          </CardTitle>
          <CardDescription>Live MT5 open trades executing on your account.</CardDescription>
        </CardHeader>

        <div className="overflow-x-auto font-mono text-xs">
          <table className="w-full text-left border-collapse">
            <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] border-b border-slate-800">
              <tr>
                <th className="p-3">Ticket</th>
                <th className="p-3">Symbol</th>
                <th className="p-3">Type</th>
                <th className="p-3">Volume</th>
                <th className="p-3">Open Price</th>
                <th className="p-3">Current Price</th>
                <th className="p-3">Stop Loss</th>
                <th className="p-3">Take Profit</th>
                <th className="p-3">Profit ($)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {(positions || []).length === 0 ? (
                <tr>
                  <td colSpan={9} className="p-6 text-center text-slate-500">
                    No active open positions.
                  </td>
                </tr>
              ) : (
                (positions || []).map((p: any) => (
                  <tr key={p.ticket || p.id} className="hover:bg-slate-900/50">
                    <td className="p-3 text-slate-300 font-bold">#{p.ticket || p.id}</td>
                    <td className="p-3 font-bold text-sky-400">{p.symbol || "XAUUSD"}</td>
                    <td className="p-3 font-bold">
                      <span className={`px-2 py-0.5 rounded text-[10px] ${p.type === "BUY" ? "bg-emerald-950 text-emerald-300 border border-emerald-800" : "bg-rose-950 text-rose-300 border border-rose-800"}`}>
                        {p.type === "BUY" ? <ArrowUpRight className="w-3 h-3 inline mr-0.5" /> : <ArrowDownRight className="w-3 h-3 inline mr-0.5" />}
                        {p.type}
                      </span>
                    </td>
                    <td className="p-3 text-slate-200">{p.volume?.toFixed(2)} Lots</td>
                    <td className="p-3 text-slate-200">{p.price_open?.toFixed(2)}</td>
                    <td className="p-3 text-slate-200">{p.price_current?.toFixed(2) || p.price_open?.toFixed(2)}</td>
                    <td className="p-3 text-rose-400 font-semibold">{p.sl?.toFixed(2) || "-"}</td>
                    <td className="p-3 text-emerald-400 font-semibold">{p.tp?.toFixed(2) || "-"}</td>
                    <td className={`p-3 font-bold ${(p.profit || 0) >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                      {(p.profit || 0) >= 0 ? "+" : ""}${(p.profit || 0).toFixed(2)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Pending Limit Orders */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sky-400 flex items-center gap-2">
            <Layers className="w-4 h-4" /> Pending Orders ({orders?.length || 0})
          </CardTitle>
          <CardDescription>Laddered limit orders queued in MetaTrader 5.</CardDescription>
        </CardHeader>

        <div className="overflow-x-auto font-mono text-xs">
          <table className="w-full text-left border-collapse">
            <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] border-b border-slate-800">
              <tr>
                <th className="p-3">Ticket</th>
                <th className="p-3">Order Type</th>
                <th className="p-3">Volume</th>
                <th className="p-3">Setup Price</th>
                <th className="p-3">Stop Loss</th>
                <th className="p-3">Take Profit</th>
                <th className="p-3">State</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {(orders || []).length === 0 ? (
                <tr>
                  <td colSpan={7} className="p-6 text-center text-slate-500">
                    No pending limit orders queued.
                  </td>
                </tr>
              ) : (
                (orders || []).map((o: any) => (
                  <tr key={o.ticket || o.id} className="hover:bg-slate-900/50">
                    <td className="p-3 text-slate-300 font-bold">#{o.ticket || o.id}</td>
                    <td className="p-3 font-bold text-amber-400">{o.type}</td>
                    <td className="p-3 text-slate-200">{o.volume?.toFixed(2)} Lots</td>
                    <td className="p-3 text-slate-200 font-bold">{o.price_setup?.toFixed(2)}</td>
                    <td className="p-3 text-rose-400 font-semibold">{o.sl?.toFixed(2) || "-"}</td>
                    <td className="p-3 text-emerald-400 font-semibold">{o.tp?.toFixed(2) || "-"}</td>
                    <td className="p-3"><Badge status={o.state || "PLACED"} /></td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Execution Batches Queue */}
      <Card>
        <CardHeader>
          <CardTitle className="text-slate-200">MT5 Execution Batch Queue</CardTitle>
          <CardDescription>Durable single-writer execution queue processing limit order submissions.</CardDescription>
        </CardHeader>

        <div className="overflow-x-auto font-mono text-xs">
          <table className="w-full text-left border-collapse">
            <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] border-b border-slate-800">
              <tr>
                <th className="p-3">Batch ID</th>
                <th className="p-3">Campaign ID</th>
                <th className="p-3">Status</th>
                <th className="p-3">Total Jobs</th>
                <th className="p-3">Completed</th>
                <th className="p-3">Failed</th>
                <th className="p-3">Created</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {(batches || []).length === 0 ? (
                <tr>
                  <td colSpan={7} className="p-4 text-center text-slate-500">
                    No execution batches queued.
                  </td>
                </tr>
              ) : (
                (batches || []).map((b: any) => (
                  <tr key={b.id} className="hover:bg-slate-800/40">
                    <td className="p-3 font-semibold text-slate-200">{b.id?.substring(0, 8)}...</td>
                    <td className="p-3 text-sky-400">{b.campaign_id?.substring(0, 8)}...</td>
                    <td className="p-3"><Badge status={b.status} /></td>
                    <td className="p-3 text-slate-300">{b.total_jobs}</td>
                    <td className="p-3 text-emerald-400">{b.completed_jobs}</td>
                    <td className="p-3 text-rose-400">{b.failed_jobs}</td>
                    <td className="p-3 text-slate-400">{new Date(b.created_at).toLocaleTimeString()}</td>
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

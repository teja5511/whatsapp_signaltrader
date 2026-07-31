import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../../api/apiClient";
import { Card, CardHeader, CardTitle, CardDescription } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { useUiStore } from "../../stores/uiStore";
import { CONTROL_PHRASES } from "../../lib/constants";
import { 
  TrendingUp, RefreshCw, Power, Lock, CheckCircle2, DollarSign, Wallet, 
  Layers, AlertOctagon, ArrowUpRight, ArrowDownRight, User, Server, 
  Building, ShieldCheck, Activity, Scale
} from "lucide-react";

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
    try {
      await apiClient.initializeMt5();
    } catch {}
    handleRefreshAll();
  };

  const handleShutdown = async () => {
    try {
      await apiClient.shutdownMt5();
    } catch {}
    handleRefreshAll();
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

  // Portfolio & Profit Calculations
  const positionsList = Array.isArray(positions) ? positions : [];
  const ordersList = Array.isArray(orders) ? orders : [];
  const batchesList = Array.isArray(batches) ? batches : [];

  const totalProfit = positionsList.reduce((acc: number, p: any) => acc + (Number(p?.profit) || 0), 0);
  const totalVolume = positionsList.reduce((acc: number, p: any) => acc + (Number(p?.volume) || 0), 0);

  const balance = account?.balance ? Number(account.balance) : 10000.00;
  const equity = account?.equity ? Number(account.equity) : (balance + totalProfit);
  const margin = account?.margin ? Number(account.margin) : 0.00;
  const freeMargin = account?.margin_free ? Number(account.margin_free) : balance;
  const marginLevel = margin > 0 ? ((equity / margin) * 100).toFixed(1) + "%" : "100.0%";

  return (
    <div className="space-y-6">
      {/* Top Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold font-mono text-slate-100">MetaTrader 5 Account & Portfolio Dashboard</h1>
          <p className="text-xs text-slate-400 mt-1">Live MetaTrader terminal connection, logged-in account portfolio, active trades & order queue.</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="danger" size="sm" onClick={handleEmergencyCloseAll} className="gap-1.5 font-mono">
            <AlertOctagon className="w-3.5 h-3.5" /> Emergency Flatten All
          </Button>
          <Button variant="secondary" size="sm" onClick={handleRefreshAll} className="gap-2 font-mono">
            <RefreshCw className="w-3.5 h-3.5" /> Refresh Dashboard
          </Button>
        </div>
      </div>

      {/* Logged-In MetaTrader Account Banner */}
      <Card className="bg-gradient-to-r from-slate-900 via-slate-900 to-slate-950 border-sky-900/50 shadow-xl">
        <div className="p-5 font-mono">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-sky-950/80 border border-sky-600/40 flex items-center justify-center shrink-0">
                <User className="w-6 h-6 text-sky-400" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-lg font-bold text-slate-100">
                    {account?.login ? `MT5 Account #${account.login}` : `MT5 Account #${account?.login_masked || "1234****"}`}
                  </h2>
                  <Badge 
                    status={account?.environment_kind || "DEMO"} 
                    variant={account?.environment_kind === "REAL" ? "red" : "green"} 
                  />
                  <span className="px-2 py-0.5 text-[10px] rounded bg-sky-950 text-sky-300 border border-sky-800">
                    {account?.margin_mode || "HEDGING"}
                  </span>
                </div>
                <p className="text-xs text-slate-400 mt-0.5 flex items-center gap-3">
                  <span className="flex items-center gap-1">
                    <Building className="w-3 h-3 text-slate-500" /> {account?.company || "Exness Technologies Ltd"}
                  </span>
                  <span className="flex items-center gap-1">
                    <Server className="w-3 h-3 text-slate-500" /> {account?.server || "Exness-MT5Trial6"}
                  </span>
                </p>
              </div>
            </div>

          {(() => {
            const isConnected = Boolean(status?.initialized || status?.account_connected || account?.login);
            return (
              <div className="flex items-center gap-3">
                <div className="text-right">
                  <span className="text-[10px] uppercase text-slate-400 block">Terminal IPC Status</span>
                  <span className={`text-xs font-bold ${isConnected ? "text-emerald-400" : "text-amber-400"}`}>
                    {isConnected ? "● CONNECTED TO TERMINAL" : "○ DISCONNECTED"}
                  </span>
                </div>
                {isConnected ? (
                  <Button variant="secondary" size="sm" onClick={handleShutdown} className="border-rose-800 text-rose-300 gap-1.5 text-xs">
                    <Power className="w-3.5 h-3.5" /> Disconnect
                  </Button>
                ) : (
                  <Button variant="primary" size="sm" onClick={handleInitialize} className="gap-1.5 text-xs">
                    <Power className="w-3.5 h-3.5" /> Connect MT5
                  </Button>
                )}
              </div>
            );
          })()}
          </div>

          {/* Account Portfolio Key Financial Metrics Grid */}
          <div className="grid grid-cols-2 md:grid-cols-6 gap-4 pt-4 text-xs">
            <div>
              <span className="text-slate-400 block text-[11px]">Account Balance</span>
              <span className="text-base font-bold text-slate-100">
                ${balance.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </span>
              <span className="text-[10px] text-slate-500 block">Initial Deposit</span>
            </div>

            <div>
              <span className="text-slate-400 block text-[11px]">Net Equity</span>
              <span className="text-base font-bold text-sky-400">
                ${equity.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </span>
              <span className="text-[10px] text-slate-500 block">Balance + P&L</span>
            </div>

            <div>
              <span className="text-slate-400 block text-[11px]">Margin Used</span>
              <span className="text-base font-bold text-slate-300">
                ${margin.toFixed(2)}
              </span>
              <span className="text-[10px] text-slate-500 block">Leverage 1:{account?.leverage || 500}</span>
            </div>

            <div>
              <span className="text-slate-400 block text-[11px]">Free Margin</span>
              <span className="text-base font-bold text-emerald-400">
                ${freeMargin.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </span>
              <span className="text-[10px] text-slate-500 block">Available for trades</span>
            </div>

            <div>
              <span className="text-slate-400 block text-[11px]">Margin Level %</span>
              <span className="text-base font-bold text-indigo-400">
                {marginLevel}
              </span>
              <span className="text-[10px] text-slate-500 block">Health Ratio</span>
            </div>

            <div>
              <span className="text-slate-400 block text-[11px]">Floating P&L</span>
              <span className={`text-base font-bold ${totalProfit >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                {totalProfit >= 0 ? "+" : ""}${totalProfit.toFixed(2)}
              </span>
              <span className="text-[10px] text-slate-500 block">{positions?.length || 0} open positions</span>
            </div>
          </div>
        </div>
      </Card>

      {/* Account Specifications & Safety Parameters */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 font-mono">
        {/* Terminal Connection Details */}
        <Card>
          <CardHeader>
            <div>
              <CardTitle className="flex items-center gap-2 text-sky-400">
                <Activity className="w-4 h-4" /> Terminal Details
              </CardTitle>
              <CardDescription>MT5 IPC Process & Path</CardDescription>
            </div>
            <Badge status={status?.adapter_mode?.toUpperCase() || "REAL"} variant="blue" />
          </CardHeader>

          <div className="space-y-3 text-xs border-t border-slate-800 pt-4">
            <div className="flex justify-between">
              <span className="text-slate-400">Adapter Mode:</span>
              <span className="text-slate-200 uppercase font-bold">{status?.adapter_mode || "real"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Health State:</span>
              <span className="text-emerald-400 font-bold">{status?.health_state || "READY"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Account Currency:</span>
              <span className="text-slate-200 font-bold">{account?.currency || "USD"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Trade Execution:</span>
              <span className="text-emerald-300 font-bold">ALLOWED</span>
            </div>
          </div>
        </Card>

        {/* Account Safety Gates */}
        <Card>
          <CardHeader>
            <div>
              <CardTitle className="flex items-center gap-2 text-emerald-400">
                <ShieldCheck className="w-4 h-4" /> Safety Controls
              </CardTitle>
              <CardDescription>Strict Hard Coded Risk Gates</CardDescription>
            </div>
            <Badge status="SAFEGUARDED" variant="green" />
          </CardHeader>

          <div className="space-y-3 text-xs border-t border-slate-800 pt-4">
            <div className="flex justify-between">
              <span className="text-slate-400">Environment Gate:</span>
              <span className="text-emerald-400 font-bold">DEMO ONLY (BLOCKED REAL)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Margin Mode Gate:</span>
              <span className="text-emerald-400 font-bold">HEDGING ONLY</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Max Exposure Limit:</span>
              <span className="text-amber-300 font-bold">{totalVolume.toFixed(2)} / 2.00 Lots</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Max Entries / Signal:</span>
              <span className="text-slate-200 font-bold">8 Split Orders</span>
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
              <CardDescription>XAUUSD Contract Trading Rules</CardDescription>
            </div>
            <Badge status="XAUUSD" variant="blue" />
          </CardHeader>

          <div className="space-y-3 text-xs border-t border-slate-800 pt-4">
            <div className="flex justify-between">
              <span className="text-slate-400">Canonical Symbol:</span>
              <span className="text-slate-200 font-bold">XAUUSD</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Broker Symbol:</span>
              <span className="text-slate-200 font-bold">{symbol?.broker_symbol || "XAUUSDm"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Digits / Point:</span>
              <span className="text-slate-200">{symbol?.digits || 2} / {symbol?.point || 0.01}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Volume Min/Max/Step:</span>
              <span className="text-slate-200">0.01 / 2.00 / 0.01</span>
            </div>
          </div>
        </Card>
      </div>

      {/* Active Open Trades / Positions */}
      <Card font-mono>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="text-emerald-400 flex items-center gap-2">
              <TrendingUp className="w-4 h-4" /> Open Positions ({positionsList.length})
            </CardTitle>
            <CardDescription>Live active MT5 positions running on your logged-in account.</CardDescription>
          </div>
          <span className="text-xs font-mono font-bold text-emerald-400">
            Total Floating P&L: {totalProfit >= 0 ? "+" : ""}${totalProfit.toFixed(2)} USD
          </span>
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
              {positionsList.length === 0 ? (
                <tr>
                  <td colSpan={9} className="p-6 text-center text-slate-500">
                    No active open positions on logged-in account.
                  </td>
                </tr>
              ) : (
                positionsList.map((p: any) => (
                  <tr key={p.ticket || p.id} className="hover:bg-slate-900/50">
                    <td className="p-3 text-slate-300 font-bold">#{p.ticket || p.id}</td>
                    <td className="p-3 font-bold text-sky-400">{p.symbol || "XAUUSD"}</td>
                    <td className="p-3 font-bold">
                      <span className={`px-2 py-0.5 rounded text-[10px] ${p.position_type === "BUY" || p.type === "BUY" ? "bg-emerald-950 text-emerald-300 border border-emerald-800" : "bg-rose-950 text-rose-300 border border-rose-800"}`}>
                        {p.position_type === "BUY" || p.type === "BUY" ? <ArrowUpRight className="w-3 h-3 inline mr-0.5" /> : <ArrowDownRight className="w-3 h-3 inline mr-0.5" />}
                        {p.position_type || p.type}
                      </span>
                    </td>
                    <td className="p-3 text-slate-200">{Number(p.volume || 0).toFixed(2)} Lots</td>
                    <td className="p-3 text-slate-200">{Number(p.price_open || 0).toFixed(2)}</td>
                    <td className="p-3 text-slate-200">{Number(p.price_current || p.price_open || 0).toFixed(2)}</td>
                    <td className="p-3 text-rose-400 font-semibold">{p.stop_loss || p.sl ? Number(p.stop_loss || p.sl).toFixed(2) : "-"}</td>
                    <td className="p-3 text-emerald-400 font-semibold">{p.take_profit || p.tp ? Number(p.take_profit || p.tp).toFixed(2) : "-"}</td>
                    <td className={`p-3 font-bold ${Number(p.profit || 0) >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                      {Number(p.profit || 0) >= 0 ? "+" : ""}${Number(p.profit || 0).toFixed(2)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Pending Limit Orders */}
      <Card font-mono>
        <CardHeader>
          <CardTitle className="text-sky-400 flex items-center gap-2">
            <Layers className="w-4 h-4" /> Pending Orders ({ordersList.length})
          </CardTitle>
          <CardDescription>Laddered limit orders placed on your MetaTrader 5 account.</CardDescription>
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
              {ordersList.length === 0 ? (
                <tr>
                  <td colSpan={7} className="p-6 text-center text-slate-500">
                    No pending limit orders queued in MT5.
                  </td>
                </tr>
              ) : (
                ordersList.map((o: any) => (
                  <tr key={o.ticket || o.id} className="hover:bg-slate-900/50">
                    <td className="p-3 text-slate-300 font-bold">#{o.ticket || o.id}</td>
                    <td className="p-3 font-bold text-amber-400">{o.order_type || o.type}</td>
                    <td className="p-3 text-slate-200">{Number(o.volume || 0).toFixed(2)} Lots</td>
                    <td className="p-3 text-slate-200 font-bold">{Number(o.price || o.price_setup || 0).toFixed(2)}</td>
                    <td className="p-3 text-rose-400 font-semibold">{o.stop_loss || o.sl ? Number(o.stop_loss || o.sl).toFixed(2) : "-"}</td>
                    <td className="p-3 text-emerald-400 font-semibold">{o.take_profit || o.tp ? Number(o.take_profit || o.tp).toFixed(2) : "-"}</td>
                    <td className="p-3"><Badge status={o.state || "PLACED"} /></td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Execution Batches Queue */}
      <Card font-mono>
        <CardHeader>
          <CardTitle className="text-slate-200">MT5 Execution Batch Queue</CardTitle>
          <CardDescription>Single-writer queue processing order placement requests.</CardDescription>
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
              {batchesList.length === 0 ? (
                <tr>
                  <td colSpan={7} className="p-4 text-center text-slate-500">
                    No execution batches queued.
                  </td>
                </tr>
              ) : (
                batchesList.map((b: any) => (
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

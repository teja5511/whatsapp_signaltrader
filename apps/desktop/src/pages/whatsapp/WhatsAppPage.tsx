import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../../api/apiClient";
import { Card, CardHeader, CardTitle, CardDescription } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { useUiStore } from "../../stores/uiStore";
import { CONTROL_PHRASES } from "../../lib/constants";
import { MessageSquare, RefreshCw, Shield, Users, Check, Save, Link as LinkIcon, Search } from "lucide-react";

export const WhatsAppPage: React.FC = () => {
  const { openConfirmModal } = useUiStore();
  const [groupInput, setGroupInput] = useState("");
  const [adminInput, setAdminInput] = useState("");
  const [inviteLinkInput, setInviteLinkInput] = useState("");
  const [isResolvingLink, setIsResolvingLink] = useState(false);
  const [saveSuccessMsg, setSaveSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const { data: status, refetch: refetchStatus } = useQuery({
    queryKey: ["waStatus"],
    queryFn: () => apiClient.getWhatsAppStatus().catch(() => ({ connected: false, mode: "baileys_node" })),
    refetchInterval: 5000,
  });

  const { data: config, refetch: refetchConfig } = useQuery({
    queryKey: ["waConfig"],
    queryFn: () => apiClient.getWhatsAppConfiguration().catch(() => ({ approved_group_id: "", approved_admin_id: "" })),
    refetchInterval: 5000,
  });

  const { data: spool } = useQuery({
    queryKey: ["waSpool"],
    queryFn: () => apiClient.getWhatsAppSpool().catch(() => ({ pending: 0, delivered: 0, quarantined: 0 })),
    refetchInterval: 5000,
  });

  const { data: groups, refetch: refetchGroups, isFetching: isFetchingGroups } = useQuery({
    queryKey: ["waGroups"],
    queryFn: () => apiClient.listWhatsAppGroups().catch(() => []),
    enabled: false,
  });

  const handleResetSession = () => {
    openConfirmModal({
      type: "RESET_WHATSAPP",
      title: "Reset WhatsApp Worker Session",
      description: "Logs out current Baileys/OpenWA WhatsApp session and removes stored session data on disk.",
      phrase: CONTROL_PHRASES.RESET_WHATSAPP,
      action: async () => {
        await apiClient.resetWhatsAppSession(CONTROL_PHRASES.RESET_WHATSAPP);
        refetchStatus();
      },
    });
  };

  const handleSaveAllowlist = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    if (groupInput.trim()) {
      await apiClient.setWhatsAppGroup(groupInput.trim());
    }
    if (adminInput.trim()) {
      await apiClient.setWhatsAppAdmin(adminInput.trim());
    }
    setSaveSuccessMsg("WhatsApp Allowlist updated successfully!");
    refetchConfig();
    setTimeout(() => setSaveSuccessMsg(null), 4000);
  };

  const handleSelectGroup = async (groupId: string, displayName: string) => {
    setErrorMsg(null);
    setGroupInput(groupId);
    await apiClient.setWhatsAppGroup(groupId, displayName);
    setSaveSuccessMsg(`Approved group set to: ${displayName} (${groupId})`);
    refetchConfig();
    setTimeout(() => setSaveSuccessMsg(null), 4000);
  };

  const handleResolveInviteLink = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inviteLinkInput.trim()) return;
    setIsResolvingLink(true);
    setErrorMsg(null);
    try {
      const summary = await apiClient.resolveGroupInviteLink(inviteLinkInput.trim());
      if (summary && summary.group_id) {
        await apiClient.setWhatsAppGroup(summary.group_id, summary.display_name);
        setGroupInput(summary.group_id);
        setSaveSuccessMsg(`Resolved & Set Group: ${summary.display_name} (${summary.group_id})`);
        setInviteLinkInput("");
        refetchConfig();
        refetchGroups();
        setTimeout(() => setSaveSuccessMsg(null), 4000);
      } else {
        setErrorMsg("Could not find WhatsApp group for that invite link. Ensure worker is connected.");
      }
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to resolve WhatsApp group invite link.");
    } finally {
      setIsResolvingLink(false);
    }
  };

  const currentGroup = groupInput || config?.approved_group_id || "Not Configured";
  const currentAdmin = adminInput || config?.approved_admin_id || "Not Configured";

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold font-mono text-slate-100">WhatsApp Setup & Group Configuration</h1>
          <p className="text-xs text-slate-400 mt-1">Manage single WhatsApp account connection, scan groups, or paste a group invite link.</p>
        </div>
        <Button variant="secondary" size="sm" onClick={() => { refetchStatus(); refetchConfig(); }} className="gap-2 font-mono">
          <RefreshCw className="w-3.5 h-3.5" /> Refresh Status
        </Button>
      </div>

      {saveSuccessMsg && (
        <div className="p-3 rounded bg-emerald-950/80 border border-emerald-700/80 text-emerald-300 text-xs font-mono flex items-center gap-2">
          <Check className="w-4 h-4" /> {saveSuccessMsg}
        </div>
      )}

      {errorMsg && (
        <div className="p-3 rounded bg-rose-950/80 border border-rose-700/80 text-rose-300 text-xs font-mono flex items-center gap-2">
          {errorMsg}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Connection & Session Card */}
        <Card>
          <CardHeader>
            <div>
              <CardTitle className="flex items-center gap-2 text-sky-400">
                <MessageSquare className="w-4 h-4" /> Connection & Session
              </CardTitle>
              <CardDescription>Baileys Worker & Connection Engine</CardDescription>
            </div>
            <Badge status={status?.connection_state === "READY" || status?.connected ? "CONNECTED" : "DISCONNECTED"} />
          </CardHeader>

          <div className="space-y-3 font-mono text-xs border-t border-slate-800 pt-4">
            <div className="flex justify-between">
              <span className="text-slate-400">Connection Engine:</span>
              <span className="text-slate-200">Baileys Direct (WebSockets)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Worker Status:</span>
              <span className="text-emerald-400 font-bold">{status?.connection_state || "READY"}</span>
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
                <Shield className="w-4 h-4" /> Group & Admin Allowlist
              </CardTitle>
              <CardDescription>Single Approved Group & Admin Phone Number</CardDescription>
            </div>
            <Badge status={currentGroup !== "Not Configured" ? "CONFIGURED" : "NOT_SET"} variant={currentGroup !== "Not Configured" ? "green" : "red"} />
          </CardHeader>

          <form onSubmit={handleSaveAllowlist} className="space-y-4 font-mono text-xs border-t border-slate-800 pt-4">
            <div>
              <label className="block text-slate-400 mb-1">Target Group JID (`APPROVED_GROUP_JID`):</label>
              <input
                type="text"
                value={groupInput}
                onChange={(e) => setGroupInput(e.target.value)}
                placeholder={config?.approved_group_id || "e.g. 120363024890123456@g.us"}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded text-slate-100 font-bold focus:outline-none focus:ring-1 focus:ring-sky-500"
              />
              <span className="text-[11px] text-slate-500 mt-0.5 block">Current: {currentGroup}</span>
            </div>

            <div>
              <label className="block text-slate-400 mb-1">Approved Admin JID (`APPROVED_ADMIN_JID`):</label>
              <input
                type="text"
                value={adminInput}
                onChange={(e) => setAdminInput(e.target.value)}
                placeholder={config?.approved_admin_id || "e.g. 919876543210@s.whatsapp.net"}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded text-slate-100 font-bold focus:outline-none focus:ring-1 focus:ring-sky-500"
              />
              <span className="text-[11px] text-slate-500 mt-0.5 block">Current: {currentAdmin}</span>
            </div>

            <Button type="submit" variant="primary" size="sm" className="gap-2">
              <Save className="w-3.5 h-3.5" /> Save Allowlist Configuration
            </Button>
          </form>
        </Card>
      </div>

      {/* Option A: Resolve Group Invite Link */}
      <Card>
        <CardHeader>
          <CardTitle className="text-amber-400 flex items-center gap-2">
            <LinkIcon className="w-4 h-4" /> Option A: Paste Group Invite Link
          </CardTitle>
          <CardDescription>Paste your WhatsApp group invite link (e.g. https://chat.whatsapp.com/...) to automatically resolve the Group ID.</CardDescription>
        </CardHeader>

        <form onSubmit={handleResolveInviteLink} className="flex flex-col sm:flex-row gap-3 pt-2 font-mono text-xs">
          <input
            type="text"
            value={inviteLinkInput}
            onChange={(e) => setInviteLinkInput(e.target.value)}
            placeholder="https://chat.whatsapp.com/AbCdEfGhIjK123456"
            className="flex-1 px-3 py-2.5 bg-slate-950 border border-slate-700 rounded text-slate-100 focus:outline-none focus:ring-1 focus:ring-amber-500"
          />
          <Button type="submit" variant="warning" size="sm" disabled={isResolvingLink || !inviteLinkInput.trim()} className="gap-2">
            <Search className={`w-3.5 h-3.5 ${isResolvingLink ? "animate-spin" : ""}`} />
            {isResolvingLink ? "Resolving..." : "Resolve & Set Group"}
          </Button>
        </form>
      </Card>

      {/* Option B: Fetch Connected WhatsApp Groups */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="text-sky-400 flex items-center gap-2">
              <Users className="w-4 h-4" /> Option B: Scan Connected WhatsApp Groups
            </CardTitle>
            <CardDescription>Fetch live groups from your linked WhatsApp account to auto-select your target group ID.</CardDescription>
          </div>
          <Button variant="secondary" size="sm" onClick={() => refetchGroups()} disabled={isFetchingGroups} className="gap-2 font-mono">
            <RefreshCw className={`w-3.5 h-3.5 ${isFetchingGroups ? "animate-spin" : ""}`} />
            {isFetchingGroups ? "Fetching..." : "Fetch My Groups"}
          </Button>
        </CardHeader>

        {groups && groups.length > 0 ? (
          <div className="overflow-x-auto font-mono text-xs">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 bg-slate-950">
                  <th className="p-3">Group Name</th>
                  <th className="p-3">Group JID</th>
                  <th className="p-3">Members</th>
                  <th className="p-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {groups.map((g: any) => (
                  <tr key={g.group_id} className="hover:bg-slate-900/50">
                    <td className="p-3 font-bold text-slate-200">{g.display_name}</td>
                    <td className="p-3 text-sky-400 font-mono select-all">{g.group_id}</td>
                    <td className="p-3 text-slate-400">{g.participant_count || "-"}</td>
                    <td className="p-3 text-right">
                      <Button
                        variant={g.group_id === currentGroup ? "secondary" : "primary"}
                        size="sm"
                        onClick={() => handleSelectGroup(g.group_id, g.display_name)}
                        className="text-xs"
                      >
                        {g.group_id === currentGroup ? "Selected" : "Select Group"}
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-6 text-center text-xs font-mono text-slate-400 bg-slate-950/40 rounded-lg border border-dashed border-slate-800">
            {isFetchingGroups
              ? "Scanning connected WhatsApp groups..."
              : "Click 'Fetch My Groups' above or paste your Group Invite Link in Option A."}
          </div>
        )}
      </Card>

      {/* Spool Queue Monitoring */}
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
            <span className="text-xl font-bold text-slate-300">Disk Spool</span>
            <span className="block text-xs text-slate-400 mt-1">Status Active</span>
          </div>
        </div>
      </Card>
    </div>
  );
};

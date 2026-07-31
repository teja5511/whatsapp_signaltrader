import React, { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../../api/apiClient";
import { Card, CardHeader, CardTitle, CardDescription } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { useUiStore } from "../../stores/uiStore";
import { CONTROL_PHRASES } from "../../lib/constants";
import { 
  MessageSquare, RefreshCw, Shield, Users, Check, Save, Link as LinkIcon, 
  Search, Plus, Trash2, ToggleLeft, ToggleRight, AlertTriangle, Activity, CheckSquare, Square
} from "lucide-react";

export const WhatsAppPage: React.FC = () => {
  const { openConfirmModal } = useUiStore();
  const [adminInput, setAdminInput] = useState("");
  const [inviteLinkInput, setInviteLinkInput] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedJids, setSelectedJids] = useState<Set<string>>(new Set());
  const [isResolvingLink, setIsResolvingLink] = useState(false);
  const [saveSuccessMsg, setSaveSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // 1. Worker & Configuration Query
  const { data: status, refetch: refetchStatus } = useQuery({
    queryKey: ["waStatus"],
    queryFn: () => apiClient.getWhatsAppStatus().catch(() => ({ connected: false, mode: "baileys_node" })),
    refetchInterval: 5000,
  });

  const { data: config, refetch: refetchConfig } = useQuery({
    queryKey: ["waConfig"],
    queryFn: () => apiClient.getWhatsAppConfiguration().catch(() => ({ approved_admin_id: "" })),
    refetchInterval: 5000,
  });

  const { data: spool } = useQuery({
    queryKey: ["waSpool"],
    queryFn: () => apiClient.getWhatsAppSpool().catch(() => ({ pending: 0, delivered: 0, quarantined: 0 })),
    refetchInterval: 5000,
  });

  // 2. FEATURE 2 & 13: Live WhatsApp Groups & SQLite Configured Groups Auto-Polling
  const { data: rawGroups, refetch: refetchGroups, isFetching: isFetchingGroups } = useQuery({
    queryKey: ["waGroups"],
    queryFn: () => apiClient.listWhatsAppGroups().catch(() => []),
    refetchInterval: 5000,
  });

  const { data: selectedGroups, refetch: refetchSelectedGroups } = useQuery({
    queryKey: ["waSelectedGroups"],
    queryFn: () => apiClient.getSelectedGroups().catch(() => []),
    refetchInterval: 5000,
  });

  // 3. Computed Datasets & Deduplication
  const groupsList = useMemo(() => Array.isArray(rawGroups) ? rawGroups : [], [rawGroups]);
  const configuredGroupsList = useMemo(() => Array.isArray(selectedGroups) ? selectedGroups : [], [selectedGroups]);

  const configuredJidsSet = useMemo(() => {
    return new Set(configuredGroupsList.map((g: any) => g.jid || g.group_id));
  }, [configuredGroupsList]);

  // Live WhatsApp participating groups Map for missing group detection
  const liveGroupsMap = useMemo(() => {
    const map = new Map<string, any>();
    groupsList.forEach((g: any) => {
      const jid = g.id || g.group_id;
      if (jid) map.set(jid, g);
    });
    return map;
  }, [groupsList]);

  // FEATURE 3 & 14: Available Groups Filter, Search & Alphabetical Sort
  const availableGroups = useMemo(() => {
    return groupsList
      .filter((g: any) => {
        const jid = g.id || g.group_id;
        return jid && !configuredJidsSet.has(jid);
      })
      .filter((g: any) => {
        if (!searchQuery.trim()) return true;
        const q = searchQuery.toLowerCase().trim();
        const name = (g.name || g.display_name || "").toLowerCase();
        const jid = (g.id || g.group_id || "").toLowerCase();
        return name.includes(q) || jid.includes(q);
      })
      .sort((a: any, b: any) => {
        const nameA = (a.name || a.display_name || "").toLowerCase();
        const nameB = (b.name || b.display_name || "").toLowerCase();
        return nameA.localeCompare(nameB);
      });
  }, [groupsList, configuredJidsSet, searchQuery]);

  // FEATURE 15: Header Statistics Calculations
  const totalGroupsCount = groupsList.length;
  const configuredCount = configuredGroupsList.length;
  const enabledCount = configuredGroupsList.filter((g: any) => g.enabled).length;

  // Actions
  const handleAddGroup = async (jid: string, name: string) => {
    setErrorMsg(null);
    try {
      await apiClient.addSelectedGroup(jid, name);
      setSaveSuccessMsg(`Added group "${name}" to Configured Groups`);
      refetchSelectedGroups();
      refetchGroups();
      setTimeout(() => setSaveSuccessMsg(null), 3000);
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to add group.");
    }
  };

  const handleBatchAddSelected = async () => {
    if (selectedJids.size === 0) return;
    setErrorMsg(null);
    try {
      for (const jid of Array.from(selectedJids)) {
        const g = availableGroups.find((item: any) => (item.id || item.group_id) === jid);
        const name = g ? (g.name || g.display_name || jid) : jid;
        await apiClient.addSelectedGroup(jid, name);
      }
      setSaveSuccessMsg(`Added ${selectedJids.size} selected group(s) to Configured Groups`);
      setSelectedJids(new Set());
      refetchSelectedGroups();
      refetchGroups();
      setTimeout(() => setSaveSuccessMsg(null), 3000);
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to add selected groups.");
    }
  };

  const handleDeleteGroup = async (jid: string, name: string) => {
    setErrorMsg(null);
    try {
      await apiClient.deleteSelectedGroup(jid);
      setSaveSuccessMsg(`Removed "${name}" from Configured Groups`);
      refetchSelectedGroups();
      refetchGroups();
      setTimeout(() => setSaveSuccessMsg(null), 3000);
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to remove group.");
    }
  };

  const handleToggleGroupEnabled = async (jid: string, currentEnabled: boolean) => {
    setErrorMsg(null);
    try {
      await apiClient.patchSelectedGroup(jid, !currentEnabled);
      refetchSelectedGroups();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to update group status.");
    }
  };

  const handleSaveAdmin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (adminInput.trim()) {
      await apiClient.setWhatsAppAdmin(adminInput.trim());
      setSaveSuccessMsg("Approved Admin JID updated successfully!");
      refetchConfig();
      setTimeout(() => setSaveSuccessMsg(null), 3000);
    }
  };

  const handleResolveInviteLink = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inviteLinkInput.trim()) return;
    setIsResolvingLink(true);
    setErrorMsg(null);
    try {
      const summary = await apiClient.resolveGroupInviteLink(inviteLinkInput.trim());
      if (summary && (summary.id || summary.group_id)) {
        const jid = summary.id || summary.group_id;
        const name = summary.name || summary.display_name || jid;
        await apiClient.addSelectedGroup(jid, name);
        setSaveSuccessMsg(`Resolved & Configured Group: ${name} (${jid})`);
        setInviteLinkInput("");
        refetchSelectedGroups();
        refetchGroups();
        setTimeout(() => setSaveSuccessMsg(null), 3000);
      } else {
        setErrorMsg("Could not resolve WhatsApp group from invite link. Ensure worker is connected.");
      }
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to resolve group invite link.");
    } finally {
      setIsResolvingLink(false);
    }
  };

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

  const toggleSelectJid = (jid: string) => {
    const next = new Set(selectedJids);
    if (next.has(jid)) next.delete(jid);
    else next.add(jid);
    setSelectedJids(next);
  };

  const toggleSelectAllAvailable = () => {
    if (selectedJids.size === availableGroups.length) {
      setSelectedJids(new Set());
    } else {
      setSelectedJids(new Set(availableGroups.map((g: any) => g.id || g.group_id)));
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold font-mono text-slate-100">WhatsApp Group Manager</h1>
          <p className="text-xs text-slate-400 mt-1">Live Baileys group scanner, persistent SQLite allowlist & group signal monitoring controls.</p>
        </div>
        <Button variant="secondary" size="sm" onClick={() => { refetchStatus(); refetchGroups(); refetchSelectedGroups(); }} className="gap-2 font-mono">
          <RefreshCw className="w-3.5 h-3.5" /> Refresh Groups
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

      {/* FEATURE 15: Top Summary Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 font-mono">
        <Card className="p-4 bg-slate-900/60 border-slate-800">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Total WhatsApp Groups</span>
            <Users className="w-4 h-4 text-sky-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100 mt-2">
            {totalGroupsCount}
          </div>
          <span className="text-[11px] text-slate-500 mt-1 block">Live Participating Chats</span>
        </Card>

        <Card className="p-4 bg-slate-900/60 border-slate-800">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Configured Groups</span>
            <Shield className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-bold text-indigo-400 mt-2">
            {configuredCount}
          </div>
          <span className="text-[11px] text-slate-500 mt-1 block">Persisted in SQLite</span>
        </Card>

        <Card className="p-4 bg-slate-900/60 border-slate-800">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Enabled Monitoring Groups</span>
            <Activity className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-emerald-400 mt-2">
            {enabledCount}
          </div>
          <span className="text-[11px] text-slate-500 mt-1 block">Actively Parsed by Worker</span>
        </Card>
      </div>

      {/* FEATURE 6 & 7: Configured Groups Section */}
      <Card font-mono>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="text-emerald-400 flex items-center gap-2">
              <Shield className="w-4 h-4" /> Configured Monitored Groups ({configuredCount})
            </CardTitle>
            <CardDescription>SQLite persisted groups. Messages from enabled groups are actively ingested by the bot.</CardDescription>
          </div>
        </CardHeader>

        <div className="overflow-x-auto text-xs">
          <table className="w-full text-left border-collapse">
            <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] border-b border-slate-800">
              <tr>
                <th className="p-3">Group Name</th>
                <th className="p-3">WhatsApp JID</th>
                <th className="p-3 text-center">Status</th>
                <th className="p-3">Last Signal Time</th>
                <th className="p-3">Messages Today</th>
                <th className="p-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {configuredGroupsList.length === 0 ? (
                <tr>
                  <td colSpan={6} className="p-6 text-center text-slate-500">
                    No configured groups in SQLite. Add groups from Available Groups below.
                  </td>
                </tr>
              ) : (
                configuredGroupsList.map((g: any) => {
                  const jid = g.jid || g.group_id;
                  const liveGroup = liveGroupsMap.get(jid);
                  const isMissing = !liveGroup && groupsList.length > 0;

                  return (
                    <tr key={g.id || jid} className="hover:bg-slate-900/50">
                      <td className="p-3 font-bold text-slate-100 flex items-center gap-2">
                        {g.name || g.display_name || jid}
                        {/* FEATURE 17: Missing Group Badge */}
                        {isMissing && (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800 text-[10px]">
                            <AlertTriangle className="w-3 h-3" /> Missing Group
                          </span>
                        )}
                      </td>
                      <td className="p-3 text-sky-400 select-all">{jid}</td>
                      <td className="p-3 text-center">
                        <button
                          onClick={() => handleToggleGroupEnabled(jid, Boolean(g.enabled))}
                          className={`inline-flex items-center gap-1 px-2.5 py-1 rounded text-[11px] font-bold transition-colors ${
                            g.enabled 
                              ? "bg-emerald-950 text-emerald-300 border border-emerald-800 hover:bg-emerald-900" 
                              : "bg-slate-900 text-slate-500 border border-slate-800 hover:bg-slate-800"
                          }`}
                        >
                          {g.enabled ? <ToggleRight className="w-4 h-4 text-emerald-400" /> : <ToggleLeft className="w-4 h-4 text-slate-500" />}
                          {g.enabled ? "ENABLED" : "DISABLED"}
                        </button>
                      </td>
                      <td className="p-3 text-slate-400">
                        {g.lastSignalTime ? new Date(g.lastSignalTime).toLocaleTimeString() : "No signals yet"}
                      </td>
                      <td className="p-3 text-slate-300 font-bold">
                        {g.messagesToday || 0}
                      </td>
                      <td className="p-3 text-right">
                        {/* FEATURE 10: Delete Button */}
                        <Button
                          variant="danger"
                          size="sm"
                          onClick={() => handleDeleteGroup(jid, g.name || jid)}
                          className="gap-1 text-xs"
                        >
                          <Trash2 className="w-3.5 h-3.5" /> Delete
                        </Button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* FEATURE 3 & 4: Available WhatsApp Groups Section */}
      <Card font-mono>
        <CardHeader className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <CardTitle className="text-sky-400 flex items-center gap-2">
              <Users className="w-4 h-4" /> Available WhatsApp Groups ({availableGroups.length})
            </CardTitle>
            <CardDescription>Live groups fetched directly from your Baileys connection store.</CardDescription>
          </div>

          <div className="flex items-center gap-3">
            {/* Search Box */}
            <div className="relative">
              <Search className="w-3.5 h-3.5 absolute left-3 top-3 text-slate-500" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search groups..."
                className="pl-8 pr-3 py-1.5 bg-slate-950 border border-slate-700 rounded text-slate-100 text-xs focus:outline-none focus:ring-1 focus:ring-sky-500"
              />
            </div>

            {selectedJids.size > 0 && (
              <Button variant="primary" size="sm" onClick={handleBatchAddSelected} className="gap-1 text-xs">
                <Plus className="w-3.5 h-3.5" /> Add Selected ({selectedJids.size})
              </Button>
            )}
          </div>
        </CardHeader>

        {availableGroups.length > 0 ? (
          <div className="overflow-x-auto text-xs">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 bg-slate-950 uppercase text-[10px]">
                  <th className="p-3 w-10 text-center">
                    <button onClick={toggleSelectAllAvailable} className="text-slate-400 hover:text-slate-200">
                      {selectedJids.size > 0 && selectedJids.size === availableGroups.length ? (
                        <CheckSquare className="w-4 h-4 text-sky-400" />
                      ) : (
                        <Square className="w-4 h-4" />
                      )}
                    </button>
                  </th>
                  <th className="p-3">Group Name</th>
                  <th className="p-3">WhatsApp JID</th>
                  <th className="p-3">Participants</th>
                  <th className="p-3">Type</th>
                  <th className="p-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {availableGroups.map((g: any) => {
                  const jid = g.id || g.group_id;
                  const name = g.name || g.display_name || "WhatsApp Group";
                  const participantCount = g.participants || g.participant_count || 0;
                  const isChecked = selectedJids.has(jid);

                  return (
                    <tr key={jid} className={`hover:bg-slate-900/50 ${isChecked ? "bg-slate-900/40" : ""}`}>
                      <td className="p-3 text-center">
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={() => toggleSelectJid(jid)}
                          className="rounded border-slate-700 bg-slate-950 text-sky-500 focus:ring-0"
                        />
                      </td>
                      <td className="p-3 font-bold text-slate-200">{name}</td>
                      <td className="p-3 text-sky-400 select-all">{jid}</td>
                      <td className="p-3 text-slate-300">{participantCount} members</td>
                      <td className="p-3 text-slate-400">
                        {g.isCommunity ? <Badge status="COMMUNITY" variant="blue" /> : <Badge status="GROUP" />}
                      </td>
                      <td className="p-3 text-right">
                        {/* FEATURE 4: ADD Button */}
                        <Button
                          variant="primary"
                          size="sm"
                          onClick={() => handleAddGroup(jid, name)}
                          className="gap-1 text-xs"
                        >
                          <Plus className="w-3.5 h-3.5" /> ADD
                        </Button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-6 text-center text-xs font-mono text-slate-400 bg-slate-950/40 rounded-lg border border-dashed border-slate-800">
            {isFetchingGroups
              ? "Scanning connected WhatsApp groups..."
              : searchQuery
              ? "No available groups match your search filter."
              : "All participating WhatsApp groups have been configured into SQLite."}
          </div>
        )}
      </Card>

      {/* Option A: Paste Group Invite Link */}
      <Card font-mono>
        <CardHeader>
          <CardTitle className="text-amber-400 flex items-center gap-2">
            <LinkIcon className="w-4 h-4" /> Option A: Resolve & Add Group Invite Link
          </CardTitle>
          <CardDescription>Paste your WhatsApp group invite link (e.g. https://chat.whatsapp.com/...) to automatically resolve and add to SQLite.</CardDescription>
        </CardHeader>

        <form onSubmit={handleResolveInviteLink} className="flex flex-col sm:flex-row gap-3 pt-2 text-xs">
          <input
            type="text"
            value={inviteLinkInput}
            onChange={(e) => setInviteLinkInput(e.target.value)}
            placeholder="https://chat.whatsapp.com/AbCdEfGhIjK123456"
            className="flex-1 px-3 py-2.5 bg-slate-950 border border-slate-700 rounded text-slate-100 focus:outline-none focus:ring-1 focus:ring-amber-500"
          />
          <Button type="submit" variant="warning" size="sm" disabled={isResolvingLink || !inviteLinkInput.trim()} className="gap-2">
            <Search className={`w-3.5 h-3.5 ${isResolvingLink ? "animate-spin" : ""}`} />
            {isResolvingLink ? "Resolving..." : "Resolve & Add Group"}
          </Button>
        </form>
      </Card>

      {/* Approved Admin JID */}
      <Card font-mono>
        <CardHeader>
          <CardTitle className="text-emerald-400 flex items-center gap-2">
            <Shield className="w-4 h-4" /> Approved Admin Allowlist
          </CardTitle>
          <CardDescription>Only signals sent by this WhatsApp Admin ID will be executed.</CardDescription>
        </CardHeader>

        <form onSubmit={handleSaveAdmin} className="space-y-3 text-xs border-t border-slate-800 pt-4">
          <div>
            <label className="block text-slate-400 mb-1">Approved Admin JID (`APPROVED_ADMIN_JID`):</label>
            <div className="flex gap-3">
              <input
                type="text"
                value={adminInput}
                onChange={(e) => setAdminInput(e.target.value)}
                placeholder={config?.approved_admin_id || "e.g. 919876543210@s.whatsapp.net"}
                className="flex-1 px-3 py-2 bg-slate-950 border border-slate-700 rounded text-slate-100 font-bold focus:outline-none focus:ring-1 focus:ring-sky-500"
              />
              <Button type="submit" variant="primary" size="sm" className="gap-2">
                <Save className="w-3.5 h-3.5" /> Save Admin
              </Button>
            </div>
            <span className="text-[11px] text-slate-500 mt-1 block">Current: {config?.approved_admin_id || "Not Configured"}</span>
          </div>
        </form>
      </Card>
    </div>
  );
};

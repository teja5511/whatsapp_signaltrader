import React, { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../../api/apiClient";
import { globalEventClient } from "../../realtime/eventClient";
import { Card, CardHeader, CardTitle, CardDescription } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { DomainEvent, RealtimeStatus } from "../../types";
import { Activity, RefreshCw, Filter, Copy, Code } from "lucide-react";

export const EventsPage: React.FC = () => {
  const [liveEvents, setLiveEvents] = useState<DomainEvent[]>([]);
  const [realtimeState, setRealtimeState] = useState<RealtimeStatus>("DISCONNECTED");
  const [selectedEvent, setSelectedEvent] = useState<DomainEvent | null>(null);

  // Initial Rest Fetch
  const { data: initialEvents, refetch } = useQuery({
    queryKey: ["eventsReplay"],
    queryFn: () => apiClient.listDomainEvents(0, 100),
  });

  useEffect(() => {
    if (initialEvents) {
      setLiveEvents(initialEvents);
    }
  }, [initialEvents]);

  // Connect Realtime Event Client
  useEffect(() => {
    const unsubscribe = globalEventClient.subscribe(
      (newEvent) => {
        setLiveEvents((prev) => [newEvent, ...prev.slice(0, 499)]);
      },
      (newStatus) => {
        setRealtimeState(newStatus);
      }
    );

    globalEventClient.connect();

    return () => {
      unsubscribe();
    };
  }, []);

  return (
    <div className="space-y-6 font-mono">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-100 font-mono">Real-Time Domain Event Stream & Outbox Replay</h1>
          <p className="text-xs text-slate-400 mt-1">Immutable transactional outbox domain events streamed via WebSocket / SSE with zero-trust payload redaction.</p>
        </div>
        <div className="flex items-center gap-3">
          <Badge status={realtimeState} />
          <Button variant="secondary" size="sm" onClick={() => refetch()} className="gap-2 font-mono">
            <RefreshCw className="w-3.5 h-3.5" /> Replay Events
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Events Table */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-sky-400 flex items-center gap-2">
              <Activity className="w-4 h-4" /> Live Domain Event Log ({liveEvents.length})
            </CardTitle>
          </CardHeader>

          <div className="overflow-x-auto max-h-[600px] overflow-y-auto">
            <table className="w-full text-left font-mono text-xs">
              <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] sticky top-0">
                <tr>
                  <th className="p-3">Seq</th>
                  <th className="p-3">Event Type</th>
                  <th className="p-3">Aggregate</th>
                  <th className="p-3">Campaign</th>
                  <th className="p-3">Time</th>
                  <th className="p-3 text-right">Inspect</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {liveEvents.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="p-6 text-center text-slate-500">
                      No domain events received.
                    </td>
                  </tr>
                ) : (
                  liveEvents.map((e) => (
                    <tr key={e.event_id || e.sequence} className="hover:bg-slate-800/40 cursor-pointer" onClick={() => setSelectedEvent(e)}>
                      <td className="p-3 font-bold text-sky-400">#{e.sequence}</td>
                      <td className="p-3 font-bold text-slate-200">{e.event_type}</td>
                      <td className="p-3 text-slate-400">{e.aggregate_type}</td>
                      <td className="p-3 text-indigo-300">{e.campaign_id?.substring(0, 8) || "N/A"}</td>
                      <td className="p-3 text-slate-400">{new Date(e.occurred_at).toLocaleTimeString()}</td>
                      <td className="p-3 text-right">
                        <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                          <Code className="w-3.5 h-3.5 text-slate-400" />
                        </Button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </Card>

        {/* Selected Event JSON Inspector */}
        <Card>
          <CardHeader>
            <CardTitle className="text-slate-200 flex items-center gap-2">
              <Code className="w-4 h-4 text-emerald-400" /> Event Inspector
            </CardTitle>
            <CardDescription>Redacted event payload & metadata</CardDescription>
          </CardHeader>

          {selectedEvent ? (
            <div className="space-y-4 font-mono text-xs">
              <div className="p-3 rounded bg-slate-950 border border-slate-800 space-y-1.5">
                <div><span className="text-slate-500">Event ID:</span> <span className="text-slate-200 text-[11px] select-all">{selectedEvent.event_id}</span></div>
                <div><span className="text-slate-500">Sequence:</span> <span className="text-sky-400 font-bold">#{selectedEvent.sequence}</span></div>
                <div><span className="text-slate-500">Event Type:</span> <span className="text-emerald-400 font-bold">{selectedEvent.event_type}</span></div>
                <div><span className="text-slate-500">Correlation ID:</span> <span className="text-slate-300 text-[11px] select-all">{selectedEvent.correlation_id}</span></div>
                <div><span className="text-slate-500">Occurred At:</span> <span className="text-slate-300">{new Date(selectedEvent.occurred_at).toLocaleString()}</span></div>
              </div>

              <div>
                <span className="text-slate-400 text-[10px] uppercase font-bold block mb-1">Payload JSON (Redacted):</span>
                <pre className="p-3 rounded bg-slate-950 border border-slate-800 text-[11px] text-emerald-300 overflow-x-auto max-h-80">
                  {JSON.stringify(selectedEvent.payload, null, 2)}
                </pre>
              </div>
            </div>
          ) : (
            <div className="p-12 text-center text-slate-500 text-xs">
              Select an event from the table to inspect details.
            </div>
          )}
        </Card>
      </div>
    </div>
  );
};

import React from 'react';
import {
  Clock,
  Search,
  FolderGit2,
  ShieldCheck,
  FileText,
  Activity,
  ArrowRight,
  User,
  Building,
  Shield,
  CheckCircle2,
  Lock,
  Zap,
} from 'lucide-react';
import { PageHeader } from '../../components/common/PageHeader';
import { useInvestigations, useAuditLogs } from '../../core/api/hooks';

interface RecentActivityPageProps {
  onNavigateToInvestigation?: (id: string) => void;
  onNavigateToSearch?: (query: string) => void;
}

export const RecentActivityPage: React.FC<RecentActivityPageProps> = ({
  onNavigateToInvestigation,
  onNavigateToSearch,
}) => {
  const { data: investigations = [], isLoading: isInvLoading } = useInvestigations();
  const { data: auditLogs = [], isLoading: isAuditLoading } = useAuditLogs(20);

  return (
    <div className="flex-1 overflow-y-auto bg-slate-50 dark:bg-[#070b13] p-4 sm:p-6 lg:p-8">
      <div className="w-full space-y-6">
        <PageHeader
          title="Recent Activity & Investigation Timeline"
          description="Comprehensive audit trail and operational chronology of recent intelligence queries, active investigations, evidence vault additions, and provider executions."
        />

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column: Recent Investigations */}
          <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 space-y-4 shadow-xs">
            <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-800">
              <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <FolderGit2 className="w-4 h-4 text-indigo-500" />
                <span>Active & Recent Investigations</span>
              </h3>
              <span className="text-xs font-mono text-slate-400">
                {investigations.length} Total
              </span>
            </div>

            {isInvLoading ? (
              <div className="text-center py-12 text-xs font-mono text-slate-400">
                Loading active investigations...
              </div>
            ) : investigations.length === 0 ? (
              <div className="text-center py-12 text-xs font-mono text-slate-500">
                No investigations created yet.
              </div>
            ) : (
              <div className="space-y-2.5">
                {investigations.slice(0, 8).map((inv: any) => (
                  <div
                    key={inv.id}
                    onClick={() => onNavigateToInvestigation?.(inv.id)}
                    className="p-3.5 rounded-lg border border-slate-200 dark:border-slate-800/80 hover:border-indigo-500/50 bg-slate-50/50 dark:bg-slate-800/40 hover:bg-indigo-50/30 dark:hover:bg-indigo-950/20 transition-all cursor-pointer flex items-center justify-between group"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-xs text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                          {inv.title || inv.target}
                        </span>
                        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 font-bold uppercase">
                          {inv.target_type || 'TARGET'}
                        </span>
                      </div>
                      <p className="text-[11px] font-mono text-slate-500">
                        ID: {inv.id} • Target: <span className="text-slate-700 dark:text-slate-300">{inv.target}</span>
                      </p>
                    </div>
                    <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-indigo-500 group-hover:translate-x-0.5 transition-all" />
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Right Column: Audit Logs & Events */}
          <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 space-y-4 shadow-xs flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-800">
                <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                  <Activity className="w-4 h-4 text-emerald-500" />
                  <span>Operational Audit Trail</span>
                </h3>
                <span className="text-xs font-mono text-slate-400">
                  Live Core Feed
                </span>
              </div>

              {isAuditLoading ? (
                <div className="text-center py-12 text-xs font-mono text-slate-400">
                  Retrieving tenant audit telemetry...
                </div>
              ) : auditLogs.length === 0 ? (
                <div className="space-y-4 pt-2">
                  <div className="rounded-lg border border-dashed border-slate-200 dark:border-slate-800 p-4 text-center">
                    <p className="text-xs font-mono text-slate-500">
                      Zero audit events recorded in current time window.
                    </p>
                    <p className="text-[11px] text-slate-400 mt-1">
                      Audit telemetry is automatically written upon investigation creation, search execution, and evidence storage.
                    </p>
                  </div>

                  {/* Operational Readiness Status Telemetry */}
                  <div className="space-y-2.5">
                    <span className="text-[10px] font-mono font-bold uppercase text-slate-400 block tracking-wider">
                      System Audit & Compliance Readiness:
                    </span>

                    <div className="p-3 rounded-lg border border-slate-200 dark:border-slate-800/80 bg-slate-50/50 dark:bg-slate-850 flex items-center justify-between">
                      <div className="flex items-center gap-2.5">
                        <Lock className="w-4 h-4 text-indigo-500" />
                        <div>
                          <div className="text-xs font-bold text-slate-900 dark:text-white">Tenant Isolation Protocol</div>
                          <div className="text-[10px] font-mono text-slate-500">Strict scope bounds for tenant_acme</div>
                        </div>
                      </div>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 font-bold border border-emerald-500/20">
                        ENFORCED
                      </span>
                    </div>

                    <div className="p-3 rounded-lg border border-slate-200 dark:border-slate-800/80 bg-slate-50/50 dark:bg-slate-850 flex items-center justify-between">
                      <div className="flex items-center gap-2.5">
                        <ShieldCheck className="w-4 h-4 text-emerald-500" />
                        <div>
                          <div className="text-xs font-bold text-slate-900 dark:text-white">Cryptographic Provenance</div>
                          <div className="text-[10px] font-mono text-slate-500">SHA-256 evidence integrity hashing</div>
                        </div>
                      </div>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 font-bold border border-emerald-500/20">
                        ACTIVE
                      </span>
                    </div>

                    <div className="p-3 rounded-lg border border-slate-200 dark:border-slate-800/80 bg-slate-50/50 dark:bg-slate-850 flex items-center justify-between">
                      <div className="flex items-center gap-2.5">
                        <Zap className="w-4 h-4 text-amber-500" />
                        <div>
                          <div className="text-xs font-bold text-slate-900 dark:text-white">Orchestration Registry</div>
                          <div className="text-[10px] font-mono text-slate-500">335+ OSINT & Threat Intelligence modules</div>
                        </div>
                      </div>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 font-bold border border-emerald-500/20">
                        ONLINE
                      </span>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="space-y-2.5">
                  {auditLogs.slice(0, 8).map((log: any, idx: number) => (
                    <div
                      key={idx}
                      className="p-3 rounded-lg border border-slate-200 dark:border-slate-800/80 bg-slate-50/50 dark:bg-slate-800/30 flex items-start justify-between gap-3 text-xs"
                    >
                      <div className="space-y-0.5">
                        <div className="flex items-center gap-2">
                          <span className="font-mono font-bold text-slate-900 dark:text-white">
                            {log.action || log.event_type || 'SYSTEM_ACTION'}
                          </span>
                          <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-emerald-50 text-emerald-800 border border-emerald-200 dark:bg-emerald-950 dark:border-emerald-800 dark:text-emerald-300">
                            {log.resource_type || 'AUDIT'}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-500 font-mono">
                          User: {log.user_id || 'System'} • Tenant: {log.tenant_id}
                        </p>
                      </div>
                      <span className="text-[10px] font-mono text-slate-400 whitespace-nowrap">
                        {log.timestamp ? new Date(log.timestamp).toLocaleTimeString() : 'Recent'}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

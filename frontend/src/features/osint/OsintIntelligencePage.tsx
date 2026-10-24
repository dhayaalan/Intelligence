import React, { useState } from 'react';
import {
  Search,
  Globe,
  Server,
  Mail,
  Phone,
  User,
  Shield,
  Wrench,
  Terminal,
  RefreshCw,
  ExternalLink,
  Layers,
  ChevronRight,
  Filter
} from 'lucide-react';
import { PageHeader } from '../../components/common/PageHeader';
import { useTools, ToolItem } from '../../core/api/hooks';
import { ToolGrid, ToolRunModal } from '../../components/tools';
import { apiRequest } from '../../core/api/client';

interface OsintIntelligencePageProps {
  onOpenInvestigation?: (target: string, targetType: string, searchId?: string) => void;
}

export const OsintIntelligencePage: React.FC<OsintIntelligencePageProps> = ({
  onOpenInvestigation,
}) => {
  const [activeTab, setActiveTab] = useState<'search' | 'workbench'>('search');
  const [targetType, setTargetType] = useState<'DOMAIN' | 'IP' | 'EMAIL' | 'PHONE' | 'USERNAME'>('DOMAIN');
  const [targetValue, setTargetValue] = useState('');
  const [isExecuting, setIsExecuting] = useState(false);
  const [osintResults, setOsintResults] = useState<any | null>(null);
  const [selectedTool, setSelectedTool] = useState<ToolItem | null>(null);

  const { data: tools = [], isLoading: isToolsLoading } = useTools();
  const osintTools = tools.filter((t) => t.category !== 'Threat Intelligence' && t.category !== 'threat_intelligence');

  const handleExecuteOsint = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetValue.trim()) return;

    setIsExecuting(true);
    try {
      const res = await apiRequest<any>('/search', {
        method: 'POST',
        body: JSON.stringify({
          query: targetValue.trim(),
          modules: ['osint'],
        }),
      });
      setOsintResults(res);
    } catch (err) {
      console.error('OSINT search execution failed', err);
    } finally {
      setIsExecuting(false);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto bg-slate-50 dark:bg-[#070b13] p-4 sm:p-6 lg:p-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <PageHeader
          title="Open-Source Intelligence (OSINT)"
          description="Autonomous open-source investigation across domain footprints, WHOIS/DNS records, network infrastructure, identity recon, email verification, and public records."
        />

        {/* View Switcher */}
        <div className="flex items-center gap-1 bg-slate-200/70 dark:bg-slate-800 p-1 rounded-lg text-xs font-mono">
          <button
            type="button"
            onClick={() => setActiveTab('search')}
            className={`px-3 py-1.5 rounded-md transition-all cursor-pointer font-bold ${
              activeTab === 'search'
                ? 'bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-2xs'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            OSINT Search
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('workbench')}
            className={`px-3 py-1.5 rounded-md transition-all cursor-pointer font-bold ${
              activeTab === 'workbench'
                ? 'bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-2xs'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            Tool Workbench ({osintTools.length})
          </button>
        </div>
      </div>

      {activeTab === 'search' ? (
        <div className="space-y-6">
          {/* Target Query Card */}
          <div className="p-5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-xs">
            <form onSubmit={handleExecuteOsint} className="space-y-4">
              {/* Target Type Selector */}
              <div className="flex items-center gap-2 overflow-x-auto text-xs font-mono">
                <span className="text-slate-500 font-semibold mr-1">TARGET TYPE:</span>
                {[
                  { id: 'DOMAIN', label: 'Domain / FQDN', icon: <Globe className="w-3.5 h-3.5" /> },
                  { id: 'IP', label: 'IP Address / Subnet', icon: <Server className="w-3.5 h-3.5" /> },
                  { id: 'EMAIL', label: 'Email Address', icon: <Mail className="w-3.5 h-3.5" /> },
                  { id: 'PHONE', label: 'Phone Number', icon: <Phone className="w-3.5 h-3.5" /> },
                  { id: 'USERNAME', label: 'Username / Handle', icon: <User className="w-3.5 h-3.5" /> },
                ].map((type) => (
                  <button
                    key={type.id}
                    type="button"
                    onClick={() => setTargetType(type.id as any)}
                    className={`px-3 py-1.5 rounded-lg border transition-all flex items-center gap-1.5 cursor-pointer ${
                      targetType === type.id
                        ? 'bg-indigo-50 border-indigo-300 text-indigo-700 dark:bg-indigo-950/40 dark:border-indigo-800 dark:text-indigo-300 font-bold'
                        : 'bg-slate-100/70 border-slate-200 text-slate-600 hover:bg-slate-200 dark:bg-slate-800/60 dark:border-slate-700/60 dark:text-slate-400'
                    }`}
                  >
                    {type.icon}
                    <span>{type.label}</span>
                  </button>
                ))}
              </div>

              {/* Input bar */}
              <div className="flex flex-col sm:flex-row gap-3">
                <div className="relative flex-1">
                  <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
                  <input
                    type="text"
                    value={targetValue}
                    onChange={(e) => setTargetValue(e.target.value)}
                    placeholder={`Enter ${targetType.toLowerCase()} to investigate (e.g. example.com)...`}
                    className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/80 text-sm font-mono text-slate-900 dark:text-white placeholder-slate-400 focus:outline-hidden focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all"
                  />
                </div>
                <button
                  type="submit"
                  disabled={isExecuting || !targetValue.trim()}
                  className="px-5 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-medium text-sm flex items-center justify-center gap-2 transition-all cursor-pointer shadow-xs shadow-indigo-600/20"
                >
                  {isExecuting ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
                  <span>{isExecuting ? 'Gathering OSINT...' : 'Run OSINT Query'}</span>
                </button>
              </div>
            </form>
          </div>

          {/* Initial State: OSINT Reconnaissance Modules & Presets */}
          {!osintResults && !isExecuting && (
            <div className="space-y-6 animate-in fade-in duration-200">
              {/* Quick Target Presets */}
              <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-2xs">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <span className="text-xs font-mono font-bold uppercase text-slate-500 dark:text-slate-400">
                    Sample OSINT Targets:
                  </span>
                  <div className="flex items-center gap-1.5 flex-wrap">
                    {[
                      { target: 'github.com', type: 'DOMAIN' as const },
                      { target: '1.1.1.1', type: 'IP' as const },
                      { target: 'torvalds', type: 'USERNAME' as const },
                      { target: 'admin@google.com', type: 'EMAIL' as const },
                      { target: '+1-555-0199', type: 'PHONE' as const },
                    ].map((chip) => (
                      <button
                        key={chip.target}
                        type="button"
                        onClick={() => {
                          setTargetType(chip.type);
                          setTargetValue(chip.target);
                        }}
                        className="px-2.5 py-1 rounded-md text-xs font-mono bg-slate-100 hover:bg-slate-200 text-slate-700 dark:bg-slate-800 dark:hover:bg-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 transition-colors cursor-pointer"
                      >
                        <span>{chip.target}</span>
                        <span className="text-[10px] text-slate-400 ml-1">[{chip.type}]</span>
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* 4 Recon Workflows Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-xs space-y-2">
                  <div className="flex items-center gap-2.5 text-indigo-600 dark:text-indigo-400">
                    <Globe className="w-5 h-5" />
                    <h4 className="text-sm font-bold text-slate-900 dark:text-white">Domain & Network Footprint</h4>
                  </div>
                  <p className="text-xs text-slate-600 dark:text-slate-400">
                    Maps top-level domain records, authoritative DNS servers, mail exchanges, Certificate Transparency subdomains, and historical WHOIS ownership.
                  </p>
                  <div className="text-[10px] font-mono text-slate-400 flex items-center gap-2 pt-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                    <span>DNS • RDAP • crt.sh • Amass • Subfinder</span>
                  </div>
                </div>

                <div className="p-5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-xs space-y-2">
                  <div className="flex items-center gap-2.5 text-blue-600 dark:text-blue-400">
                    <Server className="w-5 h-5" />
                    <h4 className="text-sm font-bold text-slate-900 dark:text-white">Host & Infrastructure Census</h4>
                  </div>
                  <p className="text-xs text-slate-600 dark:text-slate-400">
                    Scans exposed open ports, detects banners, validates ASN routing blocks, and resolves physical IP geographic origin without active intrusion.
                  </p>
                  <div className="text-[10px] font-mono text-slate-400 flex items-center gap-2 pt-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
                    <span>Shodan InternetDB • IP-API • BGP ASN</span>
                  </div>
                </div>

                <div className="p-5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-xs space-y-2">
                  <div className="flex items-center gap-2.5 text-purple-600 dark:text-purple-400">
                    <User className="w-5 h-5" />
                    <h4 className="text-sm font-bold text-slate-900 dark:text-white">Identity & Username Recon</h4>
                  </div>
                  <p className="text-xs text-slate-600 dark:text-slate-400">
                    Cross-references handles across 335+ public services, developer portals, GitHub/GitLab commits, and online presence registers.
                  </p>
                  <div className="text-[10px] font-mono text-slate-400 flex items-center gap-2 pt-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-purple-500" />
                    <span>WhatsMyName • Gravatar • Public API Queries</span>
                  </div>
                </div>

                <div className="p-5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-xs space-y-2">
                  <div className="flex items-center gap-2.5 text-amber-600 dark:text-amber-400">
                    <Mail className="w-5 h-5" />
                    <h4 className="text-sm font-bold text-slate-900 dark:text-white">Email & Threat Attribution</h4>
                  </div>
                  <p className="text-xs text-slate-600 dark:text-slate-400">
                    Inspects MX records, disposable domain blocklists, RFC syntax compliance, and associated corporate organizational presence.
                  </p>
                  <div className="text-[10px] font-mono text-slate-400 flex items-center gap-2 pt-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
                    <span>GLEIF LEI • SEC EDGAR • Carrier Lookup</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Results Overview */}
          {osintResults && (
            <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 space-y-4 shadow-xs">
              <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-800">
                <div className="flex items-center gap-2">
                  <Shield className="w-4 h-4 text-indigo-500" />
                  <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                    OSINT Findings for {osintResults.query}
                  </h3>
                </div>
                {onOpenInvestigation && (
                  <button
                    type="button"
                    onClick={() => onOpenInvestigation(osintResults.query, targetType, osintResults.search_id)}
                    className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-mono font-bold flex items-center gap-1.5 transition-all cursor-pointer"
                  >
                    <span>Promote to Investigation</span>
                    <ChevronRight className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>

              {/* Findings List */}
              <div className="space-y-2.5">
                {(osintResults.findings || []).length === 0 ? (
                  <div className="text-center py-8 text-xs text-slate-500 font-mono">
                    No matching OSINT findings returned for this query.
                  </div>
                ) : (
                  (osintResults.findings || []).map((finding: any, idx: number) => (
                    <div
                      key={idx}
                      className="p-3.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/40 space-y-1"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-xs text-slate-900 dark:text-white">
                          {finding.title || finding.summary}
                        </span>
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300 font-bold">
                          {finding.source || 'OSINT'}
                        </span>
                      </div>
                      <p className="text-xs text-slate-600 dark:text-slate-300">
                        {finding.description || finding.raw_reference}
                      </p>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>
      ) : (
        /* Tool Workbench Tab */
        <div className="space-y-4">
          <ToolGrid tools={osintTools} onRunTool={(tool) => setSelectedTool(tool)} />
          {selectedTool && (
            <ToolRunModal
              tool={selectedTool}
              isOpen={Boolean(selectedTool)}
              onClose={() => setSelectedTool(null)}
            />
          )}
        </div>
      )}
    </div>
  );
};

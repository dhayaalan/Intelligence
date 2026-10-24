import React, { useState } from 'react';
import {
  ShieldAlert,
  Search,
  Server,
  Zap,
  Globe,
  FileCode,
  AlertTriangle,
  CheckCircle2,
  ExternalLink,
  RefreshCw,
  Terminal,
  Activity,
  Layers
} from 'lucide-react';
import { PageHeader } from '../../components/common/PageHeader';
import { apiRequest } from '../../core/api/client';
import { useTools, ToolItem } from '../../core/api/hooks';

interface ThreatScanResult {
  engine: string;
  target: string;
  status: 'completed' | 'failed' | 'running';
  summary?: string;
  findings: Array<{
    title: string;
    severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
    description: string;
    cve?: string;
    path?: string;
  }>;
  endpoints_discovered?: string[];
  duration_ms?: number;
}

export const ThreatIntelligencePage: React.FC = () => {
  const [target, setTarget] = useState('');
  const [scanType, setScanType] = useState<'zap' | 'openapi' | 'ports' | 'cve'>('zap');
  const [isScanning, setIsScanning] = useState(false);
  const [scanResults, setScanResults] = useState<ThreatScanResult[]>([]);
  const [selectedResult, setSelectedResult] = useState<ThreatScanResult | null>(null);

  const { data: tools = [] } = useTools();
  const threatTools = tools.filter((t) => t.category === 'Threat Intelligence' || t.category === 'threat_intelligence');

  const handleRunScan = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!target.trim()) return;

    setIsScanning(true);
    const startTime = Date.now();

    try {
      // Execute scan through backend search or tools API
      const res = await apiRequest<any>('/search', {
        method: 'POST',
        body: JSON.stringify({
          query: target.trim(),
          modules: ['threat_intelligence'],
        }),
      });

      const findings = (res?.findings || []).map((f: any) => ({
        title: f.title || f.summary || 'Discovered Threat Indicator',
        severity: (f.severity || 'medium').toLowerCase() as any,
        description: f.description || f.raw_reference || 'Observed during automated threat reconnaissance.',
        cve: f.cve_id || (f.metadata && f.metadata.cve),
        path: f.path || (f.metadata && f.metadata.url),
      }));

      const newResult: ThreatScanResult = {
        engine: scanType.toUpperCase() + ' Attack Surface Engine',
        target: target.trim(),
        status: 'completed',
        summary: `Discovered ${findings.length} findings across target infrastructure.`,
        findings,
        endpoints_discovered: res?.endpoints || [],
        duration_ms: Date.now() - startTime,
      };

      setScanResults((prev) => [newResult, ...prev]);
      setSelectedResult(newResult);
    } catch (err: any) {
      const failedResult: ThreatScanResult = {
        engine: scanType.toUpperCase() + ' Attack Surface Engine',
        target: target.trim(),
        status: 'failed',
        summary: err?.message || 'Threat reconnaissance failed or target host refused connection.',
        findings: [],
        duration_ms: Date.now() - startTime,
      };
      setScanResults((prev) => [failedResult, ...prev]);
      setSelectedResult(failedResult);
    } finally {
      setIsScanning(false);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto bg-slate-50 dark:bg-[#070b13] p-4 sm:p-6 lg:p-8 space-y-6">
      <PageHeader
        title="Threat Intelligence & Attack Surface Recon"
        description="Autonomous vulnerability discovery, OWASP ZAP crawling, exposed OpenAPI schema parsing, active service detection, and CVE vulnerability correlation."
      />

      {/* Target Intake & Engine Selection */}
      <div className="p-5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-xs">
        <form onSubmit={handleRunScan} className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
              <input
                type="text"
                value={target}
                onChange={(e) => setTarget(e.target.value)}
                placeholder="Target URL, domain, or IP address (e.g., https://api.target.com or 192.168.1.1)..."
                className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/80 text-sm font-mono text-slate-900 dark:text-white placeholder-slate-400 focus:outline-hidden focus:ring-2 focus:ring-rose-500 focus:border-rose-500 transition-all"
              />
            </div>
            <button
              type="submit"
              disabled={isScanning || !target.trim()}
              className="px-5 py-2.5 rounded-lg bg-rose-600 hover:bg-rose-500 disabled:opacity-50 text-white font-medium text-sm flex items-center justify-center gap-2 transition-all cursor-pointer shadow-xs shadow-rose-600/20"
            >
              {isScanning ? <RefreshCw className="w-4 h-4 animate-spin" /> : <ShieldAlert className="w-4 h-4" />}
              <span>{isScanning ? 'Executing Recon...' : 'Launch Threat Scan'}</span>
            </button>
          </div>

          {/* Engine Selector */}
          <div className="flex items-center gap-2 pt-1 overflow-x-auto text-xs font-mono">
            <span className="text-slate-500 font-semibold mr-1">ENGINE:</span>
            {[
              { id: 'zap', label: 'ZAP Crawler & Spider', icon: <Globe className="w-3.5 h-3.5" /> },
              { id: 'openapi', label: 'OpenAPI Schema Parser', icon: <FileCode className="w-3.5 h-3.5" /> },
              { id: 'ports', label: 'Shodan Port Recon', icon: <Server className="w-3.5 h-3.5" /> },
              { id: 'cve', label: 'NVD / CVE Correlator', icon: <AlertTriangle className="w-3.5 h-3.5" /> },
            ].map((engine) => (
              <button
                key={engine.id}
                type="button"
                onClick={() => setScanType(engine.id as any)}
                className={`px-3 py-1.5 rounded-lg border transition-all flex items-center gap-1.5 cursor-pointer ${
                  scanType === engine.id
                    ? 'bg-rose-50 border-rose-300 text-rose-700 dark:bg-rose-950/40 dark:border-rose-800 dark:text-rose-300 font-bold'
                    : 'bg-slate-100/70 border-slate-200 text-slate-600 hover:bg-slate-200 dark:bg-slate-800/60 dark:border-slate-700/60 dark:text-slate-400'
                }`}
              >
                {engine.icon}
                <span>{engine.label}</span>
              </button>
            ))}
          </div>
        </form>
      </div>

      {/* Grid: Results Summary & Detailed Findings */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Prior Runs */}
        <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4 space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-slate-200 dark:border-slate-800">
            <h3 className="text-xs font-bold font-mono uppercase tracking-wider text-slate-500">
              Threat Execution History ({scanResults.length})
            </h3>
            <span className="text-[11px] text-slate-400 font-mono">33 Engines Ready</span>
          </div>

          {scanResults.length === 0 ? (
            <div className="text-center py-8 text-xs text-slate-500 font-mono">
              No active scans executed yet. Enter a target domain or IP above to initiate automated threat reconnaissance.
            </div>
          ) : (
            <div className="space-y-2">
              {scanResults.map((r, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => setSelectedResult(r)}
                  className={`w-full text-left p-3 rounded-lg border transition-all cursor-pointer ${
                    selectedResult === r
                      ? 'border-rose-500/50 bg-rose-50/50 dark:bg-rose-950/20 shadow-2xs'
                      : 'border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50'
                  }`}
                >
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="font-mono font-bold text-slate-900 dark:text-white truncate max-w-[180px]">
                      {r.target}
                    </span>
                    <span
                      className={`text-[10px] font-mono px-1.5 py-0.5 rounded font-bold uppercase ${
                        r.status === 'completed'
                          ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
                          : 'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300'
                      }`}
                    >
                      {r.status}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 font-mono truncate">{r.engine}</p>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Right Column: Detailed Findings */}
        <div className="lg:col-span-2 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-800">
            <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-rose-500" />
              <span>Inspection Findings & Discovered Endpoints</span>
            </h3>
            {selectedResult?.duration_ms && (
              <span className="text-xs font-mono text-slate-500">
                Completed in {(selectedResult.duration_ms / 1000).toFixed(2)}s
              </span>
            )}
          </div>

          {!selectedResult ? (
            <div className="text-center py-16 text-slate-400 text-xs font-mono">
              Select or execute a scan to inspect discovered endpoints, headers, and correlated vulnerabilities.
            </div>
          ) : selectedResult.status === 'failed' ? (
            <div className="p-4 rounded-xl border border-rose-200 bg-rose-50/50 dark:border-rose-900/60 dark:bg-rose-950/20 text-rose-800 dark:text-rose-300 text-xs font-mono">
              {selectedResult.summary}
            </div>
          ) : selectedResult.findings.length === 0 ? (
            <div className="text-center py-12 text-slate-500 text-xs font-mono space-y-2">
              <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto" />
              <p>Reconnaissance completed with zero open vulnerabilities detected for target.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {selectedResult.findings.map((finding, idx) => (
                <div
                  key={idx}
                  className="p-3.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/40 space-y-1.5"
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-semibold text-xs text-slate-900 dark:text-white">{finding.title}</span>
                    <span
                      className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold uppercase ${
                        finding.severity === 'critical'
                          ? 'bg-purple-100 text-purple-800 dark:bg-purple-950 dark:text-purple-300'
                          : finding.severity === 'high'
                          ? 'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300'
                          : finding.severity === 'medium'
                          ? 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300'
                          : 'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300'
                      }`}
                    >
                      {finding.severity}
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 dark:text-slate-300">{finding.description}</p>
                  {finding.path && (
                    <div className="text-[11px] font-mono text-slate-500 flex items-center gap-1.5 pt-1">
                      <span className="text-slate-400">Path:</span>
                      <code className="text-rose-600 dark:text-rose-400 bg-slate-100 dark:bg-slate-900 px-1 py-0.5 rounded">
                        {finding.path}
                      </code>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

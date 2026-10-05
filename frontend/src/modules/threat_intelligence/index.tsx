import React from 'react';
import { frontendModuleRegistry, ModuleSearchResultProps, ModuleEntityPanelProps } from '../../core/module_sdk';
import { ShieldAlert, Bug, Activity, Server } from 'lucide-react';

export const ThreatIntelSearchResult: React.FC<ModuleSearchResultProps> = ({ searchResult, moduleEntities, moduleEvidence }) => {
  const vulns = moduleEntities.filter((e) => e.type === 'vulnerability');
  const iocs = moduleEntities.filter((e) => e.type === 'threat_indicator');
  const ips = moduleEntities.filter((e) => e.type === 'ip');
  const services = moduleEntities.filter((e) => e.type === 'technology');

  return (
    <div className="bg-surface-100 border border-surface-border rounded-xl p-5 shadow-sm space-y-4">
      <div className="flex items-center justify-between border-b border-surface-border pb-3">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-rose-500/10 border border-rose-500/30 flex items-center justify-center text-rose-400">
            <ShieldAlert className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-100 text-sm">Threat Intelligence & Attack Surface</h3>
            <p className="text-xs text-slate-400">Vulnerabilities, DNS telemetry, IOC feeds, and active service indicators</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {vulns.length > 0 && (
            <span className="text-xs px-2.5 py-1 bg-rose-500/10 border border-rose-500/30 text-rose-300 rounded-full font-mono">
              {vulns.length} CVEs Detected
            </span>
          )}
          <span className="text-xs px-2.5 py-1 bg-surface-200 border border-surface-border text-slate-300 rounded-full font-mono">
            {ips.length} IPs Resolved
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {/* Identified CVE Vulnerabilities */}
        <div className="bg-surface-200 border border-surface-border rounded-lg p-3">
          <div className="flex items-center gap-2 text-xs font-medium text-rose-400 mb-2">
            <Bug className="w-3.5 h-3.5" />
            <span>CVE Exposures ({vulns.length})</span>
          </div>
          {vulns.length === 0 ? (
            <p className="text-xs text-slate-500 italic">No critical CVEs identified</p>
          ) : (
            <div className="space-y-1.5 max-h-32 overflow-y-auto">
              {vulns.map((v, idx) => (
                <div key={idx} className="text-xs font-mono bg-rose-950/30 border border-rose-900/50 px-2 py-1 rounded text-rose-200 flex justify-between items-center">
                  <span>{v.value}</span>
                  <span className="text-[10px] bg-rose-900/60 px-1 rounded text-rose-100">
                    CVSS {v.metadata?.cvss_score || 'High'}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Threat Indicators & IOCs */}
        <div className="bg-surface-200 border border-surface-border rounded-lg p-3">
          <div className="flex items-center gap-2 text-xs font-medium text-amber-400 mb-2">
            <Activity className="w-3.5 h-3.5" />
            <span>IOC Indicator Feeds ({iocs.length})</span>
          </div>
          {iocs.length === 0 ? (
            <p className="text-xs text-slate-500 italic">No suspicious IOC matches found</p>
          ) : (
            <div className="space-y-1.5 max-h-32 overflow-y-auto">
              {iocs.map((ioc, idx) => (
                <div key={idx} className="text-xs font-mono bg-amber-950/30 border border-amber-900/50 px-2 py-1 rounded text-amber-200">
                  <div className="font-semibold">{ioc.value}</div>
                  <div className="text-[10px] text-amber-400/80">{ioc.metadata?.malware_family || 'Threat Indicator'}</div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Exposed Network Services */}
        <div className="bg-surface-200 border border-surface-border rounded-lg p-3">
          <div className="flex items-center gap-2 text-xs font-medium text-slate-300 mb-2">
            <Server className="w-3.5 h-3.5 text-sky-400" />
            <span>Open Services & Ports ({services.length})</span>
          </div>
          {services.length === 0 ? (
            <p className="text-xs text-slate-500 italic">No open service ports reported</p>
          ) : (
            <div className="space-y-1.5 max-h-32 overflow-y-auto">
              {services.map((s, idx) => (
                <div key={idx} className="text-xs font-mono bg-surface-300 px-2 py-1 rounded text-slate-200 truncate">
                  {s.value}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export const ThreatIntelEntityDetail: React.FC<ModuleEntityPanelProps> = ({ entity }) => {
  return (
    <div className="text-xs space-y-2 p-3 bg-surface-200 rounded border border-surface-border">
      <div className="font-semibold text-rose-400">Threat Intelligence Assessment</div>
      <div className="flex justify-between">
        <span className="text-slate-400">Severity / CVSS:</span>
        <span className="font-mono text-slate-200">{entity.metadata?.cvss_score || 'Assessed'}</span>
      </div>
    </div>
  );
};

// Register Threat Intelligence module with frontend registry
export function registerThreatIntelModule() {
  frontendModuleRegistry.registerExtension({
    id: 'threat_intelligence',
    name: 'Threat Intelligence',
    badge: 'Threat Surface & IOCs',
    color: 'rose',
    iconName: 'ShieldAlert',
    SearchResultComponent: ThreatIntelSearchResult,
    EntityDetailComponent: ThreatIntelEntityDetail,
  });
}

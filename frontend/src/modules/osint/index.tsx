import React from 'react';
import { frontendModuleRegistry, ModuleSearchResultProps, ModuleEntityPanelProps } from '../../core/module_sdk';
import { Globe, Mail, Network, Search, ExternalLink } from 'lucide-react';

export const OsintSearchResult: React.FC<ModuleSearchResultProps> = ({ searchResult, moduleEntities, moduleEvidence }) => {
  const emails = moduleEntities.filter((e) => e.type === 'email');
  const subdomains = moduleEntities.filter((e) => e.type === 'subdomain');
  const orgs = moduleEntities.filter((e) => e.type === 'organization');

  return (
    <div className="bg-surface-100 border border-surface-border rounded-xl p-5 shadow-sm space-y-4">
      <div className="flex items-center justify-between border-b border-surface-border pb-3">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-sky-500/10 border border-sky-500/30 flex items-center justify-center text-sky-400">
            <Globe className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-100 text-sm">OSINT Reconnaissance Findings</h3>
            <p className="text-xs text-slate-400">Automated open-source intelligence collection & transform pivots</p>
          </div>
        </div>
        <span className="text-xs px-2.5 py-1 bg-sky-500/10 border border-sky-500/30 text-sky-300 rounded-full font-mono">
          {moduleEntities.length} entities discovered
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {/* Discovered Emails */}
        <div className="bg-surface-200 border border-surface-border rounded-lg p-3">
          <div className="flex items-center gap-2 text-xs font-medium text-slate-300 mb-2">
            <Mail className="w-3.5 h-3.5 text-sky-400" />
            <span>Public Emails ({emails.length})</span>
          </div>
          {emails.length === 0 ? (
            <p className="text-xs text-slate-500 italic">No public emails discovered</p>
          ) : (
            <div className="space-y-1.5 max-h-32 overflow-y-auto">
              {emails.map((e, idx) => (
                <div key={idx} className="text-xs font-mono bg-surface-300 px-2 py-1 rounded text-slate-200 truncate">
                  {e.value}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Subdomains & Infrastructure */}
        <div className="bg-surface-200 border border-surface-border rounded-lg p-3">
          <div className="flex items-center gap-2 text-xs font-medium text-slate-300 mb-2">
            <Network className="w-3.5 h-3.5 text-emerald-400" />
            <span>Exposed Hosts ({subdomains.length})</span>
          </div>
          {subdomains.length === 0 ? (
            <p className="text-xs text-slate-500 italic">No subdomains identified</p>
          ) : (
            <div className="space-y-1.5 max-h-32 overflow-y-auto">
              {subdomains.map((e, idx) => (
                <div key={idx} className="text-xs font-mono bg-surface-300 px-2 py-1 rounded text-slate-200 truncate flex items-center justify-between">
                  <span>{e.value}</span>
                  <span className="text-[10px] text-slate-400">{Math.round(e.confidence * 100)}%</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Organizations & Footprints */}
        <div className="bg-surface-200 border border-surface-border rounded-lg p-3">
          <div className="flex items-center gap-2 text-xs font-medium text-slate-300 mb-2">
            <Search className="w-3.5 h-3.5 text-amber-400" />
            <span>Entities & ASN ({orgs.length})</span>
          </div>
          {orgs.length === 0 ? (
            <p className="text-xs text-slate-500 italic">No organization records</p>
          ) : (
            <div className="space-y-1.5 max-h-32 overflow-y-auto">
              {orgs.map((e, idx) => (
                <div key={idx} className="text-xs bg-surface-300 px-2 py-1 rounded text-slate-200 truncate">
                  {e.value}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export const OsintEntityDetail: React.FC<ModuleEntityPanelProps> = ({ entity }) => {
  return (
    <div className="text-xs space-y-2 p-3 bg-surface-200 rounded border border-surface-border">
      <div className="font-semibold text-sky-400">OSINT Recon Attribution</div>
      <div className="flex gap-2">
        <span className="text-slate-400">Discovered via:</span>
        <span className="font-mono text-slate-200">{entity.sources.join(', ')}</span>
      </div>
    </div>
  );
};

// Register OSINT module with frontend registry
export function registerOsintModule() {
  frontendModuleRegistry.registerExtension({
    id: 'osint',
    name: 'OSINT Intelligence',
    badge: 'Recon & Footprints',
    color: 'sky',
    iconName: 'Globe',
    SearchResultComponent: OsintSearchResult,
    EntityDetailComponent: OsintEntityDetail,
  });
}

import React, { useState, useEffect } from 'react';
import { Shield, Building2, Users, Cpu, Activity, Settings, CheckCircle2, ToggleLeft, ToggleRight, Plus, RefreshCw, Key } from 'lucide-react';
import { ModuleRegistryItem, Tenant, User, AuditLog, ProviderMetadata, ProviderStats } from '../../types';
import { apiRequest } from '../../core/api/client';
import { Button } from '../../components/ui/Button';

export const SuperAdminWorkspace: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'modules' | 'providers' | 'tenants' | 'users' | 'audit'>('overview');
  const [modules, setModules] = useState<ModuleRegistryItem[]>([]);
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [providers, setProviders] = useState<ProviderMetadata[]>([]);
  const [providerStats, setProviderStats] = useState<ProviderStats | null>(null);
  const [providerSearch, setProviderSearch] = useState('');
  const [providerModuleFilter, setProviderModuleFilter] = useState<'ALL' | 'osint' | 'threat_intelligence'>('ALL');
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Tenant creation state
  const [newTenantName, setNewTenantName] = useState('');
  const [newTenantSlug, setNewTenantSlug] = useState('');
  const [selectedModules, setSelectedModules] = useState<string[]>(['osint', 'threat_intelligence']);

  const loadAllData = async () => {
    setIsRefreshing(true);
    try {
      const [modData, tenData, userData, auditData, provData, statsData] = await Promise.all([
        apiRequest<ModuleRegistryItem[]>('/modules'),
        apiRequest<Tenant[]>('/tenants'),
        apiRequest<User[]>('/users'),
        apiRequest<AuditLog[]>('/audit'),
        apiRequest<ProviderMetadata[]>('/providers?limit=500'),
        apiRequest<ProviderStats>('/providers/stats'),
      ]);
      setModules(modData);
      setTenants(tenData);
      setUsers(userData);
      setAuditLogs(auditData);
      setProviders(provData);
      setProviderStats(statsData);
    } catch (err) {
      console.error('Failed to load super admin data', err);
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleToggleProvider = async (providerId: string, currentEnabled: boolean) => {
    try {
      const updated = await apiRequest<ProviderMetadata>(`/providers/${providerId}/toggle`, {
        method: 'POST',
        body: JSON.stringify({ enabled: !currentEnabled }),
      });
      setProviders(providers.map((p) => (p.provider_id === providerId ? updated : p)));
    } catch (err) {
      console.error('Failed to toggle provider', err);
    }
  };

  useEffect(() => {
    loadAllData();
  }, []);

  const handleToggleModule = async (moduleId: string, currentEnabled: boolean) => {
    try {
      const updated = await apiRequest<ModuleRegistryItem>(`/modules/${moduleId}/toggle`, {
        method: 'POST',
        body: JSON.stringify({ enabled: !currentEnabled }),
      });
      setModules(modules.map((m) => (m.id === moduleId ? updated : m)));
    } catch (err) {
      console.error('Failed to toggle module', err);
    }
  };

  const handleCreateTenant = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTenantName.trim() || !newTenantSlug.trim()) return;

    try {
      const created = await apiRequest<Tenant>('/tenants', {
        method: 'POST',
        body: JSON.stringify({
          name: newTenantName.trim(),
          slug: newTenantSlug.trim(),
          entitled_modules: selectedModules,
        }),
      });
      setTenants([...tenants, created]);
      setNewTenantName('');
      setNewTenantSlug('');
    } catch (err) {
      console.error('Failed to create tenant', err);
    }
  };

  return (
    <div className="w-full space-y-6">
      {/* Top Banner */}
      <div className="bg-white dark:bg-[#0f1422] border border-slate-200/90 dark:border-slate-800 p-5 sm:p-6 rounded-2xl flex flex-wrap items-center justify-between gap-4 shadow-xs">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-400 text-xs font-mono mb-2">
            <Shield className="w-3.5 h-3.5" />
            <span>Super Administrator Mode</span>
          </div>
          <h1 className="text-xl font-bold text-slate-900 dark:text-white tracking-tight font-sans">
            Platform Administration Workspace
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Global multi-tenant governance, dynamic module registry lifecycle, and platform provider telemetry
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            onClick={loadAllData}
            disabled={isRefreshing}
            variant="secondary"
            size="md"
            className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700 shadow-xs"
          >
            <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${isRefreshing ? 'animate-spin' : ''}`} />
            <span>Refresh Telemetry</span>
          </Button>
        </div>
      </div>

      {/* Admin Navigation Tabs */}
      <div className="flex border-b border-slate-200/90 dark:border-slate-800 text-xs gap-1 overflow-x-auto">
        {[
          { id: 'overview', label: 'Platform Overview', icon: Activity },
          { id: 'modules', label: 'Module Registry', icon: Cpu },
          { id: 'providers', label: `Provider Registry (${providerStats?.total_providers || providers.length})`, icon: Settings },
          { id: 'tenants', label: 'Tenants & Licenses', icon: Building2 },
          { id: 'users', label: 'All Users', icon: Users },
          { id: 'audit', label: 'Audit Logs', icon: Key },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-4 py-2.5 font-medium flex items-center gap-2 border-b-2 transition-all whitespace-nowrap ${
                isActive
                  ? 'border-slate-900 text-slate-900 dark:border-white dark:text-white bg-slate-100/70 dark:bg-slate-800/40 rounded-t-lg'
                  : 'border-transparent text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab: Overview */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white dark:bg-[#0f1422] border border-slate-200/90 dark:border-slate-800 p-5 rounded-2xl shadow-xs space-y-2">
            <span className="text-xs text-slate-500 dark:text-slate-400">Active Tenants</span>
            <div className="text-2xl font-bold text-slate-900 dark:text-white">{tenants.length}</div>
            <div className="text-[11px] text-emerald-600 dark:text-emerald-400 font-medium">Multi-tenant isolated</div>
          </div>
          <div className="bg-white dark:bg-[#0f1422] border border-slate-200/90 dark:border-slate-800 p-5 rounded-2xl shadow-xs space-y-2">
            <span className="text-xs text-slate-500 dark:text-slate-400">Registered Modules</span>
            <div className="text-2xl font-bold text-slate-900 dark:text-white">{modules.length}</div>
            <div className="text-[11px] text-sky-600 dark:text-sky-400 font-medium">
              {modules.filter((m) => m.enabled).length} enabled platform-wide
            </div>
          </div>
          <div className="bg-white dark:bg-[#0f1422] border border-slate-200/90 dark:border-slate-800 p-5 rounded-2xl shadow-xs space-y-2">
            <span className="text-xs text-slate-500 dark:text-slate-400">Total Users</span>
            <div className="text-2xl font-bold text-slate-900 dark:text-white">{users.length}</div>
            <div className="text-[11px] text-slate-500 dark:text-slate-400 font-mono">4 RBAC roles configured</div>
          </div>
          <div className="bg-white dark:bg-[#0f1422] border border-slate-200/90 dark:border-slate-800 p-5 rounded-2xl shadow-xs space-y-2">
            <span className="text-xs text-slate-500 dark:text-slate-400">Audit Logs Recorded</span>
            <div className="text-2xl font-bold text-slate-900 dark:text-white">{auditLogs.length}</div>
            <div className="text-[11px] text-slate-500 dark:text-slate-400">Immutable trace events</div>
          </div>
        </div>
      )}

      {/* Tab: Module Registry */}
      {activeTab === 'modules' && (
        <div className="space-y-4">
          <div className="text-xs text-slate-500 dark:text-slate-400">
            Control platform intelligence modules independently. Disabling a module removes it from the search plan without impacting the rest of the SaaS platform.
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {modules.map((mod) => (
              <div
                key={mod.id}
                className="bg-white dark:bg-[#0f1422] border border-slate-200/90 dark:border-slate-800 rounded-2xl p-5 space-y-4 shadow-xs"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-slate-900 dark:text-white text-sm">{mod.name}</h3>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
                        v{mod.version}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">{mod.description}</p>
                  </div>

                  <button
                    onClick={() => handleToggleModule(mod.id, mod.enabled)}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors cursor-pointer ${
                      mod.enabled
                        ? 'bg-emerald-500/10 border border-emerald-500/30 text-emerald-600 dark:text-emerald-400'
                        : 'bg-rose-500/10 border border-rose-500/30 text-rose-600 dark:text-rose-400'
                    }`}
                  >
                    {mod.enabled ? (
                      <>
                        <ToggleRight className="w-4 h-4" />
                        <span>Enabled</span>
                      </>
                    ) : (
                      <>
                        <ToggleLeft className="w-4 h-4" />
                        <span>Disabled</span>
                      </>
                    )}
                  </button>
                </div>

                {/* Health & Providers */}
                <div className="bg-slate-50 dark:bg-slate-900/60 border border-slate-200/80 dark:border-slate-800 p-3 rounded-xl text-xs space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500 dark:text-slate-400">Lifecycle State:</span>
                    <span className="font-mono text-sky-600 dark:text-sky-400 uppercase text-[10px]">
                      {mod.lifecycle_state}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500 dark:text-slate-400">Health Status:</span>
                    <span className="font-mono text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>{mod.health_status}</span>
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500 dark:text-slate-400">Providers:</span>
                    <span className="font-mono text-slate-700 dark:text-slate-300">
                      {mod.providers.join(', ')}
                    </span>
                  </div>
                </div>

                {/* Dynamic Configuration Schema */}
                {mod.configuration_schema && mod.configuration_schema.length > 0 && (
                  <div className="border-t border-slate-200/80 dark:border-slate-800 pt-3 space-y-2">
                    <div className="text-[11px] font-semibold text-slate-700 dark:text-slate-300 uppercase">
                      Dynamic Schema Settings
                    </div>
                    <div className="space-y-1.5">
                      {mod.configuration_schema.map((field) => (
                        <div key={field.key} className="text-xs flex items-center justify-between text-slate-500 dark:text-slate-400">
                          <span>{field.label}:</span>
                          <span className="font-mono text-slate-700 dark:text-slate-300 text-[11px]">
                            {field.type === 'secret' ? '••••••••' : String(field.default ?? 'N/A')}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab: Provider Registry (368 Tools: 335 OSINT + 33 Threat Intel) */}
      {activeTab === 'providers' && (
        <div className="space-y-5">
          {/* Header & Stats Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white dark:bg-[#0f1422] border border-slate-200/90 dark:border-slate-800 p-4 rounded-2xl space-y-1 shadow-xs">
              <span className="text-[11px] text-slate-500 dark:text-slate-400 uppercase tracking-wider font-mono">Total Providers</span>
              <div className="text-2xl font-bold text-slate-900 dark:text-white">{providerStats?.total_providers || providers.length}</div>
              <div className="text-[11px] text-slate-500 dark:text-slate-400">100% pluggable adapters</div>
            </div>
            <div className="bg-white dark:bg-[#0f1422] border border-slate-200/90 dark:border-slate-800 p-4 rounded-2xl space-y-1 shadow-xs">
              <span className="text-[11px] text-slate-500 dark:text-slate-400 uppercase tracking-wider font-mono">OSINT Capabilities</span>
              <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">{providerStats?.total_osint_providers || 335}</div>
              <div className="text-[11px] text-slate-500 dark:text-slate-400">Platforms, engines & probers</div>
            </div>
            <div className="bg-white dark:bg-[#0f1422] border border-slate-200/90 dark:border-slate-800 p-4 rounded-2xl space-y-1 shadow-xs">
              <span className="text-[11px] text-slate-500 dark:text-slate-400 uppercase tracking-wider font-mono">Threat Intelligence</span>
              <div className="text-2xl font-bold text-sky-600 dark:text-sky-400">{providerStats?.total_threat_intel_providers || 33}</div>
              <div className="text-[11px] text-slate-500 dark:text-slate-400">Attack surface & security engines</div>
            </div>
            <div className="bg-white dark:bg-[#0f1422] border border-slate-200/90 dark:border-slate-800 p-4 rounded-2xl space-y-1 shadow-xs">
              <span className="text-[11px] text-slate-500 dark:text-slate-400 uppercase tracking-wider font-mono">System Health</span>
              <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400 flex items-center gap-1.5">
                <CheckCircle2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
                <span>{providerStats?.healthy_providers || providers.length} Ready</span>
              </div>
              <div className="text-[11px] text-slate-500 dark:text-slate-400">All integrations verified</div>
            </div>
          </div>

          {/* Search & Filter Toolbar */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-white dark:bg-[#0f1422] border border-slate-200/90 dark:border-slate-800 p-3.5 rounded-2xl shadow-xs">
            <div className="flex items-center gap-2 w-full sm:w-auto">
              <input
                type="text"
                placeholder="Search 368+ tools, capabilities, or platform names..."
                value={providerSearch}
                onChange={(e) => setProviderSearch(e.target.value)}
                className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 w-full sm:w-80 focus:outline-none focus:border-slate-400 dark:focus:border-slate-600 font-mono"
              />
            </div>

            <div className="flex items-center gap-1.5 w-full sm:w-auto overflow-x-auto">
              <button
                onClick={() => setProviderModuleFilter('ALL')}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors cursor-pointer ${
                  providerModuleFilter === 'ALL'
                    ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-950 shadow-xs'
                    : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                All ({providers.length})
              </button>
              <button
                onClick={() => setProviderModuleFilter('osint')}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors cursor-pointer ${
                  providerModuleFilter === 'osint'
                    ? 'bg-emerald-600 text-white shadow-xs'
                    : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                OSINT ({providers.filter((p) => p.module_id === 'osint').length})
              </button>
              <button
                onClick={() => setProviderModuleFilter('threat_intelligence')}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors cursor-pointer ${
                  providerModuleFilter === 'threat_intelligence'
                    ? 'bg-sky-600 text-white shadow-xs'
                    : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                Threat Intel ({providers.filter((p) => p.module_id === 'threat_intelligence').length})
              </button>
            </div>
          </div>

          {/* Providers Table */}
          <div className="bg-white dark:bg-[#0f1422] border border-slate-200/90 dark:border-slate-800 rounded-2xl overflow-hidden shadow-xs">
            <div className="overflow-x-auto max-h-[600px] overflow-y-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead className="bg-slate-50 dark:bg-slate-900/60 text-slate-500 dark:text-slate-400 uppercase text-[10px] tracking-wider sticky top-0 z-10 border-b border-slate-200/90 dark:border-slate-800 font-mono">
                  <tr>
                    <th className="py-2.5 px-4">Provider / Tool</th>
                    <th className="py-2.5 px-4">Module</th>
                    <th className="py-2.5 px-4">Category</th>
                    <th className="py-2.5 px-4">Supported Targets</th>
                    <th className="py-2.5 px-4">Status</th>
                    <th className="py-2.5 px-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200/80 dark:divide-slate-800 text-slate-700 dark:text-slate-300">
                  {providers
                    .filter((p) => {
                      if (providerModuleFilter !== 'ALL' && p.module_id !== providerModuleFilter) return false;
                      if (!providerSearch.trim()) return true;
                      const q = providerSearch.toLowerCase();
                      return (
                        p.name.toLowerCase().includes(q) ||
                        p.provider_id.toLowerCase().includes(q) ||
                        p.category.toLowerCase().includes(q) ||
                        p.capabilities.some((c) => c.toLowerCase().includes(q))
                      );
                    })
                    .slice(0, 150)
                    .map((p) => (
                      <tr key={p.provider_id} className="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors">
                        <td className="py-2.5 px-4">
                          <div className="font-semibold text-slate-900 dark:text-white">{p.name}</div>
                          <div className="text-[10px] font-mono text-slate-400">{p.provider_id}</div>
                        </td>
                        <td className="py-2.5 px-4">
                          <span
                            className={`inline-block px-2 py-0.5 rounded text-[10px] font-mono ${
                              p.module_id === 'osint'
                                ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20'
                                : 'bg-sky-500/10 text-sky-600 dark:text-sky-400 border border-sky-500/20'
                            }`}
                          >
                            {p.module_id === 'osint' ? 'OSINT' : 'Threat Intel'}
                          </span>
                        </td>
                        <td className="py-2.5 px-4">
                          <span className="text-[11px] text-slate-600 dark:text-slate-400">{p.category}</span>
                        </td>
                        <td className="py-2.5 px-4">
                          <div className="flex flex-wrap gap-1 max-w-xs">
                            {p.supported_targets.slice(0, 3).map((t) => (
                              <span key={t} className="px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 text-[10px] font-mono">
                                {t}
                              </span>
                            ))}
                            {p.supported_targets.length > 3 && (
                              <span className="text-[10px] text-slate-400 font-mono">
                                +{p.supported_targets.length - 3}
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="py-2.5 px-4">
                          <span className="inline-flex items-center gap-1 text-[11px] font-mono text-emerald-600 dark:text-emerald-400">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                            <span>{p.status}</span>
                          </span>
                        </td>
                        <td className="py-2.5 px-4 text-right">
                          <button
                            onClick={() => handleToggleProvider(p.provider_id, p.is_enabled)}
                            className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold transition-colors cursor-pointer ${
                              p.is_enabled
                                ? 'bg-emerald-500/10 border border-emerald-500/30 text-emerald-600 dark:text-emerald-400 hover:bg-emerald-500/20'
                                : 'bg-rose-500/10 border border-rose-500/30 text-rose-600 dark:text-rose-400 hover:bg-rose-500/20'
                            }`}
                          >
                            {p.is_enabled ? 'Enabled' : 'Disabled'}
                          </button>
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Tab: Tenants */}
      {activeTab === 'tenants' && (
        <div className="space-y-6">
          {/* Create Tenant Form */}
          <div className="bg-white dark:bg-[#0f1422] border border-slate-200/90 dark:border-slate-800 p-5 rounded-2xl space-y-3 shadow-xs">
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white">Provision New Tenant Organization</h3>
            <form onSubmit={handleCreateTenant} className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <input
                type="text"
                placeholder="Organization Name (e.g. Apex Cyber Threat Ops)"
                value={newTenantName}
                onChange={(e) => setNewTenantName(e.target.value)}
                className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3.5 py-2 text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:border-slate-400"
              />
              <input
                type="text"
                placeholder="Slug (e.g. apex-ops)"
                value={newTenantSlug}
                onChange={(e) => setNewTenantSlug(e.target.value)}
                className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3.5 py-2 text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:border-slate-400"
              />
              <button
                type="submit"
                className="bg-slate-900 hover:bg-slate-800 text-white dark:bg-white dark:text-slate-950 dark:hover:bg-slate-100 font-semibold text-xs rounded-xl py-2 transition-colors flex items-center justify-center gap-1.5 cursor-pointer shadow-xs"
              >
                <Plus className="w-4 h-4" />
                <span>Create Organization</span>
              </button>
            </form>
          </div>

          {/* Tenants List */}
          <div className="bg-white dark:bg-[#0f1422] border border-slate-200/90 dark:border-slate-800 rounded-2xl overflow-hidden shadow-xs">
            <table className="w-full text-left text-xs text-slate-700 dark:text-slate-300">
              <thead className="bg-slate-50 dark:bg-slate-900/60 text-slate-500 dark:text-slate-400 text-[10px] uppercase font-mono border-b border-slate-200/90 dark:border-slate-800">
                <tr>
                  <th className="py-3 px-4">Organization</th>
                  <th className="py-3 px-4">Tenant ID</th>
                  <th className="py-3 px-4">Entitled Modules</th>
                  <th className="py-3 px-4">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200/80 dark:divide-slate-800">
                {tenants.map((t) => (
                  <tr key={t.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 px-4 font-semibold text-slate-900 dark:text-white">{t.name}</td>
                    <td className="py-3 px-4 font-mono text-slate-500 dark:text-slate-400">{t.id}</td>
                    <td className="py-3 px-4">
                      <div className="flex gap-1.5 flex-wrap">
                        {t.entitled_modules.map((m) => (
                          <span
                            key={m}
                            className="px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 border border-slate-200/80 dark:border-slate-700 text-[10px] font-mono text-sky-600 dark:text-sky-400"
                          >
                            {m}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 text-[10px] font-medium">
                        {t.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab: Users */}
      {activeTab === 'users' && (
        <div className="bg-white dark:bg-[#0f1422] border border-slate-200/90 dark:border-slate-800 rounded-2xl overflow-hidden shadow-xs">
          <table className="w-full text-left text-xs text-slate-700 dark:text-slate-300">
            <thead className="bg-slate-50 dark:bg-slate-900/60 text-slate-500 dark:text-slate-400 text-[10px] uppercase font-mono border-b border-slate-200/90 dark:border-slate-800">
              <tr>
                <th className="py-3 px-4">Name & Email</th>
                <th className="py-3 px-4">Role</th>
                <th className="py-3 px-4">Tenant Scope</th>
                <th className="py-3 px-4">Assigned Modules</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200/80 dark:divide-slate-800">
              {users.map((u) => (
                <tr key={u.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors">
                  <td className="py-3 px-4">
                    <div className="font-semibold text-slate-900 dark:text-white">{u.name}</div>
                    <div className="text-[11px] text-slate-500 dark:text-slate-400 font-mono">{u.email}</div>
                  </td>
                  <td className="py-3 px-4 font-mono text-xs font-semibold text-sky-600 dark:text-sky-400">{u.role}</td>
                  <td className="py-3 px-4 font-mono text-slate-500 dark:text-slate-400 text-xs">{u.tenant_id}</td>
                  <td className="py-3 px-4">
                    <div className="flex gap-1 flex-wrap">
                      {u.assigned_modules.map((m) => (
                        <span key={m} className="px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-[10px] font-mono text-slate-700 dark:text-slate-300">
                          {m}
                        </span>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Tab: Audit */}
      {activeTab === 'audit' && (
        <div className="bg-white dark:bg-[#0f1422] border border-slate-200/90 dark:border-slate-800 rounded-2xl overflow-hidden shadow-xs">
          <table className="w-full text-left text-xs text-slate-700 dark:text-slate-300">
            <thead className="bg-slate-50 dark:bg-slate-900/60 text-slate-500 dark:text-slate-400 text-[10px] uppercase font-mono border-b border-slate-200/90 dark:border-slate-800">
              <tr>
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4">Action</th>
                <th className="py-3 px-4">User</th>
                <th className="py-3 px-4">Tenant</th>
                <th className="py-3 px-4">Target Resource</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200/80 dark:divide-slate-800">
              {auditLogs.map((l) => (
                <tr key={l.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors">
                  <td className="py-3 px-4 font-mono text-slate-500 dark:text-slate-400 text-[11px]">
                    {new Date(l.timestamp).toLocaleTimeString()}
                  </td>
                  <td className="py-3 px-4 font-mono font-semibold text-emerald-600 dark:text-emerald-400">{l.action}</td>
                  <td className="py-3 px-4 font-mono text-slate-700 dark:text-slate-300">{l.user_id}</td>
                  <td className="py-3 px-4 font-mono text-slate-500 dark:text-slate-400">{l.tenant_id}</td>
                  <td className="py-3 px-4 text-slate-600 dark:text-slate-400">
                    {l.resource_type}:{l.resource_id}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

import React, { useState, useEffect } from 'react';
import {
  Building,
  Users,
  UserPlus,
  Cpu,
  Activity,
  CheckSquare,
  Square,
  AlertCircle,
  Shield,
  Check,
} from 'lucide-react';
import { User, ModuleRegistryItem, AuditLog } from '../../types';
import { apiRequest } from '../../core/api/client';
import { useAuth } from '../../core/auth/AuthContext';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { Pagination } from '../../components/ui/Pagination';

export const TenantAdminWorkspace: React.FC = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'modules' | 'audit'>('overview');
  const [users, setUsers] = useState<User[]>([]);
  const [entitledModules, setEntitledModules] = useState<ModuleRegistryItem[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [userSearch, setUserSearch] = useState('');
  const [auditSearch, setAuditSearch] = useState('');

  // Pagination states
  const [userPage, setUserPage] = useState(1);
  const [userPageSize, setUserPageSize] = useState(10);
  const [auditPage, setAuditPage] = useState(1);
  const [auditPageSize, setAuditPageSize] = useState(15);

  // User creation form state
  const [newName, setNewName] = useState('');
  const [newEmail, setNewEmail] = useState('');
  const [newRole, setNewRole] = useState<'ANALYST' | 'USER'>('ANALYST');
  const [selectedModules, setSelectedModules] = useState<string[]>(['osint']);
  const [createSuccess, setCreateSuccess] = useState<string | null>(null);
  const [createError, setCreateError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const loadData = async () => {
    try {
      const [uData, mData, aData] = await Promise.all([
        apiRequest<User[]>('/users'),
        apiRequest<ModuleRegistryItem[]>('/modules'),
        apiRequest<AuditLog[]>('/audit'),
      ]);
      setUsers(uData);
      setEntitledModules(mData);
      setAuditLogs(aData);
    } catch (err) {
      console.error('Failed to load tenant admin data', err);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreateSuccess(null);
    setCreateError(null);

    if (!newEmail.trim() || !newName.trim()) return;

    setIsSubmitting(true);
    try {
      const created = await apiRequest<User>('/users', {
        method: 'POST',
        body: JSON.stringify({
          email: newEmail.trim(),
          name: newName.trim(),
          role: newRole,
          assigned_modules: selectedModules,
        }),
      });
      setUsers([...users, created]);
      setCreateSuccess(`Investigator account for ${created.name} (${created.email}) created successfully.`);
      setNewName('');
      setNewEmail('');
    } catch (err: any) {
      setCreateError(err.message || 'Failed to create user');
    } finally {
      setIsSubmitting(false);
    }
  };

  const toggleModuleSelection = (modId: string) => {
    if (selectedModules.includes(modId)) {
      setSelectedModules(selectedModules.filter((m) => m !== modId));
    } else {
      setSelectedModules([...selectedModules, modId]);
    }
  };

  const filteredUsers = users.filter(
    (u) =>
      u.name.toLowerCase().includes(userSearch.toLowerCase()) ||
      u.email.toLowerCase().includes(userSearch.toLowerCase()) ||
      u.role.toLowerCase().includes(userSearch.toLowerCase())
  );

  const filteredAuditLogs = auditLogs.filter(
    (l) =>
      l.action.toLowerCase().includes(auditSearch.toLowerCase()) ||
      l.user_id.toLowerCase().includes(auditSearch.toLowerCase()) ||
      l.resource_type.toLowerCase().includes(auditSearch.toLowerCase())
  );

  return (
    <div className="w-full space-y-6">
      {/* Header Banner */}
      <div className="bg-white dark:bg-[#0f1422] border border-slate-200/90 dark:border-slate-800 p-5 sm:p-6 rounded-2xl flex flex-wrap items-center justify-between gap-4 shadow-xs">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-700 dark:text-amber-300 text-xs font-mono mb-2">
            <Building className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" />
            <span>Organization Management</span>
            <span className="text-slate-400">•</span>
            <span className="text-amber-700 dark:text-amber-400 font-semibold">{user?.tenant_id}</span>
          </div>
          <h1 className="text-xl font-bold text-slate-900 dark:text-white tracking-tight font-sans">
            Tenant Administration Console
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Provision investigator accounts, allocate module permissions, and inspect tenant security audit records.
          </p>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex border-b border-slate-200/90 dark:border-slate-800 text-xs gap-1 overflow-x-auto">
        {[
          { id: 'overview', label: 'Organization Overview', icon: Activity },
          { id: 'users', label: 'Investigators & Access', count: users.length, icon: Users },
          { id: 'modules', label: 'Licensed Modules', count: entitledModules.length, icon: Cpu },
          { id: 'audit', label: 'Audit Trail', count: auditLogs.length, icon: Shield },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-4 py-2.5 font-medium flex items-center gap-2 border-b-2 transition-all cursor-pointer whitespace-nowrap ${
                isActive
                  ? 'border-slate-900 text-slate-900 dark:border-white dark:text-white bg-slate-100/70 dark:bg-slate-800/40 rounded-t-lg'
                  : 'border-transparent text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
              {tab.count !== undefined && (
                <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
                  {tab.count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* TAB 1: Organization Overview */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="bg-white dark:bg-[#0f1422] border border-slate-200/90 dark:border-slate-800 p-5 rounded-2xl shadow-xs space-y-1.5">
              <span className="text-xs font-mono uppercase text-slate-500 dark:text-slate-400">Active Team Members</span>
              <div className="text-2xl font-bold font-mono text-slate-900 dark:text-white">{users.length}</div>
              <div className="text-[11px] text-slate-500 dark:text-slate-400">Analysts & investigators in organization</div>
            </div>

            <div className="bg-white dark:bg-[#0f1422] border border-slate-200/90 dark:border-slate-800 p-5 rounded-2xl shadow-xs space-y-1.5">
              <span className="text-xs font-mono uppercase text-slate-500 dark:text-slate-400">Entitled Modules</span>
              <div className="text-2xl font-bold font-mono text-slate-900 dark:text-white">{entitledModules.length}</div>
              <div className="text-[11px] text-emerald-600 dark:text-emerald-400 flex items-center gap-1 font-medium">
                <Check className="w-3 h-3" /> Licensed under active subscription
              </div>
            </div>

            <div className="bg-white dark:bg-[#0f1422] border border-slate-200/90 dark:border-slate-800 p-5 rounded-2xl shadow-xs space-y-1.5">
              <span className="text-xs font-mono uppercase text-slate-500 dark:text-slate-400">Audit Events Recorded</span>
              <div className="text-2xl font-bold font-mono text-slate-900 dark:text-white">{auditLogs.length}</div>
              <div className="text-[11px] text-slate-500 dark:text-slate-400">Scoped strictly to current tenant isolation</div>
            </div>
          </div>

          {/* Quick Info Box */}
          <div className="bg-white dark:bg-[#0f1422] border border-slate-200/90 dark:border-slate-800 rounded-2xl p-5 space-y-2 shadow-xs">
            <h3 className="text-xs font-semibold text-slate-900 dark:text-white uppercase tracking-wider font-mono">
              Tenant RBAC Directives
            </h3>
            <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
              Tenant administrators have authority to invite investigators under role <span className="text-slate-900 dark:text-white font-mono font-semibold">ANALYST</span> or <span className="text-slate-900 dark:text-white font-mono font-semibold">USER</span>. Module access is strictly bounded by the organization's licensed subscription.
            </p>
          </div>
        </div>
      )}

      {/* TAB 2: Investigators & Access Allocation */}
      {activeTab === 'users' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Create User Form */}
          <div className="lg:col-span-5 bg-white dark:bg-[#0f1422] border border-slate-200/90 dark:border-slate-800 rounded-2xl p-5 space-y-4 shadow-xs">
            <div className="flex items-center gap-2 border-b border-slate-200/80 dark:border-slate-800 pb-3">
              <UserPlus className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              <h3 className="font-semibold text-slate-900 dark:text-white text-sm">Provision Investigator Account</h3>
            </div>

            {createSuccess && (
              <div className="p-3 bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-900/50 rounded-xl text-emerald-700 dark:text-emerald-300 text-xs flex items-center gap-2">
                <Check className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
                <span>{createSuccess}</span>
              </div>
            )}
            {createError && (
              <div className="p-3 bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-900/50 rounded-xl text-rose-700 dark:text-rose-300 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-rose-600 dark:text-rose-400 shrink-0" />
                <span>{createError}</span>
              </div>
            )}

            <form onSubmit={handleCreateUser} className="space-y-4">
              <div>
                <label className="text-xs text-slate-600 dark:text-slate-400 block mb-1">Full Name</label>
                <input
                  type="text"
                  placeholder="e.g. John Doe"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  className="w-full h-9 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3 text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:border-slate-400 font-mono"
                />
              </div>

              <div>
                <label className="text-xs text-slate-600 dark:text-slate-400 block mb-1">Work Email</label>
                <input
                  type="email"
                  placeholder="e.g. j.doe@organization.com"
                  value={newEmail}
                  onChange={(e) => setNewEmail(e.target.value)}
                  className="w-full h-9 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3 text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:border-slate-400 font-mono"
                />
              </div>

              {/* Role Selection: STRICTLY Analyst or User */}
              <div>
                <label className="text-xs text-slate-600 dark:text-slate-400 block mb-1.5">Investigator Role</label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => setNewRole('ANALYST')}
                    className={`p-3 rounded-xl border text-left transition-all cursor-pointer ${
                      newRole === 'ANALYST'
                        ? 'bg-slate-100 dark:bg-slate-800 border-slate-900 dark:border-white text-slate-900 dark:text-white font-semibold shadow-xs'
                        : 'bg-slate-50 dark:bg-slate-900/60 border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                    }`}
                  >
                    <div className="text-xs font-semibold">Analyst</div>
                    <div className="text-[10px] text-slate-500 dark:text-slate-400 mt-0.5">Full search & investigation cases</div>
                  </button>

                  <button
                    type="button"
                    onClick={() => setNewRole('USER')}
                    className={`p-3 rounded-xl border text-left transition-all cursor-pointer ${
                      newRole === 'USER'
                        ? 'bg-slate-100 dark:bg-slate-800 border-slate-900 dark:border-white text-slate-900 dark:text-white font-semibold shadow-xs'
                        : 'bg-slate-50 dark:bg-slate-900/60 border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                    }`}
                  >
                    <div className="text-xs font-semibold">User</div>
                    <div className="text-[10px] text-slate-500 dark:text-slate-400 mt-0.5">Read-only investigation views</div>
                  </button>
                </div>
              </div>

              {/* Module Access Selection */}
              <div>
                <label className="text-xs text-slate-600 dark:text-slate-400 block mb-1.5">Module Entitlements</label>
                <div className="space-y-2 bg-slate-50 dark:bg-slate-900/60 p-3 rounded-xl border border-slate-200/80 dark:border-slate-800">
                  {entitledModules.map((mod) => (
                    <div
                      key={mod.id}
                      onClick={() => toggleModuleSelection(mod.id)}
                      className="flex items-center gap-2.5 text-xs text-slate-700 dark:text-slate-300 cursor-pointer select-none hover:text-slate-900 dark:hover:text-white"
                    >
                      {selectedModules.includes(mod.id) ? (
                        <CheckSquare className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                      ) : (
                        <Square className="w-4 h-4 text-slate-400" />
                      )}
                      <span className="font-medium">{mod.name}</span>
                    </div>
                  ))}
                </div>
              </div>

              <Button
                type="submit"
                variant="primary"
                size="md"
                isLoading={isSubmitting}
                className="w-full rounded-xl bg-slate-900 hover:bg-slate-800 text-white dark:bg-white dark:text-slate-950 dark:hover:bg-slate-100"
              >
                Provision Investigator
              </Button>
            </form>
          </div>

          {/* Users Table */}
          <div className="lg:col-span-7 bg-white dark:bg-[#0f1422] border border-slate-200/90 dark:border-slate-800 rounded-2xl overflow-hidden shadow-xs">
            <div className="p-4 border-b border-slate-200/80 dark:border-slate-800 flex items-center justify-between gap-4">
              <div className="flex items-center gap-2">
                <Users className="w-4 h-4 text-slate-500 dark:text-slate-400" />
                <h3 className="font-semibold text-sm text-slate-900 dark:text-white">Active Investigators ({users.length})</h3>
              </div>

              <div className="w-48">
                <input
                  type="text"
                  placeholder="Search team..."
                  value={userSearch}
                  onChange={(e) => setUserSearch(e.target.value)}
                  className="w-full h-8 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg px-2.5 text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none font-mono"
                />
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-700 dark:text-slate-300">
                <thead className="bg-slate-50 dark:bg-slate-900/60 text-slate-500 dark:text-slate-400 text-[10px] uppercase font-mono border-b border-slate-200/80 dark:border-slate-800">
                  <tr>
                    <th className="py-2.5 px-4 font-semibold">Investigator</th>
                    <th className="py-2.5 px-4 font-semibold">Role</th>
                    <th className="py-2.5 px-4 font-semibold">Assigned Modules</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200/80 dark:divide-slate-800">
                  {filteredUsers.length === 0 ? (
                    <tr>
                      <td colSpan={3} className="py-8 text-center text-slate-500 text-xs">
                        No team members match search query.
                      </td>
                    </tr>
                  ) : (
                    filteredUsers
                      .slice((userPage - 1) * userPageSize, userPage * userPageSize)
                      .map((u) => (
                        <tr key={u.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors">
                          <td className="py-2.5 px-4">
                            <div className="font-medium text-slate-900 dark:text-white">{u.name}</div>
                            <div className="text-[11px] text-slate-500 dark:text-slate-400 font-mono">{u.email}</div>
                          </td>
                          <td className="py-2.5 px-4">
                            <Badge variant={u.role === 'ANALYST' ? 'success' : 'info'} size="sm">
                              {u.role}
                            </Badge>
                          </td>
                          <td className="py-2.5 px-4">
                            <div className="flex gap-1 flex-wrap">
                              {u.assigned_modules.map((m) => (
                                <Badge key={m} variant="mono" size="sm">
                                  {m}
                                </Badge>
                              ))}
                            </div>
                          </td>
                        </tr>
                      ))
                  )}
                </tbody>
              </table>

              {/* Users Pagination */}
              {filteredUsers.length > userPageSize && (
                <div className="p-3 border-t border-slate-200/90 dark:border-slate-800">
                  <Pagination
                    currentPage={userPage}
                    totalPages={Math.max(1, Math.ceil(filteredUsers.length / userPageSize))}
                    totalItems={filteredUsers.length}
                    pageSize={userPageSize}
                    pageSizeOptions={[5, 10, 20, 50]}
                    onPageChange={setUserPage}
                    onPageSizeChange={(newSize) => {
                      setUserPageSize(newSize);
                      setUserPage(1);
                    }}
                  />
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: Licensed Modules */}
      {activeTab === 'modules' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {entitledModules.map((mod) => (
            <div key={mod.id} className="bg-white dark:bg-[#0f1422] border border-slate-200/90 dark:border-slate-800 rounded-2xl p-5 space-y-3 shadow-xs">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-slate-900 dark:text-white text-sm">{mod.name}</h3>
                <Badge variant="success" size="sm">
                  Active Subscription
                </Badge>
              </div>
              <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">{mod.description}</p>
              <div className="text-xs font-mono text-slate-500 dark:text-slate-400">
                Capabilities: {mod.capabilities.join(', ')}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* TAB 4: Organization Audit Trail */}
      {activeTab === 'audit' && (
        <div className="bg-white dark:bg-[#0f1422] border border-slate-200/90 dark:border-slate-800 rounded-2xl overflow-hidden shadow-xs space-y-0">
          <div className="p-4 border-b border-slate-200/80 dark:border-slate-800 flex items-center justify-between gap-4">
            <h3 className="font-semibold text-sm text-slate-900 dark:text-white">Tenant Security Audit Logs ({auditLogs.length})</h3>
            <div className="w-56">
              <input
                type="text"
                placeholder="Search audit trail..."
                value={auditSearch}
                onChange={(e) => {
                  setAuditSearch(e.target.value);
                  setAuditPage(1);
                }}
                className="w-full h-8 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg px-2.5 text-xs text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none font-mono"
              />
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-700 dark:text-slate-300">
              <thead className="bg-slate-50 dark:bg-slate-900/60 text-slate-500 dark:text-slate-400 text-[10px] uppercase font-mono border-b border-slate-200/80 dark:border-slate-800">
                <tr>
                  <th className="py-2.5 px-4 font-semibold">Timestamp</th>
                  <th className="py-2.5 px-4 font-semibold">Security Action</th>
                  <th className="py-2.5 px-4 font-semibold">User ID</th>
                  <th className="py-2.5 px-4 font-semibold">Target Resource</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200/80 dark:divide-slate-800">
                {filteredAuditLogs.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="py-8 text-center text-slate-500 text-xs">
                      No audit events matching criteria.
                    </td>
                  </tr>
                ) : (
                  filteredAuditLogs
                    .slice((auditPage - 1) * auditPageSize, auditPage * auditPageSize)
                    .map((l) => (
                      <tr key={l.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors">
                        <td className="py-2.5 px-4 font-mono text-slate-500 dark:text-slate-400 text-[11px]">
                          {new Date(l.timestamp).toLocaleTimeString()}
                        </td>
                        <td className="py-2.5 px-4 font-mono font-semibold text-emerald-600 dark:text-emerald-400">
                          {l.action}
                        </td>
                        <td className="py-2.5 px-4 font-mono text-slate-700 dark:text-slate-300">{l.user_id}</td>
                        <td className="py-2.5 px-4 text-slate-500 dark:text-slate-400 font-mono text-[11px]">
                          {l.resource_type}:{l.resource_id}
                        </td>
                      </tr>
                    ))
                )}
              </tbody>
            </table>
          </div>

          {/* Audit Pagination */}
          {filteredAuditLogs.length > auditPageSize && (
            <div className="p-3 border-t border-slate-200/90 dark:border-slate-800">
              <Pagination
                currentPage={auditPage}
                totalPages={Math.max(1, Math.ceil(filteredAuditLogs.length / auditPageSize))}
                totalItems={filteredAuditLogs.length}
                pageSize={auditPageSize}
                pageSizeOptions={[10, 15, 30, 60]}
                onPageChange={setAuditPage}
                onPageSizeChange={(newSize) => {
                  setAuditPageSize(newSize);
                  setAuditPage(1);
                }}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
};

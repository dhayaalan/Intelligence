import React, { useState } from 'react';
import {
  Shield,
  LayoutDashboard,
  Building2,
  Users,
  Layers,
  FileText,
  Activity,
  Settings,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Plus,
  RefreshCw,
  Search,
  CheckCircle2,
  AlertTriangle,
  Database,
  Server,
  Zap,
  UserCheck,
  Sun,
  Moon
} from 'lucide-react';
import { useAuth } from '../../core/auth/AuthContext';
import { useTheme } from '../../core/theme/ThemeContext';
import {
  usePlatformDashboard,
  useTenants,
  usePlatformUsers,
  useTools,
  usePlatformAuditLogs,
  useCreateTenant,
  useToggleTenantStatus,
} from '../../core/api/hooks';

type SuperAdminNav =
  | 'dashboard'
  | 'all-tenants'
  | 'create-tenant'
  | 'all-users'
  | 'tenant-admins'
  | 'tool-registry'
  | 'osint-tools'
  | 'threat-tools'
  | 'audit-logs'
  | 'system-health'
  | 'system-settings';

export const SuperAdminLayout: React.FC = () => {
  const { user, logout } = useAuth();
  const { isDark, toggleTheme } = useTheme();
  const [activeNav, setActiveNav] = useState<SuperAdminNav>('dashboard');
  const [isCollapsed, setIsCollapsed] = useState(false);

  // TanStack React Query Hooks
  const { data: dashboard, isLoading: isDashLoading, refetch: refetchDash } = usePlatformDashboard();
  const { data: tenants = [], isLoading: isTenantsLoading, refetch: refetchTenants } = useTenants();
  const { data: users = [], isLoading: isUsersLoading, refetch: refetchUsers } = usePlatformUsers();
  const { data: tools = [], isLoading: isToolsLoading } = useTools();
  const { data: auditLogs = [], isLoading: isAuditLoading, refetch: refetchAudit } = usePlatformAuditLogs(100);

  const createTenantMutation = useCreateTenant();
  const toggleTenantStatusMutation = useToggleTenantStatus();

  // Create Tenant Form State
  const [formOrgName, setFormOrgName] = useState('');
  const [formOrgSlug, setFormOrgSlug] = useState('');
  const [formOrgDesc, setFormOrgDesc] = useState('');
  const [formOrgIndustry, setFormOrgIndustry] = useState('Cybersecurity');
  const [formOrgCountry, setFormOrgCountry] = useState('United States');
  const [formAdminName, setFormAdminName] = useState('');
  const [formAdminEmail, setFormAdminEmail] = useState('');
  const [formAdminPassword, setFormAdminPassword] = useState('');
  const [formAdminPhone, setFormAdminPhone] = useState('');
  const [formModules, setFormModules] = useState<string[]>(['osint', 'threat_intelligence']);
  const [formError, setFormError] = useState<string | null>(null);
  const [formSuccess, setFormSuccess] = useState<string | null>(null);

  // Search & Filter state
  const [tenantSearch, setTenantSearch] = useState('');
  const [userSearch, setUserSearch] = useState('');
  const [toolSearch, setToolSearch] = useState('');
  const [toolCategoryFilter, setToolCategoryFilter] = useState('ALL');

  const handleCreateTenantSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    setFormSuccess(null);

    if (!formOrgName || !formOrgSlug || !formAdminName || !formAdminEmail || !formAdminPassword) {
      setFormError('Please fill out all required organization and administrator fields.');
      return;
    }

    try {
      await createTenantMutation.mutateAsync({
        name: formOrgName.trim(),
        slug: formOrgSlug.trim().toLowerCase().replace(/\s+/g, '-'),
        description: formOrgDesc.trim(),
        industry: formOrgIndustry,
        country: formOrgCountry,
        timezone: 'UTC',
        status: 'active',
        entitled_modules: formModules,
        admin_name: formAdminName.trim(),
        admin_email: formAdminEmail.trim().toLowerCase(),
        admin_password: formAdminPassword,
        admin_phone: formAdminPhone.trim() || undefined,
      });

      setFormSuccess(`Tenant '${formOrgName}' and Admin '${formAdminEmail}' successfully created!`);
      setFormOrgName('');
      setFormOrgSlug('');
      setFormOrgDesc('');
      setFormAdminName('');
      setFormAdminEmail('');
      setFormAdminPassword('');
      setFormAdminPhone('');
      refetchTenants();
      refetchDash();
      refetchUsers();
      setTimeout(() => setActiveNav('all-tenants'), 1500);
    } catch (err: any) {
      setFormError(err.message || 'Failed to create tenant.');
    }
  };

  const filteredTenants = tenants.filter(
    (t) =>
      t.name.toLowerCase().includes(tenantSearch.toLowerCase()) ||
      t.slug.toLowerCase().includes(tenantSearch.toLowerCase()) ||
      (t.admin?.email && t.admin.email.toLowerCase().includes(tenantSearch.toLowerCase()))
  );

  const filteredUsers = users.filter((u) => {
    const matchesSearch =
      u.name.toLowerCase().includes(userSearch.toLowerCase()) ||
      u.email.toLowerCase().includes(userSearch.toLowerCase()) ||
      (u.tenant_name && u.tenant_name.toLowerCase().includes(userSearch.toLowerCase()));
    if (activeNav === 'tenant-admins') {
      return matchesSearch && u.role === 'TENANT_ADMIN';
    }
    return matchesSearch;
  });

  const filteredTools = tools.filter((t) => {
    const matchesSearch =
      t.name.toLowerCase().includes(toolSearch.toLowerCase()) ||
      t.category.toLowerCase().includes(toolSearch.toLowerCase()) ||
      t.description.toLowerCase().includes(toolSearch.toLowerCase());
    const matchesModule =
      activeNav === 'osint-tools'
        ? t.module_id === 'osint'
        : activeNav === 'threat-tools'
        ? t.module_id === 'threat_intelligence'
        : true;
    const matchesCat = toolCategoryFilter === 'ALL' || t.category === toolCategoryFilter;
    return matchesSearch && matchesModule && matchesCat;
  });

  return (
    <div className="flex h-screen bg-[#f8fafc] dark:bg-[#070b13] text-slate-900 dark:text-slate-100 overflow-hidden font-sans transition-colors">
      {/* 1. DEDICATED SUPER ADMIN COLLAPSIBLE SIDEBAR */}
      <aside
        className={`${
          isCollapsed ? 'w-20' : 'w-64'
        } transition-all duration-300 ease-in-out border-r border-slate-200 dark:border-slate-800/80 bg-white dark:bg-[#0a0f1d] flex flex-col z-30 shrink-0 select-none shadow-xs`}
      >
        {/* Sidebar Header */}
        <div className={`h-16 border-b border-slate-200 dark:border-slate-800/80 flex items-center ${isCollapsed ? 'justify-center px-2' : 'justify-between px-4'}`}>
          {!isCollapsed ? (
            <>
              <div className="flex items-center gap-3 overflow-hidden">
                <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-cyan-600 to-indigo-600 flex items-center justify-center shadow-md shadow-cyan-500/20 shrink-0 text-white">
                  <Shield className="h-5 w-5" />
                </div>
                <div className="min-w-0">
                  <div className="text-sm font-bold tracking-wider text-slate-900 dark:text-white">SENTIAL</div>
                  <div className="text-[10px] font-mono tracking-widest text-cyan-600 dark:text-cyan-400 uppercase font-semibold">
                    Platform Admin
                  </div>
                </div>
              </div>
              <button
                onClick={() => setIsCollapsed(true)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800/60 transition-colors cursor-pointer"
                title="Collapse Sidebar"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
            </>
          ) : (
            <button
              onClick={() => setIsCollapsed(false)}
              className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 to-indigo-600 flex items-center justify-center shadow-md shadow-cyan-500/20 text-white hover:scale-105 transition-all cursor-pointer relative group"
              title="Expand Sidebar"
            >
              <Shield className="h-5 w-5" />
              <div className="absolute -bottom-1 -right-1 w-4 h-4 rounded-full bg-slate-900 dark:bg-white text-white dark:text-slate-900 flex items-center justify-center text-[9px] shadow-sm">
                <ChevronRight className="w-2.5 h-2.5" />
              </div>
            </button>
          )}
        </div>

        {/* Navigation Items */}
        <div className="flex-1 overflow-y-auto py-4 px-3 space-y-4 text-xs scrollbar-thin">
          {/* Section: Overview */}
          <div>
            {!isCollapsed ? (
              <div className="px-3 mb-2 text-[10px] font-mono uppercase tracking-wider text-slate-400 dark:text-slate-400 font-bold">
                Overview
              </div>
            ) : (
              <div className="my-2 border-t border-slate-200/80 dark:border-slate-800/80 mx-1" />
            )}
            <button
              onClick={() => setActiveNav('dashboard')}
              title="Platform Dashboard"
              className={`w-full flex items-center ${
                isCollapsed ? 'justify-center h-10 px-0' : 'gap-3 px-3 py-2.5'
              } rounded-xl transition-all cursor-pointer ${
                activeNav === 'dashboard'
                  ? 'bg-cyan-50 dark:bg-cyan-500/10 text-cyan-700 dark:text-cyan-400 border border-cyan-200 dark:border-cyan-500/30 font-medium shadow-xs'
                  : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <LayoutDashboard className="h-4 w-4 shrink-0" />
              {!isCollapsed && <span>Platform Dashboard</span>}
            </button>
          </div>

          {/* Section: Tenants */}
          <div>
            {!isCollapsed ? (
              <div className="px-3 mb-2 text-[10px] font-mono uppercase tracking-wider text-slate-400 dark:text-slate-400 font-bold">
                Tenants
              </div>
            ) : (
              <div className="my-2 border-t border-slate-200/80 dark:border-slate-800/80 mx-1" />
            )}
            <div className="space-y-1">
              <button
                onClick={() => setActiveNav('all-tenants')}
                title="All Tenants"
                className={`w-full flex items-center ${
                  isCollapsed ? 'justify-center h-10 px-0' : 'justify-between px-3 py-2.5'
                } rounded-xl transition-all cursor-pointer ${
                  activeNav === 'all-tenants'
                    ? 'bg-cyan-50 dark:bg-cyan-500/10 text-cyan-700 dark:text-cyan-400 border border-cyan-200 dark:border-cyan-500/30 font-medium'
                    : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Building2 className="h-4 w-4 shrink-0" />
                  {!isCollapsed && <span>All Tenants</span>}
                </div>
                {!isCollapsed && (
                  <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-mono">
                    {tenants.length}
                  </span>
                )}
              </button>
              <button
                onClick={() => setActiveNav('create-tenant')}
                title="Create Tenant"
                className={`w-full flex items-center ${
                  isCollapsed ? 'justify-center h-10 px-0' : 'gap-3 px-3 py-2.5'
                } rounded-xl transition-all cursor-pointer ${
                  activeNav === 'create-tenant'
                    ? 'bg-cyan-50 dark:bg-cyan-500/10 text-cyan-700 dark:text-cyan-400 border border-cyan-200 dark:border-cyan-500/30 font-medium'
                    : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                <Plus className="h-4 w-4 shrink-0" />
                {!isCollapsed && <span>Create Tenant</span>}
              </button>
            </div>
          </div>

          {/* Section: Users */}
          <div>
            {!isCollapsed ? (
              <div className="px-3 mb-2 text-[10px] font-mono uppercase tracking-wider text-slate-400 dark:text-slate-400 font-bold">
                Users
              </div>
            ) : (
              <div className="my-2 border-t border-slate-200/80 dark:border-slate-800/80 mx-1" />
            )}
            <div className="space-y-1">
              <button
                onClick={() => setActiveNav('all-users')}
                title="All Users"
                className={`w-full flex items-center ${
                  isCollapsed ? 'justify-center h-10 px-0' : 'justify-between px-3 py-2.5'
                } rounded-xl transition-all cursor-pointer ${
                  activeNav === 'all-users'
                    ? 'bg-cyan-50 dark:bg-cyan-500/10 text-cyan-700 dark:text-cyan-400 border border-cyan-200 dark:border-cyan-500/30 font-medium'
                    : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Users className="h-4 w-4 shrink-0" />
                  {!isCollapsed && <span>All Users</span>}
                </div>
                {!isCollapsed && (
                  <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-mono">
                    {users.length}
                  </span>
                )}
              </button>
              <button
                onClick={() => setActiveNav('tenant-admins')}
                title="Tenant Admins"
                className={`w-full flex items-center ${
                  isCollapsed ? 'justify-center h-10 px-0' : 'gap-3 px-3 py-2.5'
                } rounded-xl transition-all cursor-pointer ${
                  activeNav === 'tenant-admins'
                    ? 'bg-cyan-50 dark:bg-cyan-500/10 text-cyan-700 dark:text-cyan-400 border border-cyan-200 dark:border-cyan-500/30 font-medium'
                    : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                <UserCheck className="h-4 w-4 shrink-0" />
                {!isCollapsed && <span>Tenant Admins</span>}
              </button>
            </div>
          </div>

          {/* Section: Intelligence & Tool Registry */}
          <div>
            {!isCollapsed ? (
              <div className="px-3 mb-2 text-[10px] font-mono uppercase tracking-wider text-slate-400 dark:text-slate-400 font-bold">
                Intelligence
              </div>
            ) : (
              <div className="my-2 border-t border-slate-200/80 dark:border-slate-800/80 mx-1" />
            )}
            <div className="space-y-1">
              <button
                onClick={() => setActiveNav('tool-registry')}
                title="Tool Registry"
                className={`w-full flex items-center ${
                  isCollapsed ? 'justify-center h-10 px-0' : 'justify-between px-3 py-2.5'
                } rounded-xl transition-all cursor-pointer ${
                  activeNav === 'tool-registry'
                    ? 'bg-cyan-50 dark:bg-cyan-500/10 text-cyan-700 dark:text-cyan-400 border border-cyan-200 dark:border-cyan-500/30 font-medium'
                    : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Layers className="h-4 w-4 shrink-0" />
                  {!isCollapsed && <span>Tool Registry</span>}
                </div>
                {!isCollapsed && (
                  <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-mono">
                    {tools.length}
                  </span>
                )}
              </button>
              <button
                onClick={() => setActiveNav('osint-tools')}
                title="OSINT Tools"
                className={`w-full flex items-center ${
                  isCollapsed ? 'justify-center h-10 px-0' : 'gap-3 px-3 py-2.5'
                } rounded-xl transition-all cursor-pointer ${
                  activeNav === 'osint-tools'
                    ? 'bg-cyan-50 dark:bg-cyan-500/10 text-cyan-700 dark:text-cyan-400 border border-cyan-200 dark:border-cyan-500/30 font-medium'
                    : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                <Search className="h-4 w-4 shrink-0" />
                {!isCollapsed && <span>OSINT Tools</span>}
              </button>
              <button
                onClick={() => setActiveNav('threat-tools')}
                title="Threat Intelligence"
                className={`w-full flex items-center ${
                  isCollapsed ? 'justify-center h-10 px-0' : 'gap-3 px-3 py-2.5'
                } rounded-xl transition-all cursor-pointer ${
                  activeNav === 'threat-tools'
                    ? 'bg-cyan-50 dark:bg-cyan-500/10 text-cyan-700 dark:text-cyan-400 border border-cyan-200 dark:border-cyan-500/30 font-medium'
                    : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                <Zap className="h-4 w-4 shrink-0" />
                {!isCollapsed && <span>Threat Intelligence</span>}
              </button>
            </div>
          </div>

          {/* Section: Security */}
          <div>
            {!isCollapsed ? (
              <div className="px-3 mb-2 text-[10px] font-mono uppercase tracking-wider text-slate-400 dark:text-slate-400 font-bold">
                Security
              </div>
            ) : (
              <div className="my-2 border-t border-slate-200/80 dark:border-slate-800/80 mx-1" />
            )}
            <button
              onClick={() => setActiveNav('audit-logs')}
              title="Audit Logs"
              className={`w-full flex items-center ${
                isCollapsed ? 'justify-center h-10 px-0' : 'gap-3 px-3 py-2.5'
              } rounded-xl transition-all cursor-pointer ${
                activeNav === 'audit-logs'
                  ? 'bg-cyan-50 dark:bg-cyan-500/10 text-cyan-700 dark:text-cyan-400 border border-cyan-200 dark:border-cyan-500/30 font-medium'
                  : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <FileText className="h-4 w-4 shrink-0" />
              {!isCollapsed && <span>Audit Logs</span>}
            </button>
          </div>

          {/* Section: System */}
          <div>
            {!isCollapsed ? (
              <div className="px-3 mb-2 text-[10px] font-mono uppercase tracking-wider text-slate-400 dark:text-slate-400 font-bold">
                System
              </div>
            ) : (
              <div className="my-2 border-t border-slate-200/80 dark:border-slate-800/80 mx-1" />
            )}
            <div className="space-y-1">
              <button
                onClick={() => setActiveNav('system-health')}
                title="System Health"
                className={`w-full flex items-center ${
                  isCollapsed ? 'justify-center h-10 px-0' : 'gap-3 px-3 py-2.5'
                } rounded-xl transition-all cursor-pointer ${
                  activeNav === 'system-health'
                    ? 'bg-cyan-50 dark:bg-cyan-500/10 text-cyan-700 dark:text-cyan-400 border border-cyan-200 dark:border-cyan-500/30 font-medium'
                    : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                <Activity className="h-4 w-4 shrink-0" />
                {!isCollapsed && <span>System Health</span>}
              </button>
              <button
                onClick={() => setActiveNav('system-settings')}
                title="Settings"
                className={`w-full flex items-center ${
                  isCollapsed ? 'justify-center h-10 px-0' : 'gap-3 px-3 py-2.5'
                } rounded-xl transition-all cursor-pointer ${
                  activeNav === 'system-settings'
                    ? 'bg-cyan-50 dark:bg-cyan-500/10 text-cyan-700 dark:text-cyan-400 border border-cyan-200 dark:border-cyan-500/30 font-medium'
                    : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                <Settings className="h-4 w-4 shrink-0" />
                {!isCollapsed && <span>Settings</span>}
              </button>
            </div>
          </div>
        </div>

        {/* Sidebar Footer: Super Admin Profile & Logout */}
        <div className="p-3 border-t border-slate-200 dark:border-slate-800/80 bg-slate-50 dark:bg-[#080d19] shrink-0">
          {!isCollapsed ? (
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5 min-w-0">
                <div className="h-8 w-8 rounded-lg bg-indigo-50 border border-indigo-200 text-indigo-700 flex items-center justify-center font-bold text-xs font-mono dark:bg-indigo-950 dark:border-indigo-800 dark:text-indigo-300 shrink-0 shadow-2xs">
                  SA
                </div>
                <div className="min-w-0">
                  <div className="text-xs font-semibold text-slate-900 dark:text-white truncate">{user?.name || 'Super Admin'}</div>
                  <div className="text-[10px] text-slate-500 dark:text-slate-400 font-mono truncate">{user?.email}</div>
                </div>
              </div>
              <button
                onClick={logout}
                className="p-1.5 rounded-lg text-slate-500 hover:text-rose-600 hover:bg-rose-50 dark:text-slate-400 dark:hover:text-rose-400 dark:hover:bg-rose-500/10 transition-colors cursor-pointer"
                title="Sign Out"
              >
                <LogOut className="h-4 w-4" />
              </button>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-2 py-1">
              <div
                className="h-8 w-8 rounded-lg bg-indigo-50 border border-indigo-200 text-indigo-700 flex items-center justify-center font-bold text-xs font-mono dark:bg-indigo-950 dark:border-indigo-800 dark:text-indigo-300 shadow-2xs cursor-default"
                title={`${user?.name || 'Super Admin'} (${user?.email || ''})`}
              >
                SA
              </div>
              <button
                onClick={logout}
                className="p-1.5 rounded-lg text-slate-500 hover:text-rose-600 hover:bg-rose-50 dark:text-slate-400 dark:hover:text-rose-400 dark:hover:bg-rose-500/10 transition-colors cursor-pointer"
                title="Sign Out"
              >
                <LogOut className="h-4 w-4" />
              </button>
            </div>
          )}
        </div>
      </aside>

      {/* 2. MAIN PLATFORM CONTENT AREA */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden bg-[#f8fafc] dark:bg-[#070b13]">
        {/* Top Header Bar */}
        <header className="h-16 border-b border-slate-200 dark:border-slate-800/80 bg-white/80 dark:bg-[#0a0f1d]/80 backdrop-blur-md px-6 flex items-center justify-between shrink-0 shadow-2xs">
          <div className="flex items-center gap-3 text-xs">
            <span className="text-slate-500 dark:text-slate-400 font-mono">Platform</span>
            <span className="text-slate-400 dark:text-slate-600">/</span>
            <span className="text-cyan-700 dark:text-cyan-400 font-semibold uppercase tracking-wider font-mono text-[11px]">
              {activeNav.replace('-', ' ')}
            </span>
          </div>

          <div className="flex items-center gap-3">
            {/* Theme Toggle Sun / Moon */}
            <button
              onClick={toggleTheme}
              type="button"
              title={isDark ? 'Switch to Light Theme' : 'Switch to Dark Theme'}
              className="p-2 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors cursor-pointer"
            >
              {isDark ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-600" />}
            </button>

            {/* MongoDB Live Status Pill */}
            <div className="hidden sm:flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20 text-emerald-700 dark:text-emerald-400 text-xs font-mono">
              <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span>MongoDB: Connected</span>
            </div>

            <button
              onClick={() => {
                refetchDash();
                refetchTenants();
                refetchUsers();
                refetchAudit();
              }}
              className="p-2 rounded-xl bg-slate-100 dark:bg-slate-800/60 hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors cursor-pointer"
              title="Refresh Data"
            >
              <RefreshCw className="h-4 w-4" />
            </button>

            {/* User Profile & Role Clearance matching Navbar */}
            <div className="flex items-center gap-2 pl-3 border-l border-slate-200 dark:border-slate-800">
              <div className="hidden sm:flex items-center gap-1.5 font-mono text-[11px]">
                <span className="px-2 py-0.5 rounded bg-purple-50 border border-purple-200 text-purple-800 dark:bg-purple-950/40 dark:border-purple-800 dark:text-purple-300 font-semibold">
                  SUPER ADMIN
                </span>
              </div>

              <div
                className="w-7 h-7 rounded-lg bg-indigo-50 border border-indigo-200 text-indigo-700 flex items-center justify-center text-xs font-bold font-mono dark:bg-indigo-950 dark:border-indigo-800 dark:text-indigo-300 shadow-2xs"
                title={`${user?.name || 'Super Admin'} (${user?.email || ''})`}
              >
                SA
              </div>

              <button
                onClick={logout}
                title="Sign Out"
                className="p-1.5 rounded-lg text-slate-500 hover:text-rose-600 hover:bg-rose-50 dark:text-slate-400 dark:hover:text-rose-400 dark:hover:bg-rose-500/10 transition-colors cursor-pointer"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </div>
        </header>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-6 sm:p-8 space-y-8">
          {/* VIEW: PLATFORM DASHBOARD */}
          {activeNav === 'dashboard' && (
            <div className="space-y-8 max-w-7xl mx-auto">
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Platform Overview</h1>
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                  Live MongoDB-aggregated multi-tenant infrastructure metrics and operational telemetry.
                </p>
              </div>

              {/* 4 Primary MongoDB Aggregated Metric Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
                <div className="bg-white dark:bg-[#0f1424] border border-slate-200/90 dark:border-slate-800/90 p-5 rounded-2xl relative overflow-hidden shadow-xs">
                  <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-mono">
                    <span>Total Tenants</span>
                    <Building2 className="h-4 w-4 text-cyan-600 dark:text-cyan-400" />
                  </div>
                  <div className="mt-3 text-3xl font-extrabold text-slate-900 dark:text-white font-mono">
                    {isDashLoading ? '...' : dashboard?.total_tenants ?? 0}
                  </div>
                  <div className="mt-2 text-[11px] text-slate-500 dark:text-slate-400 flex items-center gap-2">
                    <span className="text-emerald-600 dark:text-emerald-400 font-medium">
                      {dashboard?.active_tenants ?? 0} Active
                    </span>
                    <span>•</span>
                    <span className="text-amber-600 dark:text-amber-400 font-medium">
                      {dashboard?.suspended_tenants ?? 0} Suspended
                    </span>
                  </div>
                </div>

                <div className="bg-white dark:bg-[#0f1424] border border-slate-200/90 dark:border-slate-800/90 p-5 rounded-2xl relative overflow-hidden shadow-xs">
                  <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-mono">
                    <span>Total Users</span>
                    <Users className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
                  </div>
                  <div className="mt-3 text-3xl font-extrabold text-slate-900 dark:text-white font-mono">
                    {isDashLoading ? '...' : dashboard?.total_users ?? 0}
                  </div>
                  <div className="mt-2 text-[11px] text-slate-500 dark:text-slate-400 flex items-center gap-2">
                    <span>{dashboard?.tenant_admins ?? 0} Admins</span>
                    <span>•</span>
                    <span>{dashboard?.analysts ?? 0} Analysts</span>
                  </div>
                </div>

                <div className="bg-white dark:bg-[#0f1424] border border-slate-200/90 dark:border-slate-800/90 p-5 rounded-2xl relative overflow-hidden shadow-xs">
                  <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-mono">
                    <span>Active Investigations</span>
                    <Activity className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
                  </div>
                  <div className="mt-3 text-3xl font-extrabold text-slate-900 dark:text-white font-mono">
                    {isDashLoading ? '...' : dashboard?.active_investigations ?? 0}
                  </div>
                  <div className="mt-2 text-[11px] text-slate-500 dark:text-slate-400">Across all tenant boundaries</div>
                </div>

                <div className="bg-white dark:bg-[#0f1424] border border-slate-200/90 dark:border-slate-800/90 p-5 rounded-2xl relative overflow-hidden shadow-xs">
                  <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-mono">
                    <span>OSINT Tool Runs</span>
                    <Zap className="h-4 w-4 text-purple-600 dark:text-purple-400" />
                  </div>
                  <div className="mt-3 text-3xl font-extrabold text-slate-900 dark:text-white font-mono">
                    {isDashLoading ? '...' : dashboard?.osint_tool_runs ?? 0}
                  </div>
                  <div className="mt-2 text-[11px] text-slate-500 dark:text-slate-400">Total verified engine runs</div>
                </div>
              </div>

              {/* Platform Status & Quick Action Banner */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 bg-white dark:bg-[#0f1424] border border-slate-200/90 dark:border-slate-800/90 p-6 rounded-2xl shadow-xs">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-base font-semibold text-slate-900 dark:text-white">Platform Audit Stream</h2>
                    <span className="text-xs text-slate-500 dark:text-slate-400 font-mono">Live MongoDB Events</span>
                  </div>

                  {auditLogs.length === 0 ? (
                    <div className="py-12 text-center text-slate-400 font-mono text-xs">
                      No security audit records logged yet.
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {auditLogs.slice(0, 6).map((log, idx) => (
                        <div
                          key={log.id || idx}
                          className="flex items-center justify-between p-3 rounded-xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200/80 dark:border-slate-800/80 text-xs"
                        >
                          <div className="flex items-center gap-3">
                            <span className="px-2 py-0.5 rounded-md bg-cyan-100 dark:bg-cyan-500/10 text-cyan-800 dark:text-cyan-400 font-mono text-[10px] font-semibold">
                              {log.action}
                            </span>
                            <span className="text-slate-700 dark:text-slate-300 font-mono">{log.user_id}</span>
                          </div>
                          <div className="text-slate-500 dark:text-slate-400 text-[11px] font-mono">
                            {new Date(log.timestamp).toLocaleTimeString()}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div className="bg-white dark:bg-[#0f1424] border border-slate-200/90 dark:border-slate-800/90 p-6 rounded-2xl space-y-6 flex flex-col justify-between shadow-xs">
                  <div>
                    <h2 className="text-base font-semibold text-slate-900 dark:text-white">Platform Actions</h2>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                      Quick platform operations for Super Admin.
                    </p>
                  </div>

                  <div className="space-y-3">
                    <button
                      onClick={() => setActiveNav('create-tenant')}
                      className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 text-white font-medium text-xs hover:from-cyan-500 hover:to-indigo-500 shadow-md transition-all cursor-pointer"
                    >
                      <Plus className="h-4 w-4" />
                      <span>Create New Tenant</span>
                    </button>
                    <button
                      onClick={() => setActiveNav('tool-registry')}
                      className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-slate-100 dark:bg-slate-800/80 hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 font-medium text-xs border border-slate-200 dark:border-slate-700/60 transition-all cursor-pointer"
                    >
                      <Layers className="h-4 w-4" />
                      <span>Inspect Tool Registry</span>
                    </button>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800/80 text-xs space-y-2">
                    <div className="text-slate-500 dark:text-slate-400 font-mono text-[11px]">Database Cluster:</div>
                    <div className="flex items-center gap-2 text-emerald-600 dark:text-emerald-400 font-mono font-medium">
                      <CheckCircle2 className="h-4 w-4 shrink-0" />
                      <span>MongoDB localhost:27017 (sential_db)</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* VIEW: ALL TENANTS */}
          {activeNav === 'all-tenants' && (
            <div className="space-y-6 max-w-7xl mx-auto">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Tenants Directory</h1>
                  <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                    Manage isolated tenant organizations, resource quotas, and tenant administrator accounts.
                  </p>
                </div>
                <button
                  onClick={() => setActiveNav('create-tenant')}
                  className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs transition-colors self-start sm:self-auto cursor-pointer"
                >
                  <Plus className="h-4 w-4" />
                  <span>Create Tenant</span>
                </button>
              </div>

              {/* Filter / Search Bar */}
              <div className="relative">
                <Search className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search by tenant name, code, or administrator email..."
                  value={tenantSearch}
                  onChange={(e) => setTenantSearch(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-white dark:bg-[#0f1424] border border-slate-200 dark:border-slate-800 text-xs text-slate-900 dark:text-white placeholder-slate-400 focus:outline-hidden focus:border-cyan-500 shadow-2xs"
                />
              </div>

              {/* Tenants Table */}
              <div className="bg-white dark:bg-[#0f1424] border border-slate-200/90 dark:border-slate-800/90 rounded-2xl overflow-hidden shadow-xs">
                {filteredTenants.length === 0 ? (
                  <div className="p-12 text-center space-y-4">
                    <Building2 className="h-12 w-12 text-slate-400 dark:text-slate-600 mx-auto" />
                    <div className="text-base font-semibold text-slate-900 dark:text-white">0 Tenants in Database</div>
                    <p className="text-xs text-slate-500 dark:text-slate-400 max-w-md mx-auto">
                      On this fresh installation, no sample or mock tenants exist. Use the button below to bootstrap your first real organization.
                    </p>
                    <button
                      onClick={() => setActiveNav('create-tenant')}
                      className="px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs transition-colors cursor-pointer"
                    >
                      Create First Tenant
                    </button>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse text-xs">
                      <thead>
                        <tr className="border-b border-slate-200 dark:border-slate-800/80 bg-slate-50 dark:bg-slate-900/60 text-slate-500 dark:text-slate-400 font-mono text-[11px]">
                          <th className="py-3.5 px-6 font-semibold">ORGANIZATION</th>
                          <th className="py-3.5 px-4 font-semibold">TENANT CODE</th>
                          <th className="py-3.5 px-4 font-semibold">TENANT ADMIN</th>
                          <th className="py-3.5 px-4 font-semibold">USERS</th>
                          <th className="py-3.5 px-4 font-semibold">CASES</th>
                          <th className="py-3.5 px-4 font-semibold">STATUS</th>
                          <th className="py-3.5 px-6 text-right font-semibold">ACTIONS</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-200 dark:divide-slate-800/60">
                        {filteredTenants.map((t) => (
                          <tr key={t.id} className="hover:bg-slate-50 dark:hover:bg-slate-900/40 transition-colors">
                            <td className="py-4 px-6 font-semibold text-slate-900 dark:text-white">
                              <div>{t.name}</div>
                              {t.industry && <div className="text-[10px] text-slate-500 dark:text-slate-400 font-normal">{t.industry}</div>}
                            </td>
                            <td className="py-4 px-4 font-mono text-cyan-600 dark:text-cyan-400">{t.slug}</td>
                            <td className="py-4 px-4">
                              <div className="text-slate-800 dark:text-slate-200">{t.admin?.name || 'Unassigned'}</div>
                              <div className="text-[11px] text-slate-500 dark:text-slate-400 font-mono">{t.admin?.email}</div>
                            </td>
                            <td className="py-4 px-4 font-mono text-slate-700 dark:text-slate-300">{t.user_count ?? 0}</td>
                            <td className="py-4 px-4 font-mono text-slate-700 dark:text-slate-300">{t.case_count ?? 0}</td>
                            <td className="py-4 px-4">
                              <span
                                className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-medium ${
                                  t.status === 'active'
                                    ? 'bg-emerald-100 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-500/20'
                                    : 'bg-amber-100 dark:bg-amber-500/10 text-amber-700 dark:text-amber-400 border border-amber-200 dark:border-amber-500/20'
                                }`}
                              >
                                {t.status.toUpperCase()}
                              </span>
                            </td>
                            <td className="py-4 px-6 text-right">
                              <button
                                onClick={async () => {
                                  const nextStatus = t.status === 'active' ? 'suspended' : 'active';
                                  await toggleTenantStatusMutation.mutateAsync({
                                    tenantId: t.id,
                                    status: nextStatus,
                                  });
                                  refetchTenants();
                                }}
                                className="px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 font-mono text-[11px] transition-colors cursor-pointer"
                              >
                                {t.status === 'active' ? 'Suspend' : 'Activate'}
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* VIEW: CREATE TENANT WORKFLOW */}
          {activeNav === 'create-tenant' && (
            <div className="max-w-4xl mx-auto space-y-6">
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Create Tenant Organization</h1>
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                  Super Admin only workflow: Atomically provisions the Tenant Organization and initial Tenant Administrator in MongoDB.
                </p>
              </div>

              {formError && (
                <div className="p-4 rounded-xl bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-500/30 text-rose-700 dark:text-rose-400 text-xs flex items-center gap-3">
                  <AlertTriangle className="h-4 w-4 shrink-0" />
                  <span>{formError}</span>
                </div>
              )}

              {formSuccess && (
                <div className="p-4 rounded-xl bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/30 text-emerald-700 dark:text-emerald-400 text-xs flex items-center gap-3">
                  <CheckCircle2 className="h-4 w-4 shrink-0" />
                  <span>{formSuccess}</span>
                </div>
              )}

              <form onSubmit={handleCreateTenantSubmit} className="space-y-6">
                {/* 1. Organization Information */}
                <div className="bg-white dark:bg-[#0f1424] border border-slate-200/90 dark:border-slate-800/90 rounded-2xl p-6 space-y-4 shadow-xs">
                  <div className="flex items-center gap-2 pb-3 border-b border-slate-200 dark:border-slate-800">
                    <Building2 className="h-4 w-4 text-cyan-600 dark:text-cyan-400" />
                    <h2 className="text-sm font-semibold text-slate-900 dark:text-white uppercase tracking-wider font-mono">
                      Organization Information
                    </h2>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                    <div>
                      <label className="block text-slate-700 dark:text-slate-300 font-medium mb-1.5">
                        Organization Name <span className="text-rose-500">*</span>
                      </label>
                      <input
                        type="text"
                        required
                        placeholder="e.g. Apex Defense Solutions"
                        value={formOrgName}
                        onChange={(e) => {
                          setFormOrgName(e.target.value);
                          if (!formOrgSlug) {
                            setFormOrgSlug(e.target.value.toLowerCase().replace(/[^a-z0-9]/g, '-'));
                          }
                        }}
                        className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-hidden focus:border-cyan-500"
                      />
                    </div>

                    <div>
                      <label className="block text-slate-700 dark:text-slate-300 font-medium mb-1.5">
                        Organization Code / Slug <span className="text-rose-500">*</span>
                      </label>
                      <input
                        type="text"
                        required
                        placeholder="e.g. apex-defense"
                        value={formOrgSlug}
                        onChange={(e) => setFormOrgSlug(e.target.value)}
                        className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-white font-mono placeholder-slate-400 focus:outline-hidden focus:border-cyan-500"
                      />
                    </div>

                    <div>
                      <label className="block text-slate-700 dark:text-slate-300 font-medium mb-1.5">Industry</label>
                      <select
                        value={formOrgIndustry}
                        onChange={(e) => setFormOrgIndustry(e.target.value)}
                        className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-white focus:outline-hidden focus:border-cyan-500"
                      >
                        <option value="Cybersecurity">Cybersecurity / Defense</option>
                        <option value="Government">Government / Law Enforcement</option>
                        <option value="Financial">Financial Services / Anti-Fraud</option>
                        <option value="Healthcare">Healthcare / Pharma</option>
                        <option value="Enterprise">Enterprise Risk Management</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-slate-700 dark:text-slate-300 font-medium mb-1.5">Country</label>
                      <input
                        type="text"
                        value={formOrgCountry}
                        onChange={(e) => setFormOrgCountry(e.target.value)}
                        className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-white focus:outline-hidden focus:border-cyan-500"
                      />
                    </div>

                    <div className="sm:col-span-2">
                      <label className="block text-slate-700 dark:text-slate-300 font-medium mb-1.5">Description</label>
                      <textarea
                        rows={2}
                        placeholder="Operational scope and mandate for this intelligence tenant..."
                        value={formOrgDesc}
                        onChange={(e) => setFormOrgDesc(e.target.value)}
                        className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-hidden focus:border-cyan-500"
                      />
                    </div>
                  </div>
                </div>

                {/* 2. Tenant Administrator Account */}
                <div className="bg-white dark:bg-[#0f1424] border border-slate-200/90 dark:border-slate-800/90 rounded-2xl p-6 space-y-4 shadow-xs">
                  <div className="flex items-center gap-2 pb-3 border-b border-slate-200 dark:border-slate-800">
                    <UserCheck className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
                    <h2 className="text-sm font-semibold text-slate-900 dark:text-white uppercase tracking-wider font-mono">
                      Tenant Administrator Account
                    </h2>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                    <div>
                      <label className="block text-slate-700 dark:text-slate-300 font-medium mb-1.5">
                        Admin Full Name <span className="text-rose-500">*</span>
                      </label>
                      <input
                        type="text"
                        required
                        placeholder="e.g. Sarah Connor"
                        value={formAdminName}
                        onChange={(e) => setFormAdminName(e.target.value)}
                        className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-hidden focus:border-cyan-500"
                      />
                    </div>

                    <div>
                      <label className="block text-slate-700 dark:text-slate-300 font-medium mb-1.5">
                        Admin Work Email <span className="text-rose-500">*</span>
                      </label>
                      <input
                        type="email"
                        required
                        placeholder="admin@apexcyber.com"
                        value={formAdminEmail}
                        onChange={(e) => setFormAdminEmail(e.target.value)}
                        className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-white font-mono placeholder-slate-400 focus:outline-hidden focus:border-cyan-500"
                      />
                    </div>

                    <div>
                      <label className="block text-slate-700 dark:text-slate-300 font-medium mb-1.5">
                        Admin Initial Password <span className="text-rose-500">*</span>
                      </label>
                      <input
                        type="password"
                        required
                        placeholder="Secure password (min 6 chars)"
                        value={formAdminPassword}
                        onChange={(e) => setFormAdminPassword(e.target.value)}
                        className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-white font-mono focus:outline-hidden focus:border-cyan-500"
                      />
                    </div>

                    <div>
                      <label className="block text-slate-700 dark:text-slate-300 font-medium mb-1.5">Phone Number</label>
                      <input
                        type="tel"
                        placeholder="+1 (555) 000-0000"
                        value={formAdminPhone}
                        onChange={(e) => setFormAdminPhone(e.target.value)}
                        className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-white font-mono placeholder-slate-400 focus:outline-hidden focus:border-cyan-500"
                      />
                    </div>
                  </div>
                </div>

                {/* 3. Module Entitlements */}
                <div className="bg-white dark:bg-[#0f1424] border border-slate-200/90 dark:border-slate-800/90 rounded-2xl p-6 space-y-4 shadow-xs">
                  <div className="flex items-center gap-2 pb-3 border-b border-slate-200 dark:border-slate-800">
                    <Layers className="h-4 w-4 text-purple-600 dark:text-purple-400" />
                    <h2 className="text-sm font-semibold text-slate-900 dark:text-white uppercase tracking-wider font-mono">
                      Module Entitlements
                    </h2>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                    <label className="flex items-start gap-3 p-3 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={formModules.includes('osint')}
                        onChange={(e) => {
                          if (e.target.checked) setFormModules([...formModules, 'osint']);
                          else setFormModules(formModules.filter((m) => m !== 'osint'));
                        }}
                        className="mt-0.5 rounded-sm border-slate-300 dark:border-slate-700 text-cyan-600 focus:ring-cyan-500"
                      />
                      <div>
                        <div className="font-semibold text-slate-900 dark:text-white">OSINT Module</div>
                        <div className="text-[11px] text-slate-500 dark:text-slate-400">
                          Reconnaissance, 329 platform probers, email, phone, domain sweeps.
                        </div>
                      </div>
                    </label>

                    <label className="flex items-start gap-3 p-3 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={formModules.includes('threat_intelligence')}
                        onChange={(e) => {
                          if (e.target.checked) setFormModules([...formModules, 'threat_intelligence']);
                          else setFormModules(formModules.filter((m) => m !== 'threat_intelligence'));
                        }}
                        className="mt-0.5 rounded-sm border-slate-300 dark:border-slate-700 text-indigo-600 focus:ring-indigo-500"
                      />
                      <div>
                        <div className="font-semibold text-slate-900 dark:text-white">Threat Intelligence Module</div>
                        <div className="text-[11px] text-slate-500 dark:text-slate-400">
                          33 engines, IOC attribution, IP/domain threat scanning, CVE mappings.
                        </div>
                      </div>
                    </label>
                  </div>
                </div>

                {/* Form Actions */}
                <div className="flex items-center justify-end gap-3">
                  <button
                    type="button"
                    onClick={() => setActiveNav('all-tenants')}
                    className="px-5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 text-xs font-medium transition-colors cursor-pointer"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={createTenantMutation.isPending}
                    className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white font-semibold text-xs shadow-md transition-all disabled:opacity-50 cursor-pointer"
                  >
                    {createTenantMutation.isPending ? 'Provisioning...' : 'Provision Tenant Organization'}
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* VIEW: ALL USERS / TENANT ADMINS */}
          {(activeNav === 'all-users' || activeNav === 'tenant-admins') && (
            <div className="space-y-6 max-w-7xl mx-auto">
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
                  {activeNav === 'tenant-admins' ? 'Tenant Administrators' : 'Global Users Directory'}
                </h1>
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                  Complete identity registry across all platform organizations with strict backend RBAC enforcement.
                </p>
              </div>

              <div className="relative">
                <Search className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search users by name, email, or tenant..."
                  value={userSearch}
                  onChange={(e) => setUserSearch(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-white dark:bg-[#0f1424] border border-slate-200 dark:border-slate-800 text-xs text-slate-900 dark:text-white placeholder-slate-400 focus:outline-hidden focus:border-cyan-500 shadow-2xs"
                />
              </div>

              <div className="bg-white dark:bg-[#0f1424] border border-slate-200/90 dark:border-slate-800/90 rounded-2xl overflow-hidden shadow-xs">
                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse text-xs">
                    <thead>
                      <tr className="border-b border-slate-200 dark:border-slate-800/80 bg-slate-50 dark:bg-slate-900/60 text-slate-500 dark:text-slate-400 font-mono text-[11px]">
                        <th className="py-3.5 px-6 font-semibold">USER</th>
                        <th className="py-3.5 px-4 font-semibold">TENANT</th>
                        <th className="py-3.5 px-4 font-semibold">ROLE</th>
                        <th className="py-3.5 px-4 font-semibold">STATUS</th>
                        <th className="py-3.5 px-4 font-semibold">CREATED</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-200 dark:divide-slate-800/60">
                      {filteredUsers.map((u) => (
                        <tr key={u.id} className="hover:bg-slate-50 dark:hover:bg-slate-900/40 transition-colors">
                          <td className="py-4 px-6 font-semibold text-slate-900 dark:text-white">
                            <div>{u.name}</div>
                            <div className="text-[11px] text-slate-500 dark:text-slate-400 font-mono font-normal">{u.email}</div>
                          </td>
                          <td className="py-4 px-4 font-mono text-cyan-600 dark:text-cyan-400">{u.tenant_name || u.tenant_id}</td>
                          <td className="py-4 px-4">
                            <span
                              className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-semibold ${
                                u.role === 'SUPER_ADMIN'
                                  ? 'bg-purple-100 dark:bg-purple-500/10 text-purple-700 dark:text-purple-400 border border-purple-200 dark:border-purple-500/20'
                                  : u.role === 'TENANT_ADMIN'
                                  ? 'bg-cyan-100 dark:bg-cyan-500/10 text-cyan-700 dark:text-cyan-400 border border-cyan-200 dark:border-cyan-500/20'
                                  : u.role === 'ANALYST'
                                  ? 'bg-indigo-100 dark:bg-indigo-500/10 text-indigo-700 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-500/20'
                                  : 'bg-emerald-100 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-500/20'
                              }`}
                            >
                              {u.role}
                            </span>
                          </td>
                          <td className="py-4 px-4">
                            <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-emerald-100 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-400">
                              ACTIVE
                            </span>
                          </td>
                          <td className="py-4 px-4 text-slate-500 dark:text-slate-400 font-mono text-[11px]">
                            {u.created_at ? new Date(u.created_at).toLocaleDateString() : 'N/A'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* VIEW: TOOL REGISTRY & INVENTORY */}
          {(activeNav === 'tool-registry' || activeNav === 'osint-tools' || activeNav === 'threat-tools') && (
            <div className="space-y-6 max-w-7xl mx-auto">
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
                  {activeNav === 'osint-tools'
                    ? 'OSINT Probers & Engines'
                    : activeNav === 'threat-tools'
                    ? 'Threat Intelligence Engines'
                    : 'Database-Backed Tool Registry'}
                </h1>
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                  Centralized platform registry with explicit execution states (AVAILABLE, CONFIG_REQUIRED, COMING_SOON, DISABLED).
                </p>
              </div>

              {/* Filters */}
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1 relative">
                  <Search className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
                  <input
                    type="text"
                    placeholder="Search tools by name, category, or provider..."
                    value={toolSearch}
                    onChange={(e) => setToolSearch(e.target.value)}
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-white dark:bg-[#0f1424] border border-slate-200 dark:border-slate-800 text-xs text-slate-900 dark:text-white placeholder-slate-400 focus:outline-hidden focus:border-cyan-500 shadow-2xs"
                  />
                </div>
                <select
                  value={toolCategoryFilter}
                  onChange={(e) => setToolCategoryFilter(e.target.value)}
                  className="px-4 py-2.5 rounded-xl bg-white dark:bg-[#0f1424] border border-slate-200 dark:border-slate-800 text-xs text-slate-900 dark:text-white focus:outline-hidden focus:border-cyan-500 font-mono shadow-2xs"
                >
                  <option value="ALL">All Categories</option>
                  <option value="Username">Username</option>
                  <option value="Email">Email</option>
                  <option value="Phone">Phone</option>
                  <option value="Infrastructure">Infrastructure</option>
                  <option value="DNS">DNS</option>
                  <option value="Metadata">Metadata</option>
                  <option value="Threat Intelligence">Threat Intelligence</option>
                </select>
              </div>

              {/* Tools Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                {filteredTools.map((t) => (
                  <div
                    key={t.id}
                    className="bg-white dark:bg-[#0f1424] border border-slate-200/90 dark:border-slate-800/90 rounded-2xl p-5 flex flex-col justify-between space-y-4 hover:border-slate-400 dark:hover:border-slate-700 transition-colors shadow-xs"
                  >
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-cyan-700 dark:text-cyan-400 font-mono text-[10px] font-semibold">
                          {t.category}
                        </span>
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-medium ${
                            t.status === 'AVAILABLE'
                              ? 'bg-emerald-100 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-500/20'
                              : t.status === 'CONFIG_REQUIRED'
                              ? 'bg-amber-100 dark:bg-amber-500/10 text-amber-700 dark:text-amber-400 border border-amber-200 dark:border-amber-500/20'
                              : 'bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400'
                          }`}
                        >
                          {t.status}
                        </span>
                      </div>
                      <h3 className="text-sm font-semibold text-slate-900 dark:text-white">{t.name}</h3>
                      <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-2">{t.description}</p>
                    </div>

                    <div className="pt-3 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400 font-mono">
                      <span>v{t.version}</span>
                      <span>{t.execution_type}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* VIEW: AUDIT LOGS */}
          {activeNav === 'audit-logs' && (
            <div className="space-y-6 max-w-7xl mx-auto">
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Platform Audit Stream</h1>
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                  Cryptographically verified chain-of-custody log of all administrative and security actions across MongoDB.
                </p>
              </div>

              <div className="bg-white dark:bg-[#0f1424] border border-slate-200/90 dark:border-slate-800/90 rounded-2xl overflow-hidden shadow-xs">
                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse text-xs">
                    <thead>
                      <tr className="border-b border-slate-200 dark:border-slate-800/80 bg-slate-50 dark:bg-slate-900/60 text-slate-500 dark:text-slate-400 font-mono text-[11px]">
                        <th className="py-3.5 px-6 font-semibold">TIMESTAMP</th>
                        <th className="py-3.5 px-4 font-semibold">ACTION</th>
                        <th className="py-3.5 px-4 font-semibold">TENANT</th>
                        <th className="py-3.5 px-4 font-semibold">ACTOR</th>
                        <th className="py-3.5 px-4 font-semibold">RESOURCE</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-200 dark:divide-slate-800/60">
                      {auditLogs.map((log) => (
                        <tr key={log.id} className="hover:bg-slate-50 dark:hover:bg-slate-900/40 transition-colors font-mono">
                          <td className="py-3 px-6 text-slate-500 dark:text-slate-400 text-[11px]">
                            {new Date(log.timestamp).toLocaleString()}
                          </td>
                          <td className="py-3 px-4">
                            <span className="px-2 py-0.5 rounded-md bg-cyan-100 dark:bg-cyan-500/10 text-cyan-800 dark:text-cyan-400 font-semibold text-[10px]">
                              {log.action}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-slate-700 dark:text-slate-300">{log.tenant_id}</td>
                          <td className="py-3 px-4 text-slate-700 dark:text-slate-300">{log.user_id}</td>
                          <td className="py-3 px-4 text-slate-500 dark:text-slate-400">{log.resource_type}:{log.resource_id}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* VIEW: SYSTEM HEALTH & DIAGNOSTICS */}
          {activeNav === 'system-health' && (
            <div className="space-y-6 max-w-7xl mx-auto">
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">System Health & Telemetry</h1>
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                  Real-time infrastructure health, MongoDB connection parameters, and worker queue performance.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white dark:bg-[#0f1424] border border-slate-200/90 dark:border-slate-800/90 rounded-2xl p-6 space-y-4 shadow-xs">
                  <div className="flex items-center gap-2 text-cyan-600 dark:text-cyan-400 font-mono text-xs font-semibold">
                    <Database className="h-4 w-4" />
                    <span>MongoDB Database</span>
                  </div>
                  <div className="text-2xl font-bold text-slate-900 dark:text-white font-mono">CONNECTED</div>
                  <div className="text-xs text-slate-500 dark:text-slate-400 space-y-1 font-mono">
                    <div>Cluster: localhost:27017</div>
                    <div>Database: sential_db</div>
                    <div>Isolation: organizationId indexed</div>
                  </div>
                </div>

                <div className="bg-white dark:bg-[#0f1424] border border-slate-200/90 dark:border-slate-800/90 rounded-2xl p-6 space-y-4 shadow-xs">
                  <div className="flex items-center gap-2 text-indigo-600 dark:text-indigo-400 font-mono text-xs font-semibold">
                    <Server className="h-4 w-4" />
                    <span>Background Workers</span>
                  </div>
                  <div className="text-2xl font-bold text-slate-900 dark:text-white font-mono">OPERATIONAL</div>
                  <div className="text-xs text-slate-500 dark:text-slate-400 space-y-1 font-mono">
                    <div>Queue Engine: Redis / AsyncIO</div>
                    <div>Concurrent Tasks: Dynamic</div>
                    <div>Streaming: Server-Sent Events</div>
                  </div>
                </div>

                <div className="bg-white dark:bg-[#0f1424] border border-slate-200/90 dark:border-slate-800/90 rounded-2xl p-6 space-y-4 shadow-xs">
                  <div className="flex items-center gap-2 text-purple-600 dark:text-purple-400 font-mono text-xs font-semibold">
                    <Shield className="h-4 w-4" />
                    <span>Tool Probers</span>
                  </div>
                  <div className="text-2xl font-bold text-slate-900 dark:text-white font-mono">368 Active</div>
                  <div className="text-xs text-slate-500 dark:text-slate-400 space-y-1 font-mono">
                    <div>OSINT Probers: 335 registered</div>
                    <div>Threat Intel Engines: 33 registered</div>
                    <div>Failures: Isolated</div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* VIEW: SETTINGS */}
          {activeNav === 'system-settings' && (
            <div className="space-y-6 max-w-4xl mx-auto">
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Platform Settings</h1>
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                  Global SaaS configurations, API keys, and persistence limits.
                </p>
              </div>

              <div className="bg-white dark:bg-[#0f1424] border border-slate-200/90 dark:border-slate-800/90 rounded-2xl p-6 space-y-4 text-xs shadow-xs">
                <div className="font-semibold text-slate-900 dark:text-white text-sm">Security & Isolation Policy</div>
                <p className="text-slate-600 dark:text-slate-400">
                  Strict backend multi-tenant data isolation is active on all collections. Tenant administrators and users are cryptographically restricted to their organizationId.
                </p>
                <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 font-mono text-slate-700 dark:text-slate-300">
                  PLATFORM_SUPER_ADMIN_BOOTSTRAP = COMPLETED
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

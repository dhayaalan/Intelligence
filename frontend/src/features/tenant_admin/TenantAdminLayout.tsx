import React, { useState } from 'react';
import {
  Building2,
  LayoutDashboard,
  Users,
  Briefcase,
  FolderOpen,
  FileText,
  Shield,
  Activity,
  LogOut,
  ChevronLeft,
  ChevronRight,
  RefreshCw,
  UserPlus,
  Lock,
  CheckCircle2,
  AlertTriangle,
  Layers,
  Fingerprint,
  Sun,
  Moon,
  Search
} from 'lucide-react';
import { useAuth } from '../../core/auth/AuthContext';
import { useTheme } from '../../core/theme/ThemeContext';
import {
  useDashboard,
  useUsers,
  useCases,
  useInvestigations,
  useEvidence,
  useFindings,
  useReports,
  useAuditLogs,
  useCreateUser
} from '../../core/api/hooks';

type TenantAdminNav =
  | 'dashboard'
  | 'members'
  | 'invite-user'
  | 'analysts'
  | 'investigators'
  | 'cases'
  | 'investigations'
  | 'evidence'
  | 'findings'
  | 'reports'
  | 'audit-logs';

export const TenantAdminLayout: React.FC = () => {
  const { user, logout } = useAuth();
  const { isDark, toggleTheme } = useTheme();
  const [activeNav, setActiveNav] = useState<TenantAdminNav>('dashboard');
  const [isCollapsed, setIsCollapsed] = useState(false);

  // TanStack React Query Hooks scoped to this tenant
  const { data: dashboard, isLoading: isDashLoading, refetch: refetchDash } = useDashboard();
  const { data: users = [], isLoading: isUsersLoading, refetch: refetchUsers } = useUsers(user?.tenant_id);
  const { data: cases = [], isLoading: isCasesLoading, refetch: refetchCases } = useCases();
  const { data: investigations = [], isLoading: isInvsLoading, refetch: refetchInvs } = useInvestigations();
  const { data: evidence = [], isLoading: isEvLoading } = useEvidence();
  const { data: findings = [], isLoading: isFindingsLoading } = useFindings();
  const { data: reports = [], isLoading: isReportsLoading } = useReports();
  const { data: auditLogs = [], isLoading: isAuditLoading } = useAuditLogs(50);

  const createUserMutation = useCreateUser();

  // Create User Form State
  const [formName, setFormName] = useState('');
  const [formEmail, setFormEmail] = useState('');
  const [formPassword, setFormPassword] = useState('');
  const [formRole, setFormRole] = useState<'ANALYST' | 'INVESTIGATOR' | 'USER'>('INVESTIGATOR');
  const [formError, setFormError] = useState<string | null>(null);
  const [formSuccess, setFormSuccess] = useState<string | null>(null);

  // Search filter
  const [userSearch, setUserSearch] = useState('');

  const handleCreateUserSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    setFormSuccess(null);

    if (!formName || !formEmail || !formPassword) {
      setFormError('Please fill out all required user fields.');
      return;
    }

    try {
      await createUserMutation.mutateAsync({
        name: formName.trim(),
        email: formEmail.trim().toLowerCase(),
        password: formPassword,
        role: formRole,
        assigned_modules: ['osint', 'threat_intelligence'],
      });

      setFormSuccess(`User '${formName}' (${formRole}) successfully created in your organization!`);
      setFormName('');
      setFormEmail('');
      setFormPassword('');
      refetchUsers();
      refetchDash();
      setTimeout(() => setActiveNav('members'), 1500);
    } catch (err: any) {
      setFormError(err.message || 'Failed to create organization user.');
    }
  };

  const filteredUsers = users.filter((u) => {
    const matches =
      u.name.toLowerCase().includes(userSearch.toLowerCase()) ||
      u.email.toLowerCase().includes(userSearch.toLowerCase());
    if (activeNav === 'analysts') return matches && u.role === 'ANALYST';
    if (activeNav === 'investigators') return matches && (u.role === 'INVESTIGATOR' || u.role === 'USER');
    return matches;
  });

  return (
    <div className="flex h-screen bg-[#f8fafc] dark:bg-[#070b13] text-slate-900 dark:text-slate-100 overflow-hidden font-sans transition-colors">
      {/* 1. DEDICATED TENANT ADMIN COLLAPSIBLE SIDEBAR */}
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
                <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-cyan-600 to-blue-700 flex items-center justify-center shadow-md shadow-cyan-500/20 shrink-0 text-white">
                  <Building2 className="h-5 w-5" />
                </div>
                <div className="min-w-0">
                  <div className="text-sm font-bold tracking-wider text-slate-900 dark:text-white">SENTIAL</div>
                  <div className="text-[10px] font-mono tracking-widest text-cyan-600 dark:text-cyan-400 uppercase font-semibold">
                    Organization Admin
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
              className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 to-blue-700 flex items-center justify-center shadow-md shadow-cyan-500/20 text-white hover:scale-105 transition-all cursor-pointer relative group"
              title="Expand Sidebar"
            >
              <Building2 className="h-5 w-5" />
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
              title="Dashboard"
              className={`w-full flex items-center ${
                isCollapsed ? 'justify-center h-10 px-0' : 'gap-3 px-3 py-2.5'
              } rounded-xl transition-all cursor-pointer ${
                activeNav === 'dashboard'
                  ? 'bg-cyan-50 dark:bg-cyan-500/10 text-cyan-700 dark:text-cyan-400 border border-cyan-200 dark:border-cyan-500/30 font-medium shadow-xs'
                  : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <LayoutDashboard className="h-4 w-4 shrink-0" />
              {!isCollapsed && <span>Dashboard</span>}
            </button>
          </div>

          {/* Section: Organization & Users */}
          <div>
            {!isCollapsed ? (
              <div className="px-3 mb-2 text-[10px] font-mono uppercase tracking-wider text-slate-400 dark:text-slate-400 font-bold">
                Organization & Users
              </div>
            ) : (
              <div className="my-2 border-t border-slate-200/80 dark:border-slate-800/80 mx-1" />
            )}
            <div className="space-y-1">
              <button
                onClick={() => setActiveNav('members')}
                title="Members"
                className={`w-full flex items-center ${
                  isCollapsed ? 'justify-center h-10 px-0' : 'justify-between px-3 py-2.5'
                } rounded-xl transition-all cursor-pointer ${
                  activeNav === 'members'
                    ? 'bg-cyan-50 dark:bg-cyan-500/10 text-cyan-700 dark:text-cyan-400 border border-cyan-200 dark:border-cyan-500/30 font-medium'
                    : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Users className="h-4 w-4 shrink-0" />
                  {!isCollapsed && <span>Members</span>}
                </div>
                {!isCollapsed && (
                  <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-mono">
                    {users.length}
                  </span>
                )}
              </button>
              <button
                onClick={() => setActiveNav('invite-user')}
                title="Create User"
                className={`w-full flex items-center ${
                  isCollapsed ? 'justify-center h-10 px-0' : 'gap-3 px-3 py-2.5'
                } rounded-xl transition-all cursor-pointer ${
                  activeNav === 'invite-user'
                    ? 'bg-cyan-50 dark:bg-cyan-500/10 text-cyan-700 dark:text-cyan-400 border border-cyan-200 dark:border-cyan-500/30 font-medium'
                    : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                <UserPlus className="h-4 w-4 shrink-0" />
                {!isCollapsed && <span>Create User</span>}
              </button>
              <button
                onClick={() => setActiveNav('analysts')}
                title="Analysts"
                className={`w-full flex items-center ${
                  isCollapsed ? 'justify-center h-10 px-0' : 'gap-3 px-3 py-2.5'
                } rounded-xl transition-all cursor-pointer ${
                  activeNav === 'analysts'
                    ? 'bg-cyan-50 dark:bg-cyan-500/10 text-cyan-700 dark:text-cyan-400 border border-cyan-200 dark:border-cyan-500/30 font-medium'
                    : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                <Briefcase className="h-4 w-4 shrink-0" />
                {!isCollapsed && <span>Analysts</span>}
              </button>
              <button
                onClick={() => setActiveNav('investigators')}
                title="Investigators"
                className={`w-full flex items-center ${
                  isCollapsed ? 'justify-center h-10 px-0' : 'gap-3 px-3 py-2.5'
                } rounded-xl transition-all cursor-pointer ${
                  activeNav === 'investigators'
                    ? 'bg-cyan-50 dark:bg-cyan-500/10 text-cyan-700 dark:text-cyan-400 border border-cyan-200 dark:border-cyan-500/30 font-medium'
                    : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                <Fingerprint className="h-4 w-4 shrink-0" />
                {!isCollapsed && <span>Investigators</span>}
              </button>
            </div>
          </div>

          {/* Section: Investigations */}
          <div>
            {!isCollapsed ? (
              <div className="px-3 mb-2 text-[10px] font-mono uppercase tracking-wider text-slate-400 dark:text-slate-400 font-bold">
                Investigations
              </div>
            ) : (
              <div className="my-2 border-t border-slate-200/80 dark:border-slate-800/80 mx-1" />
            )}
            <div className="space-y-1">
              <button
                onClick={() => setActiveNav('cases')}
                title="Cases"
                className={`w-full flex items-center ${
                  isCollapsed ? 'justify-center h-10 px-0' : 'justify-between px-3 py-2.5'
                } rounded-xl transition-all cursor-pointer ${
                  activeNav === 'cases'
                    ? 'bg-cyan-50 dark:bg-cyan-500/10 text-cyan-700 dark:text-cyan-400 border border-cyan-200 dark:border-cyan-500/30 font-medium'
                    : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                <div className="flex items-center gap-3">
                  <FolderOpen className="h-4 w-4 shrink-0" />
                  {!isCollapsed && <span>Cases</span>}
                </div>
                {!isCollapsed && (
                  <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-mono">
                    {cases.length}
                  </span>
                )}
              </button>
              <button
                onClick={() => setActiveNav('investigations')}
                title="Investigations"
                className={`w-full flex items-center ${
                  isCollapsed ? 'justify-center h-10 px-0' : 'justify-between px-3 py-2.5'
                } rounded-xl transition-all cursor-pointer ${
                  activeNav === 'investigations'
                    ? 'bg-cyan-50 dark:bg-cyan-500/10 text-cyan-700 dark:text-cyan-400 border border-cyan-200 dark:border-cyan-500/30 font-medium'
                    : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Activity className="h-4 w-4 shrink-0" />
                  {!isCollapsed && <span>Investigations</span>}
                </div>
                {!isCollapsed && (
                  <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-mono">
                    {investigations.length}
                  </span>
                )}
              </button>
              <button
                onClick={() => setActiveNav('evidence')}
                title="Evidence Vault"
                className={`w-full flex items-center ${
                  isCollapsed ? 'justify-center h-10 px-0' : 'justify-between px-3 py-2.5'
                } rounded-xl transition-all cursor-pointer ${
                  activeNav === 'evidence'
                    ? 'bg-cyan-50 dark:bg-cyan-500/10 text-cyan-700 dark:text-cyan-400 border border-cyan-200 dark:border-cyan-500/30 font-medium'
                    : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Shield className="h-4 w-4 shrink-0" />
                  {!isCollapsed && <span>Evidence Vault</span>}
                </div>
                {!isCollapsed && (
                  <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-mono">
                    {evidence.length}
                  </span>
                )}
              </button>
              <button
                onClick={() => setActiveNav('findings')}
                title="Findings"
                className={`w-full flex items-center ${
                  isCollapsed ? 'justify-center h-10 px-0' : 'justify-between px-3 py-2.5'
                } rounded-xl transition-all cursor-pointer ${
                  activeNav === 'findings'
                    ? 'bg-cyan-50 dark:bg-cyan-500/10 text-cyan-700 dark:text-cyan-400 border border-cyan-200 dark:border-cyan-500/30 font-medium'
                    : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Layers className="h-4 w-4 shrink-0" />
                  {!isCollapsed && <span>Findings</span>}
                </div>
                {!isCollapsed && (
                  <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-mono">
                    {findings.length}
                  </span>
                )}
              </button>
              <button
                onClick={() => setActiveNav('reports')}
                title="Reports"
                className={`w-full flex items-center ${
                  isCollapsed ? 'justify-center h-10 px-0' : 'justify-between px-3 py-2.5'
                } rounded-xl transition-all cursor-pointer ${
                  activeNav === 'reports'
                    ? 'bg-cyan-50 dark:bg-cyan-500/10 text-cyan-700 dark:text-cyan-400 border border-cyan-200 dark:border-cyan-500/30 font-medium'
                    : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                <div className="flex items-center gap-3">
                  <FileText className="h-4 w-4 shrink-0" />
                  {!isCollapsed && <span>Reports</span>}
                </div>
                {!isCollapsed && (
                  <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-mono">
                    {reports.length}
                  </span>
                )}
              </button>
            </div>
          </div>

          {/* Section: Administration & Audit */}
          <div>
            {!isCollapsed ? (
              <div className="px-3 mb-2 text-[10px] font-mono uppercase tracking-wider text-slate-400 dark:text-slate-400 font-bold">
                Administration
              </div>
            ) : (
              <div className="my-2 border-t border-slate-200/80 dark:border-slate-800/80 mx-1" />
            )}
            <button
              onClick={() => setActiveNav('audit-logs')}
              title="Organization Audit"
              className={`w-full flex items-center ${
                isCollapsed ? 'justify-center h-10 px-0' : 'gap-3 px-3 py-2.5'
              } rounded-xl transition-all cursor-pointer ${
                activeNav === 'audit-logs'
                  ? 'bg-cyan-50 dark:bg-cyan-500/10 text-cyan-700 dark:text-cyan-400 border border-cyan-200 dark:border-cyan-500/30 font-medium'
                  : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <Shield className="h-4 w-4 shrink-0" />
              {!isCollapsed && <span>Organization Audit</span>}
            </button>
          </div>
        </div>

        {/* Sidebar Footer: Tenant Admin Profile & Logout */}
        <div className="p-3 border-t border-slate-200 dark:border-slate-800/80 bg-slate-50 dark:bg-[#080d19] shrink-0">
          {!isCollapsed ? (
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5 min-w-0">
                <div className="h-8 w-8 rounded-lg bg-indigo-50 border border-indigo-200 text-indigo-700 flex items-center justify-center font-bold text-xs font-mono dark:bg-indigo-950 dark:border-indigo-800 dark:text-indigo-300 shrink-0 shadow-2xs">
                  TA
                </div>
                <div className="min-w-0">
                  <div className="text-xs font-semibold text-slate-900 dark:text-white truncate">{user?.name || 'Tenant Admin'}</div>
                  <div className="text-[10px] text-slate-500 dark:text-slate-400 font-mono truncate">{user?.tenant_id}</div>
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
                title={`${user?.name || 'Tenant Admin'} (${user?.tenant_id || ''})`}
              >
                TA
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

      {/* 2. MAIN ORGANIZATION CONTENT AREA */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden bg-[#f8fafc] dark:bg-[#070b13]">
        {/* Top Header Bar */}
        <header className="h-16 border-b border-slate-200 dark:border-slate-800/80 bg-white/80 dark:bg-[#0a0f1d]/80 backdrop-blur-md px-6 flex items-center justify-between shrink-0 shadow-2xs">
          <div className="flex items-center gap-3 text-xs">
            <span className="text-slate-500 dark:text-slate-400 font-mono">Org: {user?.tenant_id}</span>
            <span className="text-slate-400 dark:text-slate-600">/</span>
            <span className="text-cyan-700 dark:text-cyan-400 font-semibold uppercase tracking-wider font-mono text-[11px]">
              {activeNav.replace('-', ' ')}
            </span>
          </div>

          <div className="flex items-center gap-3">
            {/* Theme Toggle Button */}
            <button
              onClick={toggleTheme}
              type="button"
              title={isDark ? 'Switch to Light Theme' : 'Switch to Dark Theme'}
              className="p-2 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors cursor-pointer"
            >
              {isDark ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-600" />}
            </button>

            <div className="hidden sm:flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-50 dark:bg-cyan-500/10 border border-cyan-200 dark:border-cyan-500/20 text-cyan-700 dark:text-cyan-400 text-xs font-mono font-medium">
              <Lock className="h-3.5 w-3.5" />
              <span>Tenant Isolated</span>
            </div>

            <button
              onClick={() => {
                refetchDash();
                refetchUsers();
                refetchCases();
                refetchInvs();
              }}
              className="p-2 rounded-xl bg-slate-100 dark:bg-slate-800/60 hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors cursor-pointer"
              title="Refresh Data"
            >
              <RefreshCw className="h-4 w-4" />
            </button>

            {/* User Profile & Role Clearance matching Navbar */}
            <div className="flex items-center gap-2 pl-3 border-l border-slate-200 dark:border-slate-800">
              <div className="hidden sm:flex items-center gap-1.5 font-mono text-[11px]">
                <span className="px-2 py-0.5 rounded bg-blue-50 border border-blue-200 text-blue-800 dark:bg-blue-950/40 dark:border-blue-800 dark:text-blue-300 font-semibold">
                  TENANT ADMIN
                </span>
              </div>

              <div
                className="w-7 h-7 rounded-lg bg-indigo-50 border border-indigo-200 text-indigo-700 flex items-center justify-center text-xs font-bold font-mono dark:bg-indigo-950 dark:border-indigo-800 dark:text-indigo-300 shadow-2xs"
                title={`${user?.name || 'Tenant Admin'} (${user?.email || ''})`}
              >
                TA
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
          {/* VIEW: ORGANIZATION DASHBOARD */}
          {activeNav === 'dashboard' && (
            <div className="space-y-8 max-w-7xl mx-auto">
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Organization Dashboard</h1>
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                  Live MongoDB metrics isolated strictly to your organization mandate.
                </p>
              </div>

              {/* Metric Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
                <div className="bg-white dark:bg-[#0f1424] border border-slate-200/90 dark:border-slate-800/90 p-5 rounded-2xl relative overflow-hidden shadow-xs">
                  <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-mono">
                    <span>Cases</span>
                    <FolderOpen className="h-4 w-4 text-cyan-600 dark:text-cyan-400" />
                  </div>
                  <div className="mt-3 text-3xl font-extrabold text-slate-900 dark:text-white font-mono">
                    {isDashLoading ? '...' : dashboard?.total_cases ?? 0}
                  </div>
                  <div className="mt-2 text-[11px] text-slate-500 dark:text-slate-400">Total dossiers registered</div>
                </div>

                <div className="bg-white dark:bg-[#0f1424] border border-slate-200/90 dark:border-slate-800/90 p-5 rounded-2xl relative overflow-hidden shadow-xs">
                  <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-mono">
                    <span>Active Investigations</span>
                    <Activity className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
                  </div>
                  <div className="mt-3 text-3xl font-extrabold text-slate-900 dark:text-white font-mono">
                    {isDashLoading ? '...' : dashboard?.active_investigations ?? 0}
                  </div>
                  <div className="mt-2 text-[11px] text-slate-500 dark:text-slate-400">In-progress sweeps</div>
                </div>

                <div className="bg-white dark:bg-[#0f1424] border border-slate-200/90 dark:border-slate-800/90 p-5 rounded-2xl relative overflow-hidden shadow-xs">
                  <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-mono">
                    <span>Evidence Stored</span>
                    <Shield className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
                  </div>
                  <div className="mt-3 text-3xl font-extrabold text-slate-900 dark:text-white font-mono">
                    {isDashLoading ? '...' : dashboard?.evidence_collected ?? 0}
                  </div>
                  <div className="mt-2 text-[11px] text-slate-500 dark:text-slate-400">SHA-256 verified artifacts</div>
                </div>

                <div className="bg-white dark:bg-[#0f1424] border border-slate-200/90 dark:border-slate-800/90 p-5 rounded-2xl relative overflow-hidden shadow-xs">
                  <div className="flex items-center justify-between text-slate-500 dark:text-slate-400 text-xs font-mono">
                    <span>Findings & Threats</span>
                    <Layers className="h-4 w-4 text-purple-600 dark:text-purple-400" />
                  </div>
                  <div className="mt-3 text-3xl font-extrabold text-slate-900 dark:text-white font-mono">
                    {isDashLoading ? '...' : dashboard?.total_findings ?? 0}
                  </div>
                  <div className="mt-2 text-[11px] text-slate-500 dark:text-slate-400 flex items-center gap-2">
                    <span className="text-rose-600 dark:text-rose-400 font-medium">
                      {dashboard?.critical_threats ?? 0} Critical
                    </span>
                  </div>
                </div>
              </div>

              {/* Organization Actions & Members Overview */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 bg-white dark:bg-[#0f1424] border border-slate-200/90 dark:border-slate-800/90 p-6 rounded-2xl space-y-4 shadow-xs">
                  <div className="flex items-center justify-between">
                    <h2 className="text-base font-semibold text-slate-900 dark:text-white">Team Members</h2>
                    <button
                      onClick={() => setActiveNav('invite-user')}
                      className="text-xs text-cyan-600 dark:text-cyan-400 hover:text-cyan-700 dark:hover:text-cyan-300 font-medium cursor-pointer"
                    >
                      + Add Member
                    </button>
                  </div>

                  {users.length === 0 ? (
                    <div className="py-10 text-center text-slate-400 font-mono text-xs">
                      No additional team members yet. Use the Invite User action to provision Analysts and Investigators.
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {users.slice(0, 5).map((u) => (
                        <div
                          key={u.id}
                          className="flex items-center justify-between p-3 rounded-xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200/80 dark:border-slate-800/80 text-xs"
                        >
                          <div>
                            <div className="font-semibold text-slate-900 dark:text-white">{u.name}</div>
                            <div className="text-[11px] text-slate-500 dark:text-slate-400 font-mono">{u.email}</div>
                          </div>
                          <span
                            className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-medium ${
                              u.role === 'TENANT_ADMIN'
                                ? 'bg-cyan-100 dark:bg-cyan-500/10 text-cyan-700 dark:text-cyan-400'
                                : u.role === 'ANALYST'
                                ? 'bg-indigo-100 dark:bg-indigo-500/10 text-indigo-700 dark:text-indigo-400'
                                : 'bg-emerald-100 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-400'
                            }`}
                          >
                            {u.role}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div className="bg-white dark:bg-[#0f1424] border border-slate-200/90 dark:border-slate-800/90 p-6 rounded-2xl space-y-6 flex flex-col justify-between shadow-xs">
                  <div>
                    <h2 className="text-base font-semibold text-slate-900 dark:text-white">Quick Actions</h2>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Tenant Administrator operations.</p>
                  </div>

                  <div className="space-y-3">
                    <button
                      onClick={() => setActiveNav('invite-user')}
                      className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 text-white font-medium text-xs hover:from-cyan-500 hover:to-blue-500 shadow-md transition-all cursor-pointer"
                    >
                      <UserPlus className="h-4 w-4" />
                      <span>Provision New Team User</span>
                    </button>
                    <button
                      onClick={() => setActiveNav('cases')}
                      className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-slate-100 dark:bg-slate-800/80 hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 font-medium text-xs border border-slate-200 dark:border-slate-700/60 transition-all cursor-pointer"
                    >
                      <FolderOpen className="h-4 w-4" />
                      <span>View Organization Cases</span>
                    </button>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800/80 text-xs text-slate-500 dark:text-slate-400 font-mono">
                    Tenant ID: <span className="text-cyan-600 dark:text-cyan-400 font-semibold">{user?.tenant_id}</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* VIEW: MEMBERS / ANALYSTS / INVESTIGATORS */}
          {(activeNav === 'members' || activeNav === 'analysts' || activeNav === 'investigators') && (
            <div className="space-y-6 max-w-7xl mx-auto">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
                    {activeNav === 'analysts'
                      ? 'Organization Analysts'
                      : activeNav === 'investigators'
                      ? 'Organization Investigators'
                      : 'Organization Members'}
                  </h1>
                  <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                    Manage team roles, access permissions, and investigator authorizations for this tenant.
                  </p>
                </div>
                <button
                  onClick={() => setActiveNav('invite-user')}
                  className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs transition-colors self-start sm:self-auto cursor-pointer"
                >
                  <UserPlus className="h-4 w-4" />
                  <span>Create User</span>
                </button>
              </div>

              <div className="relative">
                <Search className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search members by name or email..."
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
                        <th className="py-3.5 px-6 font-semibold">NAME</th>
                        <th className="py-3.5 px-4 font-semibold">EMAIL</th>
                        <th className="py-3.5 px-4 font-semibold">ROLE</th>
                        <th className="py-3.5 px-4 font-semibold">STATUS</th>
                        <th className="py-3.5 px-4 font-semibold">JOINED</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-200 dark:divide-slate-800/60">
                      {filteredUsers.map((u) => (
                        <tr key={u.id} className="hover:bg-slate-50 dark:hover:bg-slate-900/40 transition-colors">
                          <td className="py-4 px-6 font-semibold text-slate-900 dark:text-white">{u.name}</td>
                          <td className="py-4 px-4 font-mono text-slate-700 dark:text-slate-300">{u.email}</td>
                          <td className="py-4 px-4">
                            <span
                              className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-semibold ${
                                u.role === 'TENANT_ADMIN'
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

          {/* VIEW: CREATE USER WORKFLOW */}
          {activeNav === 'invite-user' && (
            <div className="max-w-2xl mx-auto space-y-6">
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Create Tenant User</h1>
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                  Tenant Admin workflow: Provision Analysts, Investigators, or Team Users directly into your organization in MongoDB.
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

              <form onSubmit={handleCreateUserSubmit} className="bg-white dark:bg-[#0f1424] border border-slate-200/90 dark:border-slate-800/90 rounded-2xl p-6 space-y-5 text-xs shadow-xs">
                <div>
                  <label className="block text-slate-700 dark:text-slate-300 font-medium mb-1.5">
                    Full Name <span className="text-rose-500">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Alice Morgan"
                    value={formName}
                    onChange={(e) => setFormName(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-hidden focus:border-cyan-500"
                  />
                </div>

                <div>
                  <label className="block text-slate-700 dark:text-slate-300 font-medium mb-1.5">
                    Work Email <span className="text-rose-500">*</span>
                  </label>
                  <input
                    type="email"
                    required
                    placeholder="alice@organization.com"
                    value={formEmail}
                    onChange={(e) => setFormEmail(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-white font-mono placeholder-slate-400 focus:outline-hidden focus:border-cyan-500"
                  />
                </div>

                <div>
                  <label className="block text-slate-700 dark:text-slate-300 font-medium mb-1.5">
                    Initial Password <span className="text-rose-500">*</span>
                  </label>
                  <input
                    type="password"
                    required
                    placeholder="Secure password (min 6 chars)"
                    value={formPassword}
                    onChange={(e) => setFormPassword(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-white font-mono focus:outline-hidden focus:border-cyan-500"
                  />
                </div>

                <div>
                  <label className="block text-slate-700 dark:text-slate-300 font-medium mb-1.5">
                    User Role <span className="text-rose-500">*</span>
                  </label>
                  <select
                    value={formRole}
                    onChange={(e) => setFormRole(e.target.value as any)}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-white focus:outline-hidden focus:border-cyan-500"
                  >
                    <option value="INVESTIGATOR">Investigator (Conducts OSINT/Threat sweeps, evidence vault, investigations)</option>
                    <option value="ANALYST">Analyst (Reviews results, contributes to findings and reports)</option>
                    <option value="USER">User (Standard member with search and read access)</option>
                  </select>
                </div>

                <div className="pt-4 flex items-center justify-end gap-3 border-t border-slate-200 dark:border-slate-800">
                  <button
                    type="button"
                    onClick={() => setActiveNav('members')}
                    className="px-5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 font-medium transition-colors cursor-pointer"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={createUserMutation.isPending}
                    className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-semibold shadow-md transition-all disabled:opacity-50 cursor-pointer"
                  >
                    {createUserMutation.isPending ? 'Provisioning...' : 'Provision User'}
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* VIEW: CASES & INVESTIGATIONS */}
          {(activeNav === 'cases' || activeNav === 'investigations') && (
            <div className="space-y-6 max-w-7xl mx-auto">
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
                  {activeNav === 'cases' ? 'Organization Cases' : 'Active Investigations'}
                </h1>
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                  Database-backed intelligence operations strictly isolated to this organization.
                </p>
              </div>

              <div className="bg-white dark:bg-[#0f1424] border border-slate-200/90 dark:border-slate-800/90 rounded-2xl overflow-hidden shadow-xs">
                {(activeNav === 'cases' ? cases : investigations).length === 0 ? (
                  <div className="p-12 text-center space-y-3">
                    <FolderOpen className="h-12 w-12 text-slate-400 dark:text-slate-600 mx-auto" />
                    <div className="text-base font-semibold text-slate-900 dark:text-white">0 Records in Database</div>
                    <p className="text-xs text-slate-500 dark:text-slate-400 max-w-md mx-auto">
                      No sample or demo records exist. Once your Investigators run searches or create cases, they will appear here.
                    </p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse text-xs">
                      <thead>
                        <tr className="border-b border-slate-200 dark:border-slate-800/80 bg-slate-50 dark:bg-slate-900/60 text-slate-500 dark:text-slate-400 font-mono text-[11px]">
                          <th className="py-3.5 px-6 font-semibold">TITLE</th>
                          <th className="py-3.5 px-4 font-semibold">TARGET</th>
                          <th className="py-3.5 px-4 font-semibold">PRIORITY</th>
                          <th className="py-3.5 px-4 font-semibold">STATUS</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-200 dark:divide-slate-800/60">
                        {(activeNav === 'cases' ? cases : investigations).map((item) => (
                          <tr key={item.id} className="hover:bg-slate-50 dark:hover:bg-slate-900/40 transition-colors">
                            <td className="py-4 px-6 font-semibold text-slate-900 dark:text-white">{item.title}</td>
                            <td className="py-4 px-4 font-mono text-cyan-600 dark:text-cyan-400">{item.target}</td>
                            <td className="py-4 px-4 font-mono">{item.priority}</td>
                            <td className="py-4 px-4">
                              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-cyan-100 dark:bg-cyan-500/10 text-cyan-700 dark:text-cyan-400">
                                {item.status}
                              </span>
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

          {/* VIEW: EVIDENCE, FINDINGS, REPORTS */}
          {(activeNav === 'evidence' || activeNav === 'findings' || activeNav === 'reports') && (
            <div className="space-y-6 max-w-7xl mx-auto">
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
                  {activeNav === 'evidence'
                    ? 'Evidence Vault'
                    : activeNav === 'findings'
                    ? 'Investigation Findings'
                    : 'Generated Intelligence Reports'}
                </h1>
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                  Persistent artifacts and reports generated from live intelligence runs.
                </p>
              </div>

              <div className="bg-white dark:bg-[#0f1424] border border-slate-200/90 dark:border-slate-800/90 rounded-2xl p-12 text-center shadow-xs">
                <Shield className="h-12 w-12 text-slate-400 dark:text-slate-600 mx-auto mb-3" />
                <div className="text-base font-semibold text-slate-900 dark:text-white">0 Items Found</div>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 max-w-md mx-auto">
                  Artifacts collected during actual operations are persisted directly to MongoDB and verified with SHA-256 bitwise checksums.
                </p>
              </div>
            </div>
          )}

          {/* VIEW: AUDIT LOGS */}
          {activeNav === 'audit-logs' && (
            <div className="space-y-6 max-w-7xl mx-auto">
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Organization Audit Log</h1>
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                  Chain-of-custody logging of all actions performed by users within your organization.
                </p>
              </div>

              <div className="bg-white dark:bg-[#0f1424] border border-slate-200/90 dark:border-slate-800/90 rounded-2xl overflow-hidden shadow-xs">
                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse text-xs">
                    <thead>
                      <tr className="border-b border-slate-200 dark:border-slate-800/80 bg-slate-50 dark:bg-slate-900/60 text-slate-500 dark:text-slate-400 font-mono text-[11px]">
                        <th className="py-3.5 px-6 font-semibold">TIMESTAMP</th>
                        <th className="py-3.5 px-4 font-semibold">ACTION</th>
                        <th className="py-3.5 px-4 font-semibold">USER</th>
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
        </div>
      </main>
    </div>
  );
};

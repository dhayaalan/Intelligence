import React, { useState } from 'react';
import {
  Search,
  FolderGit2,
  Clock,
  Globe,
  MessageSquare,
  Newspaper,
  ShieldCheck,
  ShieldAlert,
  MapPin,
  Share2,
  Layers,
  FileText,
  Users,
  Settings,
  Activity,
  Wrench,
  ChevronLeft,
  ChevronRight,
  LogOut,
  Building,
  UserCheck
} from 'lucide-react';
import { useAuth } from '../../core/auth/AuthContext';
import { SearchPage } from '../../features/search/SearchPage';
import { InvestigationsPage } from '../../features/investigations/InvestigationsPage';
import { RecentActivityPage } from '../../features/recent/RecentActivityPage';
import { OsintIntelligencePage } from '../../features/osint/OsintIntelligencePage';
import { SocialIntelligencePage } from '../../features/social_intelligence/SocialIntelligencePage';
import { NewsIntelligencePage } from '../../features/news_intelligence/NewsIntelligencePage';
import { MediaForensicsPage } from '../../features/media_forensics/MediaForensicsPage';
import { ThreatIntelligencePage } from '../../features/threat_intelligence/ThreatIntelligencePage';
import { MapPage } from '../../features/map/MapPage';
import { GraphStudioPage } from '../../features/graph/GraphStudioPage';
import { EvidencePage } from '../../features/evidence/EvidencePage';
import { ReportsPage } from '../../features/reports/ReportsPage';
import { AdministrationPage, AdminTab } from '../../features/administration/AdministrationPage';
import { apiRequest } from '../../core/api/client';

export type NavView =
  | 'search'
  | 'investigations'
  | 'recent'
  | 'osint'
  | 'social'
  | 'news'
  | 'media'
  | 'threat'
  | 'location'
  | 'entities'
  | 'evidence'
  | 'reports'
  | 'admin-users'
  | 'admin-modules'
  | 'admin-providers'
  | 'admin-jobs'
  | 'admin-audit'
  | 'admin-settings';

interface InvestigatorShellProps {
  isSidebarOpen: boolean;
  onCloseSidebar: () => void;
  universalSearchQuery?: string;
  universalModuleFilter?: string;
}

export const InvestigatorShell: React.FC<InvestigatorShellProps> = ({
  isSidebarOpen,
  onCloseSidebar,
  universalSearchQuery,
  universalModuleFilter,
}) => {
  const { user, logout } = useAuth();

  const getInitialNav = (): { nav: NavView; invId: string | null } => {
    if (typeof window !== 'undefined') {
      const parts = window.location.pathname.replace(/^\/+/, '').split('/');
      const path = (parts[0] || '').toLowerCase();
      const validNavs: NavView[] = [
        'search',
        'investigations',
        'recent',
        'osint',
        'social',
        'news',
        'media',
        'threat',
        'location',
        'entities',
        'evidence',
        'reports',
        'admin-users',
        'admin-modules',
        'admin-providers',
        'admin-jobs',
        'admin-audit',
        'admin-settings',
      ];
      if (validNavs.includes(path as NavView)) {
        return { nav: path as NavView, invId: parts[1] || null };
      }
    }
    return { nav: 'search', invId: null };
  };

  const initialRoute = getInitialNav();
  const [activeNav, setActiveNav] = useState<NavView>(initialRoute.nav);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [selectedInvId, setSelectedInvId] = useState<string | null>(initialRoute.invId);
  const [investigationsKey, setInvestigationsKey] = useState<number>(0);

  // Sync state on back/forward browser navigation
  React.useEffect(() => {
    const handlePopState = () => {
      const route = getInitialNav();
      setActiveNav(route.nav);
      setSelectedInvId(route.invId);
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const handleNavClick = (id: NavView) => {
    if (id === 'investigations') {
      setSelectedInvId(null);
      setInvestigationsKey((k) => k + 1);
    }
    setActiveNav(id);
    if (typeof window !== 'undefined') {
      window.history.pushState(null, '', `/${id}`);
    }
    onCloseSidebar();
  };

  const handleOpenInvestigationFromSearch = async (target: string, targetType: string, searchId?: string) => {
    try {
      const res = await apiRequest<any>('/investigations', {
        method: 'POST',
        body: JSON.stringify({
          title: `Target Investigation: ${target}`,
          target,
          target_type: targetType,
          search_id: searchId,
        }),
      });
      if (res?.id) {
        setSelectedInvId(res.id);
        if (typeof window !== 'undefined') {
          window.history.pushState(null, '', `/investigations/${res.id}`);
        }
      }
      setActiveNav('investigations');
    } catch (err) {
      console.error('Failed to promote target to investigation', err);
      setActiveNav('investigations');
    }
  };

  const isSuperAdmin = user?.role === 'SUPER_ADMIN';
  const isTenantAdmin = user?.role === 'TENANT_ADMIN';
  const hasAdminAccess = isSuperAdmin || isTenantAdmin;

  return (
    <div className="flex-1 flex overflow-hidden">
      {/* Backdrop for mobile */}
      {isSidebarOpen && (
        <div
          onClick={onCloseSidebar}
          className="fixed inset-0 bg-black/60 z-30 md:hidden backdrop-blur-xs transition-opacity"
        />
      )}

      {/* Modern Modular Sidebar */}
      <aside
        className={`fixed md:static inset-y-0 left-0 z-40 transition-all duration-300 ease-in-out border-r border-slate-200/80 dark:border-slate-800/80 bg-white/95 dark:bg-[#070b13]/95 backdrop-blur-md flex flex-col justify-between ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
          } ${isCollapsed ? 'w-16' : 'w-64'}`}
      >
        {/* Collapse toggle header on desktop */}
        <div className={`hidden md:flex items-center ${isCollapsed ? 'justify-center px-2 py-2.5' : 'justify-between px-3 py-2.5'} border-b border-slate-200/80 dark:border-slate-800/80`}>
          {!isCollapsed ? (
            <>
              <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 font-bold px-1">
                Navigation
              </span>
              <button
                onClick={() => setIsCollapsed(true)}
                className="p-1 rounded-md text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer"
                title="Collapse Sidebar"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
            </>
          ) : (
            <button
              onClick={() => setIsCollapsed(false)}
              className="p-1 rounded-md text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer"
              title="Expand Sidebar"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          )}
        </div>

        <div className="flex-1 overflow-y-auto py-3 px-2 space-y-5">
          {/* SECTION 1: WORKSPACE */}
          <div className="space-y-1">
            {!isCollapsed && (
              <div className="px-3 pb-1 text-[10px] font-mono font-bold uppercase tracking-wider text-slate-400">
                Workspace
              </div>
            )}
            {[
              { id: 'search' as NavView, label: 'Search', icon: <Search className="w-4 h-4" /> },
              { id: 'investigations' as NavView, label: 'Investigations', icon: <FolderGit2 className="w-4 h-4" /> },
              { id: 'recent' as NavView, label: 'Recent Activity', icon: <Clock className="w-4 h-4" /> },
            ].map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => handleNavClick(item.id)}
                title={isCollapsed ? item.label : undefined}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-all cursor-pointer ${activeNav === item.id
                    ? 'bg-slate-900 text-white font-semibold shadow-xs dark:bg-white dark:text-slate-950'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100 dark:text-slate-400 dark:hover:text-white dark:hover:bg-slate-800/60'
                  } ${isCollapsed ? 'justify-center px-0' : ''}`}
              >
                <span className={activeNav === item.id ? 'text-white dark:text-slate-950' : 'text-slate-400'}>{item.icon}</span>
                {!isCollapsed && <span>{item.label}</span>}
              </button>
            ))}
          </div>

          {/* SECTION 2: INTELLIGENCE */}
          <div className="space-y-1">
            {!isCollapsed && (
              <div className="px-3 pb-1 text-[10px] font-mono font-bold uppercase tracking-wider text-slate-400">
                Intelligence
              </div>
            )}
            {[
              { id: 'osint' as NavView, label: 'OSINT', icon: <Globe className="w-4 h-4" /> },
              { id: 'social' as NavView, label: 'Social Intelligence', icon: <MessageSquare className="w-4 h-4" /> },
              { id: 'news' as NavView, label: 'News Intelligence', icon: <Newspaper className="w-4 h-4" /> },
              { id: 'media' as NavView, label: 'Media & Forensics', icon: <ShieldCheck className="w-4 h-4" /> },
              { id: 'threat' as NavView, label: 'Threat Intelligence', icon: <ShieldAlert className="w-4 h-4" /> },
              { id: 'location' as NavView, label: 'Location Intelligence', icon: <MapPin className="w-4 h-4" /> },
            ].map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => handleNavClick(item.id)}
                title={isCollapsed ? item.label : undefined}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-all cursor-pointer ${activeNav === item.id
                    ? 'bg-slate-900 text-white font-semibold shadow-xs dark:bg-white dark:text-slate-950'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100 dark:text-slate-400 dark:hover:text-white dark:hover:bg-slate-800/60'
                  } ${isCollapsed ? 'justify-center px-0' : ''}`}
              >
                <span className={activeNav === item.id ? 'text-white dark:text-slate-950' : 'text-slate-400'}>{item.icon}</span>
                {!isCollapsed && <span>{item.label}</span>}
              </button>
            ))}
          </div>

          {/* SECTION 3: INVESTIGATION RESOURCES */}
          <div className="space-y-1">
            {!isCollapsed && (
              <div className="px-3 pb-1 text-[10px] font-mono font-bold uppercase tracking-wider text-slate-400">
                Investigation Resources
              </div>
            )}
            {[
              { id: 'reports' as NavView, label: 'Reports', icon: <FileText className="w-4 h-4" /> },
            ].map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => handleNavClick(item.id)}
                title={isCollapsed ? item.label : undefined}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-all cursor-pointer ${activeNav === item.id
                    ? 'bg-slate-900 text-white font-semibold shadow-xs dark:bg-white dark:text-slate-950'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100 dark:text-slate-400 dark:hover:text-white dark:hover:bg-slate-800/60'
                  } ${isCollapsed ? 'justify-center px-0' : ''}`}
              >
                <span className={activeNav === item.id ? 'text-white dark:text-slate-950' : 'text-slate-400'}>{item.icon}</span>
                {!isCollapsed && <span>{item.label}</span>}
              </button>
            ))}
          </div>

          {/* SECTION 4: ADMINISTRATION (Role-Gated) */}
          {hasAdminAccess && (
            <div className="space-y-1 pt-1">
              {!isCollapsed && (
                <div className="px-3 pb-1 text-[10px] font-mono font-bold uppercase tracking-wider text-slate-400">
                  Administration
                </div>
              )}
              {[
                { id: 'admin-users' as NavView, label: 'Users & Roles', icon: <Users className="w-4 h-4" /> },
                { id: 'admin-modules' as NavView, label: 'Module Entitlements', icon: <Layers className="w-4 h-4" /> },
                { id: 'admin-providers' as NavView, label: 'Provider Config', icon: <Wrench className="w-4 h-4" /> },
                { id: 'admin-jobs' as NavView, label: 'Collection Jobs', icon: <Clock className="w-4 h-4" /> },
                { id: 'admin-audit' as NavView, label: 'Audit Logs', icon: <Activity className="w-4 h-4" /> },
                { id: 'admin-settings' as NavView, label: 'Platform Settings', icon: <Settings className="w-4 h-4" /> },
              ].map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => handleNavClick(item.id)}
                  title={isCollapsed ? item.label : undefined}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-all cursor-pointer ${activeNav === item.id
                      ? 'bg-slate-900 text-white font-semibold shadow-xs dark:bg-white dark:text-slate-950'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100 dark:text-slate-400 dark:hover:text-white dark:hover:bg-slate-800/60'
                    } ${isCollapsed ? 'justify-center px-0' : ''}`}
                >
                  <span className={activeNav === item.id ? 'text-white dark:text-slate-950' : 'text-slate-400'}>{item.icon}</span>
                  {!isCollapsed && <span>{item.label}</span>}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Sidebar Footer: Tenant Isolation Enforced */}
        <div className="p-3 border-t border-slate-200/80 bg-slate-50/60 dark:border-slate-800/80 dark:bg-[#070b13]/60 text-xs font-mono shrink-0">
          {!isCollapsed ? (
            <div className="flex justify-between items-center text-[10px] text-slate-500">
              <span className="flex items-center gap-1.5">
                <Building className="w-3 h-3 text-slate-400" />
                <span>TENANT ISOLATION</span>
              </span>
              <span className="text-emerald-600 font-bold dark:text-emerald-400">ENFORCED</span>
            </div>
          ) : (
            <div className="flex justify-center" title="Tenant Isolation Enforced">
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
            </div>
          )}
        </div>
      </aside>

      {/* Main Workspace Canvas */}
      <main className="flex-1 flex flex-col min-w-0 bg-slate-50 dark:bg-[#070b13] overflow-hidden">
        {activeNav === 'search' && (
          <SearchPage
            onOpenInvestigation={handleOpenInvestigationFromSearch}
            initialQuery={universalSearchQuery}
            initialModuleFilter={universalModuleFilter}
          />
        )}

        {activeNav === 'investigations' && (
          <InvestigationsPage
            key={investigationsKey}
            selectedInvestigationId={selectedInvId}
            onSelectInvestigation={(id) => {
              setSelectedInvId(id);
              if (typeof window !== 'undefined') {
                window.history.pushState(null, '', `/investigations/${id}`);
              }
            }}
            onNavigateToSearch={(query) => {
              setActiveNav('search');
            }}
          />
        )}

        {activeNav === 'recent' && (
          <RecentActivityPage
            onNavigateToInvestigation={(id) => {
              setSelectedInvId(id);
              setActiveNav('investigations');
            }}
            onNavigateToSearch={(query) => {
              setActiveNav('search');
            }}
          />
        )}

        {activeNav === 'osint' && (
          <OsintIntelligencePage onOpenInvestigation={handleOpenInvestigationFromSearch} />
        )}

        {activeNav === 'social' && <SocialIntelligencePage />}

        {activeNav === 'news' && <NewsIntelligencePage />}

        {activeNav === 'media' && (
          <MediaForensicsPage
            onNavigateToSearch={(query) => setActiveNav('search')}
            onNavigateToInvestigation={(id) => {
              setSelectedInvId(id);
              setActiveNav('investigations');
            }}
          />
        )}

        {activeNav === 'threat' && <ThreatIntelligencePage />}

        {activeNav === 'location' && <MapPage />}

        {activeNav === 'entities' && <GraphStudioPage />}

        {activeNav === 'evidence' && <EvidencePage />}

        {activeNav === 'reports' && <ReportsPage />}

        {activeNav.startsWith('admin-') && (
          <AdministrationPage initialTab={activeNav.replace('admin-', '') as AdminTab} />
        )}
      </main>
    </div>
  );
};

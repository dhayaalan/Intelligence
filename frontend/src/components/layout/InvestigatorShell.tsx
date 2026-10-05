import React, { useState } from 'react';
import {
  Search, FolderGit2, Layers, ShieldAlert, FileText, Lock,
  Share2, Globe, ChevronLeft, ChevronRight, LogOut
} from 'lucide-react';
import { useAuth } from '../../core/auth/AuthContext';
import { SearchPage } from '../../features/search/SearchPage';
import { InvestigationsPage } from '../../features/investigations/InvestigationsPage';
import { FindingsPage } from '../../features/findings/FindingsPage';
import { EvidencePage } from '../../features/evidence/EvidencePage';
import { EntitiesPage } from '../../features/entities/EntitiesPage';
import { ReportsPage } from '../../features/reports/ReportsPage';
import { GraphStudioPage } from '../../features/graph/GraphStudioPage';
import { MapPage } from '../../features/map/MapPage';
import { apiRequest } from '../../core/api/client';

type NavView = 'search' | 'investigations' | 'entities' | 'graph' | 'map' | 'findings' | 'evidence' | 'reports';

interface NavItem {
  id: NavView;
  label: string;
  icon: React.ReactNode;
  dividerBefore?: boolean;
}

interface InvestigatorShellProps {
  isSidebarOpen: boolean;
  onCloseSidebar: () => void;
}

export const InvestigatorShell: React.FC<InvestigatorShellProps> = ({ isSidebarOpen, onCloseSidebar }) => {
  const { user, logout } = useAuth();
  const [activeNav, setActiveNav] = useState<NavView>('search');
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [searchTarget, setSearchTarget] = useState<{ query: string; targetType?: string } | null>(null);
  const [selectedInvId, setSelectedInvId] = useState<string | null>(null);

  const navItems: NavItem[] = [
    { id: 'search', label: 'Search', icon: <Search className="w-4 h-4" /> },
    { id: 'investigations', label: 'Investigations', icon: <FolderGit2 className="w-4 h-4" /> },
    { id: 'entities', label: 'Entities', icon: <Layers className="w-4 h-4" />, dividerBefore: true },
    { id: 'graph', label: 'Relationships', icon: <Share2 className="w-4 h-4" /> },
    { id: 'map', label: 'Geospatial Map', icon: <Globe className="w-4 h-4" /> },
    { id: 'findings', label: 'Findings', icon: <ShieldAlert className="w-4 h-4" />, dividerBefore: true },
    { id: 'evidence', label: 'Evidence Vault', icon: <Lock className="w-4 h-4" /> },
    { id: 'reports', label: 'Reports', icon: <FileText className="w-4 h-4" /> },
  ];

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
      }
      setActiveNav('investigations');
    } catch (err) {
      console.error('Failed to promote target to investigation', err);
      setActiveNav('investigations');
    }
  };

  const handleNavClick = (id: NavView) => {
    setActiveNav(id);
    onCloseSidebar(); // Close mobile sidebar on navigation
  };

  return (
    <div className="flex-1 flex overflow-hidden relative">
      {/* Sidebar */}
      <aside
        className={`${
          isCollapsed ? 'md:w-20' : 'md:w-64'
        } w-64 border-r border-slate-200/80 bg-white/95 backdrop-blur-md flex flex-col fixed top-14 left-0 bottom-0 transition-all duration-300 z-30 dark:border-slate-800/80 dark:bg-[#0e131f]/95 shadow-xs ${
          isSidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        {/* Collapse toggle header on desktop */}
        <div className={`hidden md:flex items-center ${isCollapsed ? 'justify-center px-2 py-2.5' : 'justify-between px-3 py-2.5'} border-b border-slate-200/80 dark:border-slate-800/80`}>
          {!isCollapsed ? (
            <>
              <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 font-bold px-1">
                Workspace
              </span>
              <button
                onClick={() => setIsCollapsed(true)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer"
                title="Collapse Sidebar"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
            </>
          ) : (
            <button
              onClick={() => setIsCollapsed(false)}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer"
              title="Expand Sidebar"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Scrollable Navigation Area */}
        <div className="flex-1 overflow-y-auto px-3 py-3 space-y-1.5 scrollbar-thin">
          {!isCollapsed && (
            <div className="px-2.5 pb-2 text-[10px] font-mono uppercase tracking-wider text-slate-400 font-bold md:hidden">
              Intelligence Workspace
            </div>
          )}

          {navItems.map((item) => {
            const isActive = activeNav === item.id;

            return (
              <React.Fragment key={item.id}>
                {item.dividerBefore && (
                  <div className="my-2 border-t border-slate-200/80 dark:border-slate-800/80" />
                )}
                <button
                  onClick={() => handleNavClick(item.id)}
                  title={item.label}
                  className={`w-full flex items-center ${
                    isCollapsed ? 'justify-center h-10 px-0' : 'justify-start px-3 py-2'
                  } rounded-xl text-xs font-medium transition-all group cursor-pointer ${
                    isActive
                      ? 'bg-slate-900 text-white font-semibold shadow-xs dark:bg-white dark:text-slate-950'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100 dark:text-slate-400 dark:hover:text-white dark:hover:bg-slate-900/80'
                  }`}
                >
                  <div className={`flex items-center ${isCollapsed ? 'justify-center' : 'gap-2.5'}`}>
                    <span
                      className={`transition-colors ${
                        isActive
                          ? 'text-white dark:text-slate-950'
                          : 'text-slate-400 group-hover:text-slate-700 dark:group-hover:text-slate-200'
                      }`}
                    >
                      {item.icon}
                    </span>
                    {!isCollapsed && <span>{item.label}</span>}
                  </div>
                </button>
              </React.Fragment>
            );
          })}
        </div>

        {/* Sidebar Footer: Profile & Intel Engines */}
        <div className="p-3 border-t border-slate-200/80 bg-slate-50/60 space-y-3 dark:border-slate-800/80 dark:bg-[#0e131f]/60 shrink-0">
          {!isCollapsed ? (
            <>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5 min-w-0">
                  <div className="h-8 w-8 rounded-lg bg-indigo-50 border border-indigo-200 text-indigo-700 flex items-center justify-center font-bold text-xs font-mono dark:bg-indigo-950 dark:border-indigo-800 dark:text-indigo-300 shrink-0 shadow-2xs">
                    {user?.name ? user.name.substring(0, 2).toUpperCase() : 'US'}
                  </div>
                  <div className="min-w-0">
                    <div className="text-xs font-semibold text-slate-900 dark:text-white truncate">{user?.name || 'User'}</div>
                    <div className="text-[10px] text-slate-500 dark:text-slate-400 font-mono truncate">{user?.tenant_id}</div>
                  </div>
                </div>
                <button
                  onClick={logout}
                  title="Sign Out"
                  className="p-1.5 rounded-lg text-slate-500 hover:text-rose-600 hover:bg-rose-50 dark:text-slate-400 dark:hover:text-rose-400 dark:hover:bg-rose-500/10 transition-colors cursor-pointer"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>

              <div className="p-2 rounded-lg border border-slate-200 bg-white dark:border-slate-800 dark:bg-[#0f1422] text-xs font-mono space-y-1">
                <div className="flex justify-between items-center text-slate-500 text-[10px]">
                  <span>TENANT ISOLATION</span>
                  <span className="text-emerald-600 font-bold dark:text-emerald-400">ENFORCED</span>
                </div>
                <div className="flex justify-between items-center text-[10px] text-slate-400">
                  <span>ENGINES</span>
                  <span className="font-semibold text-slate-700 dark:text-slate-300">368 Active</span>
                </div>
              </div>
            </>
          ) : (
            <div className="flex flex-col items-center gap-2">
              <div
                className="h-8 w-8 rounded-lg bg-indigo-50 border border-indigo-200 text-indigo-700 flex items-center justify-center font-bold text-xs font-mono dark:bg-indigo-950 dark:border-indigo-800 dark:text-indigo-300 shadow-2xs cursor-default"
                title={`${user?.name || 'User'} (${user?.tenant_id || ''})`}
              >
                {user?.name ? user.name.substring(0, 2).toUpperCase() : 'US'}
              </div>
              <button
                onClick={logout}
                title="Sign Out"
                className="p-1.5 rounded-lg text-slate-500 hover:text-rose-600 hover:bg-rose-50 dark:text-slate-400 dark:hover:text-rose-400 dark:hover:bg-rose-500/10 transition-colors cursor-pointer"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      </aside>

      {/* Mobile Overlay */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-xs z-20 md:hidden"
          onClick={onCloseSidebar}
        />
      )}

      {/* Dynamic Route Content with Smooth Transition */}
      <main
        className={`flex-1 ${
          isCollapsed ? 'md:ml-20' : 'md:ml-64'
        } overflow-y-auto h-[calc(100vh-3.5rem)] px-3 sm:px-5 py-5 bg-[#f8fafc] dark:bg-[#090d16] w-full min-w-0 transition-all duration-300`}
      >

        {activeNav === 'search' && (
          <SearchPage
            initialTarget={searchTarget?.query}
            initialTargetType={searchTarget?.targetType}
            onOpenInvestigation={handleOpenInvestigationFromSearch}
            onNavigateToInvestigation={(invId) => {
              setSelectedInvId(invId);
              setActiveNav('investigations');
            }}
          />
        )}
        {activeNav === 'investigations' && (
          <InvestigationsPage
            selectedInvestigationId={selectedInvId}
            onNavigateToSearch={(target, targetType) => {
              setSearchTarget({ query: target, targetType });
              setActiveNav('search');
            }}
          />
        )}
        {activeNav === 'entities' && <EntitiesPage />}
        {activeNav === 'graph' && <GraphStudioPage />}
        {activeNav === 'map' && <MapPage />}
        {activeNav === 'findings' && <FindingsPage />}
        {activeNav === 'evidence' && <EvidencePage />}
        {activeNav === 'reports' && <ReportsPage />}
      </main>
    </div>
  );
};

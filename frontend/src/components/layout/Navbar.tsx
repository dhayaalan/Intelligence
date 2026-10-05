import React from 'react';
import { Shield, Search, LogOut, Menu, X, Building, Sun, Moon } from 'lucide-react';
import { useAuth } from '../../core/auth/AuthContext';
import { useTheme } from '../../core/theme/ThemeContext';

interface NavbarProps {
  onOpenCommandPalette: () => void;
  onToggleSidebar: () => void;
  isSidebarOpen: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ onOpenCommandPalette, onToggleSidebar, isSidebarOpen }) => {
  const { user, logout } = useAuth();
  const { isDark, toggleTheme } = useTheme();

  return (
    <header className="h-14 border-b border-slate-200/80 bg-white/95 backdrop-blur-md sticky top-0 z-40 px-4 flex items-center justify-between dark:border-slate-800/80 dark:bg-[#0e131f]/95 shadow-xs">
      <div className="flex items-center gap-3">
        {/* Mobile Menu Toggle */}
        <button
          onClick={onToggleSidebar}
          className="md:hidden p-1.5 rounded-lg text-slate-600 hover:text-black hover:bg-slate-100 dark:text-slate-400 dark:hover:text-white dark:hover:bg-slate-800"
          aria-label="Toggle menu"
        >
          {isSidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>

        {/* Logo & Platform Name */}
        <div className="flex items-center gap-2.5 cursor-pointer select-none">
          <div className="w-7 h-7 rounded-lg bg-indigo-600 text-white flex items-center justify-center font-bold text-xs shadow-sm shadow-indigo-600/30">
            <Shield className="w-4 h-4" />
          </div>
          <div className="flex items-center">
            <span className="font-bold tracking-tight text-sm text-slate-900 dark:text-white uppercase font-sans">
              SENTIAL
            </span>
            <span className="text-[10px] text-indigo-600 font-mono ml-2 px-1.5 py-0.5 rounded border border-indigo-200 bg-indigo-50/70 dark:border-indigo-900/60 dark:bg-indigo-950/40 dark:text-indigo-400 font-semibold hidden sm:inline-block">
              INTEL PLATFORM
            </span>
          </div>
        </div>

        {/* Workspace / Tenant Context */}
        {user && (
          <div className="hidden lg:flex items-center ml-4 pl-4 border-l border-slate-200 dark:border-slate-800 text-xs">
            <Building className="w-3.5 h-3.5 text-slate-400 mr-2" />
            <span className="font-semibold text-slate-900 dark:text-white">{user.tenant_id}</span>
          </div>
        )}
      </div>

      {/* Center: Global Search Bar & Actions */}
      <div className="flex items-center gap-2.5">
        <button
          onClick={onOpenCommandPalette}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-100/80 border border-slate-200/80 text-xs text-slate-500 hover:text-slate-900 hover:border-slate-300 transition-all w-44 sm:w-56 justify-between dark:bg-slate-900 dark:border-slate-800 dark:text-slate-400 dark:hover:text-white"
        >
          <div className="flex items-center gap-2 truncate">
            <Search className="w-3.5 h-3.5 text-slate-400" />
            <span className="font-mono text-[11px]">Search intelligence...</span>
          </div>
          <kbd className="hidden sm:inline-block text-[10px] bg-white border border-slate-200 px-1.5 py-0.5 rounded font-mono text-slate-500 dark:bg-slate-800 dark:border-slate-700 dark:text-slate-400 shadow-2xs">
            ⌘K
          </kbd>
        </button>

        {/* Theme Toggle Button */}
        <button
          onClick={toggleTheme}
          title={isDark ? 'Switch to Light Theme' : 'Switch to Dark Theme'}
          className="p-1.5 rounded-lg text-slate-600 hover:text-black hover:bg-slate-100 transition-colors dark:text-slate-400 dark:hover:text-white dark:hover:bg-slate-800"
          aria-label="Toggle theme"
        >
          {isDark ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-600" />}
        </button>

        {/* User Profile & Role Clearance */}
        <div className="flex items-center gap-2 pl-2 border-l border-slate-200 dark:border-slate-800">
          {user && (
            <div className="hidden sm:flex items-center gap-1.5 font-mono text-[11px]">
              {user.role === 'USER' ? (
                <button
                  type="button"
                  onClick={async () => {
                    await logout();
                    window.location.href = '/login';
                  }}
                  title="Currently logged in as Investigator (OSINT only). Click to switch to Analyst for 368 engines."
                  className="px-2 py-0.5 rounded bg-amber-50 border border-amber-200 text-amber-800 dark:bg-amber-950/40 dark:border-amber-800 dark:text-amber-300 hover:border-amber-400 transition-colors"
                >
                  INVESTIGATOR (OSINT) • SWITCH TO ANALYST ↗
                </button>
              ) : user.role === 'ANALYST' ? (
                <span className="px-2 py-0.5 rounded bg-emerald-50 border border-emerald-200 text-emerald-800 dark:bg-emerald-950/40 dark:border-emerald-800 dark:text-emerald-300 font-semibold">
                  LEAD ANALYST (368 ENGINES)
                </span>
              ) : user.role === 'TENANT_ADMIN' ? (
                <span className="px-2 py-0.5 rounded bg-blue-50 border border-blue-200 text-blue-800 dark:bg-blue-950/40 dark:border-blue-800 dark:text-blue-300 font-semibold">
                  TENANT ADMIN
                </span>
              ) : (
                <span className="px-2 py-0.5 rounded bg-purple-50 border border-purple-200 text-purple-800 dark:bg-purple-950/40 dark:border-purple-800 dark:text-purple-300 font-semibold">
                  SUPER ADMIN
                </span>
              )}
            </div>
          )}

          <div
            className="w-7 h-7 rounded-lg bg-indigo-50 border border-indigo-200 text-indigo-700 flex items-center justify-center text-xs font-bold font-mono dark:bg-indigo-950 dark:border-indigo-800 dark:text-indigo-300 shadow-2xs"
            title={`${user?.name || 'User'} (${user?.email || ''})`}
          >
            {user?.name ? user.name.substring(0, 2).toUpperCase() : 'US'}
          </div>
          <button
            onClick={logout}
            title="Sign Out"
            className="p-1.5 rounded-lg text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition-colors dark:text-slate-400 dark:hover:text-white dark:hover:bg-slate-800"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
};

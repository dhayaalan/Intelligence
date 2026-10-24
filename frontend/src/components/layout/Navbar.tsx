import React, { useState } from 'react';
import {
  Shield,
  Search,
  LogOut,
  Menu,
  X,
  Building,
  Sun,
  Moon,
  Filter,
  CheckCircle2,
  ChevronDown,
  UserCheck
} from 'lucide-react';
import { useAuth } from '../../core/auth/AuthContext';
import { useTheme } from '../../core/theme/ThemeContext';

interface NavbarProps {
  onOpenCommandPalette: () => void;
  onToggleSidebar: () => void;
  isSidebarOpen: boolean;
  onExecuteUniversalSearch?: (query: string, moduleFilter?: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  onOpenCommandPalette,
  onToggleSidebar,
  isSidebarOpen,
  onExecuteUniversalSearch,
}) => {
  const { user, logout } = useAuth();
  const { isDark, toggleTheme } = useTheme();
  const [navSearchQuery, setNavSearchQuery] = useState('');
  const [selectedModuleFilter, setSelectedModuleFilter] = useState('all');
  const [isFilterDropdownOpen, setIsFilterDropdownOpen] = useState(false);

  const moduleOptions = [
    { id: 'all', label: 'All Modules' },
    { id: 'osint', label: 'OSINT' },
    { id: 'social_media_intelligence', label: 'Social Intel' },
    { id: 'news_intelligence', label: 'News Intel' },
    { id: 'media_intelligence', label: 'Media Forensics' },
    { id: 'threat_intelligence', label: 'Threat Intel' },
    { id: 'geo_intelligence', label: 'Location (GIS)' },
  ];

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!navSearchQuery.trim()) {
      onOpenCommandPalette();
      return;
    }
    if (onExecuteUniversalSearch) {
      onExecuteUniversalSearch(navSearchQuery.trim(), selectedModuleFilter);
    }
  };

  return (
    <header className="h-14 border-b border-slate-200/80 bg-white/95 backdrop-blur-md sticky top-0 z-40 px-3 sm:px-4 flex items-center justify-between dark:border-slate-800/80 dark:bg-[#070b13]/95 shadow-xs transition-colors">
      <div className="flex items-center gap-3">
        {/* Mobile Menu Toggle */}
        <button
          onClick={onToggleSidebar}
          className="md:hidden p-1.5 rounded-lg text-slate-600 hover:text-black hover:bg-slate-100 dark:text-slate-400 dark:hover:text-white dark:hover:bg-slate-800 transition-colors"
          aria-label="Toggle navigation menu"
        >
          {isSidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>

        {/* Logo & Platform Wordmark */}
        <div className="flex items-center gap-2.5 cursor-pointer select-none">
          <div className="w-7 h-7 rounded-lg bg-indigo-600 text-white flex items-center justify-center font-bold text-xs shadow-sm shadow-indigo-600/30">
            <Shield className="w-4 h-4" />
          </div>
          <div className="flex items-center">
            <span className="font-extrabold tracking-tight text-sm text-slate-900 dark:text-white uppercase font-sans">
              SENTIAL
            </span>
            <span className="text-[10px] text-indigo-600 font-mono ml-2 px-1.5 py-0.5 rounded border border-indigo-200 bg-indigo-50/70 dark:border-indigo-900/60 dark:bg-indigo-950/40 dark:text-indigo-400 font-bold hidden sm:inline-block">
              INTELLIGENCE SAAS
            </span>
          </div>
        </div>

        {/* Workspace / Tenant Context Badge */}
        {user && (
          <div className="hidden xl:flex items-center ml-3 pl-3 border-l border-slate-200 dark:border-slate-800 text-xs font-mono">
            <Building className="w-3.5 h-3.5 text-slate-400 mr-1.5" />
            <span className="text-slate-400 mr-1">TENANT:</span>
            <span className="font-bold text-slate-900 dark:text-white bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded">
              {user.tenant_id}
            </span>
          </div>
        )}
      </div>

      {/* Center: Persistent Universal Search Bar */}
      <form onSubmit={handleSearchSubmit} className="hidden md:flex items-center gap-2 flex-1 max-w-2xl mx-2 lg:mx-6 min-w-0">
        <div className="relative flex-1 flex items-center min-w-0">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 pointer-events-none" />
          <input
            type="text"
            value={navSearchQuery}
            onChange={(e) => setNavSearchQuery(e.target.value)}
            placeholder="Universal search (domain, IP, handle, email, hash)..."
            className="w-full pl-9 pr-12 py-1.5 rounded-lg bg-slate-100/80 border border-slate-200/80 text-xs text-slate-900 dark:text-white font-mono placeholder:text-slate-400 focus:outline-hidden focus:ring-2 focus:ring-indigo-500/30 focus:border-indigo-500 dark:bg-slate-900/80 dark:border-slate-800 transition-all"
          />
          <button
            type="button"
            onClick={onOpenCommandPalette}
            className="absolute right-2 px-1.5 py-0.5 rounded bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-[10px] font-mono text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors"
            title="Open Command Palette"
          >
            ⌘K
          </button>
        </div>

        {/* Module Scope Dropdown */}
        <div className="relative">
          <button
            type="button"
            onClick={() => setIsFilterDropdownOpen((prev) => !prev)}
            className="h-8 px-2.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-100/60 dark:bg-slate-900 text-[11px] font-mono text-slate-600 dark:text-slate-300 flex items-center gap-1.5 hover:bg-slate-200/60 dark:hover:bg-slate-800 transition-colors cursor-pointer"
          >
            <Filter className="w-3 h-3 text-slate-400" />
            <span className="truncate max-w-[90px]">
              {moduleOptions.find((m) => m.id === selectedModuleFilter)?.label || 'All'}
            </span>
            <ChevronDown className="w-3 h-3 text-slate-400" />
          </button>

          {isFilterDropdownOpen && (
            <div className="absolute right-0 mt-1 w-44 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-lg py-1 z-50 text-xs font-mono">
              {moduleOptions.map((opt) => (
                <button
                  key={opt.id}
                  type="button"
                  onClick={() => {
                    setSelectedModuleFilter(opt.id);
                    setIsFilterDropdownOpen(false);
                  }}
                  className={`w-full text-left px-3 py-1.5 transition-colors cursor-pointer flex items-center justify-between ${
                    selectedModuleFilter === opt.id
                      ? 'bg-indigo-50 text-indigo-700 dark:bg-indigo-950/60 dark:text-indigo-300 font-bold'
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800'
                  }`}
                >
                  <span>{opt.label}</span>
                  {selectedModuleFilter === opt.id && <CheckCircle2 className="w-3.5 h-3.5 text-indigo-500" />}
                </button>
              ))}
            </div>
          )}
        </div>
      </form>

      {/* Right Controls: Core Health, Theme, User Profile */}
      <div className="flex items-center gap-2">
        {/* Core Live Status Pill */}
        <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400 font-mono text-[10px] font-bold">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
          <span>LIVE CORE</span>
        </div>

        {/* Theme Toggle Button */}
        <button
          onClick={toggleTheme}
          title={isDark ? 'Switch to Light Theme' : 'Switch to Dark Theme'}
          className="p-1.5 rounded-lg text-slate-600 hover:text-black hover:bg-slate-100 dark:text-slate-400 dark:hover:text-white dark:hover:bg-slate-800 transition-colors cursor-pointer"
          aria-label="Toggle theme"
        >
          {isDark ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-600" />}
        </button>

        {/* Role & User Clearance Pill */}
        {user && (
          <div className="flex items-center gap-2 pl-2 border-l border-slate-200 dark:border-slate-800 shrink-0">
            <div className="hidden sm:flex flex-col items-end text-right font-mono">
              <span className="text-xs font-bold text-slate-900 dark:text-white truncate max-w-[180px] lg:max-w-[220px]" title={user.name || user.email}>
                {user.name || user.email}
              </span>
              <span
                className={`text-[9px] font-bold uppercase px-1 rounded ${
                  user.role === 'SUPER_ADMIN'
                    ? 'text-purple-600 dark:text-purple-400 bg-purple-50 dark:bg-purple-950/60'
                    : user.role === 'TENANT_ADMIN'
                    ? 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/60'
                    : 'text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60'
                }`}
              >
                {user.role}
              </span>
            </div>

            {/* Logout button */}
            <button
              onClick={logout}
              title="Sign Out"
              className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/40 dark:hover:text-rose-400 transition-colors cursor-pointer"
              aria-label="Sign out"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </header>
  );
};

import React, { useState, useRef, useEffect } from 'react';
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
  Play,
  Check,
  CheckSquare,
  Square,
  Globe,
  ShieldAlert,
  Users,
  Newspaper,
  Camera,
  MapPin
} from 'lucide-react';
import { useAuth } from '../../core/auth/AuthContext';
import { useTheme } from '../../core/theme/ThemeContext';

export interface ModuleOption {
  id: string;
  label: string;
  shortLabel: string;
  desc: string;
  icon: React.ReactNode;
}

export const AVAILABLE_MODULES: ModuleOption[] = [
  {
    id: 'osint',
    label: 'Open-Source Intelligence (OSINT)',
    shortLabel: 'OSINT',
    desc: 'Domain, WHOIS, DNS, and identity recon',
    icon: <Globe className="w-3.5 h-3.5 text-indigo-500" />,
  },
  {
    id: 'threat_intelligence',
    label: 'Threat Intelligence & Attack Surface',
    shortLabel: 'Threat Intel',
    desc: 'OWASP ZAP, Shodan port recon, and CVEs',
    icon: <ShieldAlert className="w-3.5 h-3.5 text-rose-500" />,
  },
  {
    id: 'social_media_intelligence',
    label: 'Social Media Intelligence',
    shortLabel: 'Social Intel',
    desc: 'Cross-platform usernames, avatars, and posts',
    icon: <Users className="w-3.5 h-3.5 text-blue-500" />,
  },
  {
    id: 'news_intelligence',
    label: 'News Intelligence & Wire',
    shortLabel: 'News Intel',
    desc: 'Real-time media leaks, articles, and sentiment',
    icon: <Newspaper className="w-3.5 h-3.5 text-amber-500" />,
  },
  {
    id: 'media_intelligence',
    label: 'Media Forensics & Deepfake Intel',
    shortLabel: 'Media Forensics',
    desc: 'C2PA manifests, EXIF metadata, and ANPR',
    icon: <Camera className="w-3.5 h-3.5 text-purple-500" />,
  },
  {
    id: 'geo_intelligence',
    label: 'Location & Geospatial Intelligence',
    shortLabel: 'Location (GIS)',
    desc: 'Coordinate resolution, maps, and flight radar',
    icon: <MapPin className="w-3.5 h-3.5 text-emerald-500" />,
  },
];

const ALL_MODULE_IDS = AVAILABLE_MODULES.map((m) => m.id);

interface NavbarProps {
  onOpenCommandPalette: () => void;
  onToggleSidebar: () => void;
  isSidebarOpen: boolean;
  onExecuteUniversalSearch?: (query: string, selectedModules: string[]) => void;
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
  const [selectedModules, setSelectedModules] = useState<string[]>(ALL_MODULE_IDS);
  const [isFilterDropdownOpen, setIsFilterDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement | null>(null);

  const isAllSelected = selectedModules.length === ALL_MODULE_IDS.length;

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsFilterDropdownOpen(false);
      }
    };
    if (isFilterDropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isFilterDropdownOpen]);

  const toggleModule = (id: string) => {
    if (selectedModules.includes(id)) {
      // Don't allow 0 modules; if only 1 is active, keep it
      if (selectedModules.length > 1) {
        setSelectedModules(selectedModules.filter((m) => m !== id));
      }
    } else {
      setSelectedModules([...selectedModules, id]);
    }
  };

  const handleSelectAll = () => {
    if (isAllSelected) {
      // If all selected, keep only OSINT and Threat Intel as minimal default
      setSelectedModules(['osint', 'threat_intelligence']);
    } else {
      setSelectedModules(ALL_MODULE_IDS);
    }
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!navSearchQuery.trim()) {
      onOpenCommandPalette();
      return;
    }
    if (onExecuteUniversalSearch) {
      onExecuteUniversalSearch(navSearchQuery.trim(), selectedModules);
    }
  };

  const getDropdownLabel = () => {
    if (isAllSelected) return 'All Modules (6)';
    if (selectedModules.length === 1) {
      const match = AVAILABLE_MODULES.find((m) => m.id === selectedModules[0]);
      return match ? match.shortLabel : '1 Module';
    }
    return `${selectedModules.length} Modules`;
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

      {/* Center: Persistent Universal Search Bar with Multi-Module Selector & Execute Button */}
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
            className="absolute right-2 px-1.5 py-0.5 rounded bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-[10px] font-mono text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors cursor-pointer"
            title="Open Command Palette (⌘K)"
          >
            ⌘K
          </button>
        </div>

        {/* Multi-Module Scope Dropdown */}
        <div className="relative" ref={dropdownRef}>
          <button
            type="button"
            onClick={() => setIsFilterDropdownOpen((prev) => !prev)}
            className="h-8 px-2.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-100/60 dark:bg-slate-900 text-[11px] font-mono text-slate-700 dark:text-slate-300 flex items-center gap-1.5 hover:bg-slate-200/60 dark:hover:bg-slate-800 transition-colors cursor-pointer shrink-0"
            title="Select target intelligence modules"
          >
            <Filter className="w-3 h-3 text-indigo-500" />
            <span className="truncate max-w-[110px] font-semibold">{getDropdownLabel()}</span>
            <ChevronDown className="w-3 h-3 text-slate-400" />
          </button>

          {isFilterDropdownOpen && (
            <div className="absolute right-0 mt-1.5 w-72 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-xl py-2 z-50 text-xs font-mono animate-in fade-in zoom-in-95 duration-150">
              <div className="flex items-center justify-between px-3 pb-2 border-b border-slate-100 dark:border-slate-800 text-[11px]">
                <span className="font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                  Target Modules ({selectedModules.length}/6)
                </span>
                <button
                  type="button"
                  onClick={handleSelectAll}
                  className="text-indigo-600 dark:text-indigo-400 hover:underline font-bold text-[10px] cursor-pointer"
                >
                  {isAllSelected ? 'Deselect All' : 'Select All'}
                </button>
              </div>

              <div className="max-h-64 overflow-y-auto py-1 divide-y divide-slate-100/60 dark:divide-slate-800/60">
                {AVAILABLE_MODULES.map((opt) => {
                  const isChecked = selectedModules.includes(opt.id);
                  return (
                    <button
                      key={opt.id}
                      type="button"
                      onClick={() => toggleModule(opt.id)}
                      className={`w-full text-left px-3 py-2 transition-colors cursor-pointer flex items-start gap-2.5 hover:bg-slate-50 dark:hover:bg-slate-800/60 ${
                        isChecked ? 'bg-indigo-50/40 dark:bg-indigo-950/20' : ''
                      }`}
                    >
                      <div className="mt-0.5 shrink-0">
                        {isChecked ? (
                          <div className="w-4 h-4 rounded bg-indigo-600 text-white flex items-center justify-center">
                            <Check className="w-3 h-3 stroke-[3]" />
                          </div>
                        ) : (
                          <div className="w-4 h-4 rounded border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800" />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-1.5">
                          {opt.icon}
                          <span className={`font-semibold text-xs truncate ${isChecked ? 'text-slate-900 dark:text-white' : 'text-slate-500'}`}>
                            {opt.shortLabel}
                          </span>
                        </div>
                        <p className="text-[10px] text-slate-400 dark:text-slate-500 truncate mt-0.5">
                          {opt.desc}
                        </p>
                      </div>
                    </button>
                  );
                })}
              </div>

              <div className="px-3 pt-2 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-[10px] text-slate-400">
                <span>Multi-module execution enabled</span>
                <button
                  type="button"
                  onClick={() => setIsFilterDropdownOpen(false)}
                  className="font-bold text-slate-700 dark:text-slate-300 hover:text-indigo-600 cursor-pointer"
                >
                  Done
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Explicit Execute Search Button */}
        <button
          type="submit"
          className="h-8 px-3.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 active:scale-98 text-white font-mono text-xs font-bold flex items-center gap-1.5 transition-all cursor-pointer shadow-xs shadow-indigo-600/30 shrink-0"
          title="Execute multi-module intelligence search across selected engines"
        >
          <Play className="w-3 h-3 fill-current" />
          <span>Execute</span>
        </button>
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

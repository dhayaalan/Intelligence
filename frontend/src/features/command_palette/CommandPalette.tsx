import React, { useState, useEffect } from 'react';
import {
  Search,
  FolderPlus,
  FileText,
  X,
  Shield,
  ArrowRight,
  Globe,
  Radio,
  Layers,
  Sparkles,
  Command,
} from 'lucide-react';
import { Badge } from '../../components/ui/Badge';

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  onNavigate: (view: string) => void;
  onExecuteSearch: (query: string) => void;
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({
  isOpen,
  onClose,
  onNavigate,
  onExecuteSearch,
}) => {
  const [query, setQuery] = useState('');

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        if (isOpen) onClose();
        else setQuery('');
      }
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onExecuteSearch(query.trim());
      onClose();
    }
  };

  const quickActions = [
    {
      id: 'search',
      title: 'Target Reconnaissance Across 368 Engines',
      subtitle: 'Dispatch OSINT & Cyber Threat Intelligence pipelines',
      icon: Search,
      iconColor: 'text-indigo-600 dark:text-indigo-400',
      badge: 'Enter',
      action: () => {
        if (query.trim()) onExecuteSearch(query.trim());
        else onNavigate('search');
        onClose();
      },
    },
    {
      id: 'investigations',
      title: 'Open Threat & Security Investigations',
      subtitle: 'Correlate case evidence, targets, and telemetry',
      icon: FolderPlus,
      iconColor: 'text-emerald-600 dark:text-emerald-400',
      badge: 'G then I',
      action: () => {
        onNavigate('investigations');
        onClose();
      },
    },
    {
      id: 'entities',
      title: 'Normalized Entity Explorer',
      subtitle: 'Browse unified cross-case intelligence indicators',
      icon: Layers,
      iconColor: 'text-sky-600 dark:text-sky-400',
      badge: 'G then E',
      action: () => {
        onNavigate('entities');
        onClose();
      },
    },
    {
      id: 'map',
      title: 'Geospatial Radar & Live IP Tracing',
      subtitle: 'Track active physical coordinates and ASN threat feeds',
      icon: Globe,
      iconColor: 'text-rose-600 dark:text-rose-400',
      badge: 'G then M',
      action: () => {
        onNavigate('map');
        onClose();
      },
    },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 px-4 animate-in fade-in duration-150">
      <div
        className="fixed inset-0 bg-slate-900/40 dark:bg-black/70 backdrop-blur-xs transition-opacity"
        onClick={onClose}
      />
      <div className="relative bg-white dark:bg-[#0f1422] border border-slate-200/90 dark:border-slate-800 w-full max-w-xl rounded-2xl shadow-2xl overflow-hidden transition-all z-10">
        {/* Search Input Bar */}
        <form
          onSubmit={handleSubmit}
          className="flex items-center px-4 py-3.5 border-b border-slate-200/80 dark:border-slate-800 bg-slate-50/60 dark:bg-[#090d16]/60"
        >
          <Search className="w-4 h-4 text-slate-400 dark:text-slate-500 mr-3 shrink-0" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Type a target (domain, IP, email, username) or command..."
            className="w-full bg-transparent text-xs sm:text-sm font-mono text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none"
            autoFocus
          />
          {query && (
            <button
              type="button"
              onClick={() => setQuery('')}
              className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1 mr-1 rounded"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
          <button
            type="button"
            onClick={onClose}
            className="text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 p-1 rounded-md transition-colors"
          >
            <kbd className="px-1.5 py-0.5 text-[10px] font-mono font-semibold bg-slate-200/70 dark:bg-slate-800 text-slate-600 dark:text-slate-400 rounded">
              ESC
            </kbd>
          </button>
        </form>

        {/* Actions List */}
        <div className="p-2 space-y-1 max-h-[60vh] overflow-y-auto">
          <div className="flex items-center justify-between text-[10px] font-mono font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider px-3 py-1.5">
            <span>Navigation & Quick Reconnaissance</span>
            <span>368 Engines Active</span>
          </div>

          {quickActions.map((action) => {
            const Icon = action.icon;
            return (
              <button
                key={action.id}
                type="button"
                onClick={action.action}
                className="w-full flex items-center justify-between px-3 py-2.5 text-xs text-slate-800 dark:text-slate-200 hover:bg-slate-100/90 dark:hover:bg-slate-800/60 rounded-xl transition-all font-mono group cursor-pointer text-left"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div className="w-8 h-8 rounded-lg bg-slate-100 dark:bg-slate-800/80 flex items-center justify-center shrink-0 border border-slate-200/60 dark:border-slate-700/60">
                    <Icon className={`w-4 h-4 ${action.iconColor}`} />
                  </div>
                  <div className="min-w-0">
                    <div className="font-semibold text-slate-900 dark:text-slate-100 truncate">
                      {action.title}
                    </div>
                    <div className="text-[10px] text-slate-500 dark:text-slate-400 truncate">
                      {action.subtitle}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-1.5 shrink-0 ml-2">
                  <span className="text-[10px] font-mono text-slate-400 dark:text-slate-500 group-hover:text-slate-600 dark:group-hover:text-slate-300">
                    {action.badge}
                  </span>
                  <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:translate-x-0.5 transition-transform" />
                </div>
              </button>
            );
          })}
        </div>

        {/* Footer */}
        <div className="px-4 py-2.5 bg-slate-50 dark:bg-[#090d16] border-t border-slate-200/80 dark:border-slate-800 text-[11px] text-slate-500 dark:text-slate-400 flex justify-between items-center font-mono">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1 text-[10px]">
              <kbd className="px-1 py-0.2 bg-white dark:bg-slate-800 rounded border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 font-bold">↵</kbd> Select
            </span>
            <span className="text-slate-300 dark:text-slate-700">•</span>
            <span className="inline-flex items-center gap-1 text-[10px]">
              <kbd className="px-1 py-0.2 bg-white dark:bg-slate-800 rounded border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 font-bold">ESC</kbd> Close
            </span>
          </div>

          <div className="flex items-center gap-1.5 text-[10px] text-slate-400">
            <Sparkles className="w-3 h-3 text-indigo-500" />
            <span>SENTIAL INTELLIGENCE PALETTE</span>
          </div>
        </div>
      </div>
    </div>
  );
};

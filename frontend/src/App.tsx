import React, { useState, useEffect } from 'react';
import { useAuth } from './core/auth/AuthContext';
import { LoginPage } from './features/auth/LoginPage';
import { Navbar } from './components/layout/Navbar';
import { InvestigatorShell } from './components/layout/InvestigatorShell';
import { CommandPalette } from './features/command_palette/CommandPalette';
import { initializeFrontendModules } from './modules';

export const AppContent: React.FC = () => {
  const { user, isLoading } = useAuth();
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [universalSearchQuery, setUniversalSearchQuery] = useState<string | undefined>();
  const [universalModuleFilter, setUniversalModuleFilter] = useState<string | undefined>();

  useEffect(() => {
    initializeFrontendModules();
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#070b13] flex items-center justify-center text-slate-400 font-mono text-xs">
        Initializing Sential Intelligence Core...
      </div>
    );
  }

  if (!user) {
    return <LoginPage />;
  }

  // Unified Investigator-First Platform Shell across all authorized personas
  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col font-sans">
      <Navbar
        onOpenCommandPalette={() => setIsCommandPaletteOpen(true)}
        onToggleSidebar={() => setIsSidebarOpen((prev) => !prev)}
        isSidebarOpen={isSidebarOpen}
        onExecuteUniversalSearch={(query, moduleFilter) => {
          setUniversalSearchQuery(query);
          setUniversalModuleFilter(moduleFilter);
        }}
      />

      <div className="flex-1 flex flex-col min-h-0">
        <InvestigatorShell
          isSidebarOpen={isSidebarOpen}
          onCloseSidebar={() => setIsSidebarOpen(false)}
          universalSearchQuery={universalSearchQuery}
          universalModuleFilter={universalModuleFilter}
        />
      </div>

      {/* Global Command Palette */}
      <CommandPalette
        isOpen={isCommandPaletteOpen}
        onClose={() => setIsCommandPaletteOpen(false)}
        onNavigate={(_view) => { }}
        onExecuteSearch={(query) => {
          setUniversalSearchQuery(query);
        }}
      />
    </div>
  );
};

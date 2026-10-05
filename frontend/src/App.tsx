import React, { useState, useEffect } from 'react';
import { useAuth } from './core/auth/AuthContext';
import { LoginPage } from './features/auth/LoginPage';
import { Navbar } from './components/layout/Navbar';
import { InvestigatorShell } from './components/layout/InvestigatorShell';
import { SuperAdminLayout } from './features/super_admin/SuperAdminLayout';
import { TenantAdminLayout } from './features/tenant_admin/TenantAdminLayout';
import { CommandPalette } from './features/command_palette/CommandPalette';
import { initializeFrontendModules } from './modules';

export const AppContent: React.FC = () => {
  const { user, isLoading } = useAuth();
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

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

  // 1. DEDICATED SUPER ADMIN EXPERIENCE (Sections 6 & 32)
  if (user.role === 'SUPER_ADMIN') {
    return <SuperAdminLayout />;
  }

  // 2. DEDICATED TENANT ADMIN EXPERIENCE (Sections 9 & 33)
  if (user.role === 'TENANT_ADMIN') {
    return <TenantAdminLayout />;
  }

  // 3. INVESTIGATOR & ANALYST EXPERIENCE (Search, Cases, Graph, Evidence, Findings, Reports)
  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col font-sans">
      <Navbar
        onOpenCommandPalette={() => setIsCommandPaletteOpen(true)}
        onToggleSidebar={() => setIsSidebarOpen((prev) => !prev)}
        isSidebarOpen={isSidebarOpen}
      />

      <div className="flex-1 flex flex-col min-h-0">
        <InvestigatorShell
          isSidebarOpen={isSidebarOpen}
          onCloseSidebar={() => setIsSidebarOpen(false)}
        />
      </div>

      {/* Global Command Palette */}
      <CommandPalette
        isOpen={isCommandPaletteOpen}
        onClose={() => setIsCommandPaletteOpen(false)}
        onNavigate={(_view) => { }}
        onExecuteSearch={(_query) => { }}
      />
    </div>
  );
};


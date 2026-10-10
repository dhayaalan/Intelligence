import React, { useState, useEffect, useRef } from 'react';
import { Shield, Eye, EyeOff, Lock, Mail, ArrowRight, AlertCircle, KeyRound, CheckCircle2, Cpu, Database, Fingerprint, Sun, Moon } from 'lucide-react';
import { useAuth } from '../../core/auth/AuthContext';
import { useTheme } from '../../core/theme/ThemeContext';
import { Button } from '../../components/ui/Button';

export const LoginPage: React.FC = () => {
  const { login, isLoading } = useAuth();
  const { isDark, toggleTheme } = useTheme();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  // Subtle interactive investigation network canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let width = (canvas.width = canvas.parentElement?.clientWidth || 600);
    let height = (canvas.height = canvas.parentElement?.clientHeight || 800);

    const handleResize = () => {
      if (!canvas.parentElement) return;
      width = canvas.width = canvas.parentElement.clientWidth;
      height = canvas.height = canvas.parentElement.clientHeight;
    };
    window.addEventListener('resize', handleResize);

    // Nodes representing intelligence entities (Domains, IPs, Threat Actors, Hashes)
    const nodes = Array.from({ length: 26 }, (_, i) => ({
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - 0.5) * 0.35,
      vy: (Math.random() - 0.5) * 0.35,
      radius: i % 5 === 0 ? 3.5 : 2,
      label: i % 4 === 0 ? `NODE-0${i}` : '',
      highlight: i === 0 || i === 7 || i === 14,
    }));

    const render = () => {
      ctx.clearRect(0, 0, width, height);

      // Draw subtle grid
      ctx.strokeStyle = isDark ? 'rgba(255, 255, 255, 0.02)' : 'rgba(15, 23, 42, 0.04)';
      ctx.lineWidth = 1;
      const gridSize = 40;
      for (let x = 0; x < width; x += gridSize) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
      }
      for (let y = 0; y < height; y += gridSize) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }

      // Draw connecting edges
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const dx = nodes[i].x - nodes[j].x;
          const dy = nodes[i].y - nodes[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < 130) {
            const alpha = (1 - dist / 130) * 0.15;
            ctx.strokeStyle = nodes[i].highlight || nodes[j].highlight
              ? `rgba(16, 185, 129, ${alpha * 1.5})`
              : isDark ? `rgba(255, 255, 255, ${alpha})` : `rgba(15, 23, 42, ${alpha * 0.8})`;
            ctx.beginPath();
            ctx.moveTo(nodes[i].x, nodes[i].y);
            ctx.lineTo(nodes[j].x, nodes[j].y);
            ctx.stroke();
          }
        }
      }

      // Draw nodes
      nodes.forEach((node) => {
        node.x += node.vx;
        node.y += node.vy;

        if (node.x < 0 || node.x > width) node.vx *= -1;
        if (node.y < 0 || node.y > height) node.vy *= -1;

        ctx.beginPath();
        ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
        ctx.fillStyle = node.highlight
          ? '#10b981'
          : isDark ? 'rgba(255, 255, 255, 0.4)' : 'rgba(15, 23, 42, 0.3)';
        ctx.fill();

        if (node.highlight) {
          ctx.beginPath();
          ctx.arc(node.x, node.y, node.radius + 4, 0, Math.PI * 2);
          ctx.strokeStyle = 'rgba(16, 185, 129, 0.25)';
          ctx.stroke();
        }

        if (node.label) {
          ctx.fillStyle = isDark ? 'rgba(255, 255, 255, 0.25)' : 'rgba(15, 23, 42, 0.35)';
          ctx.font = '9px monospace';
          ctx.fillText(node.label, node.x + 6, node.y + 3);
        }
      });

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animationFrameId);
    };
  }, [isDark]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await login(email, password);
    } catch (err: any) {
      setError(err?.message || 'Authentication failed. Please verify your clearance credentials.');
    }
  };

  const handleSelectPersona = (pEmail: string, pPwd: string) => {
    setEmail(pEmail);
    setPassword(pPwd);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-[#f8fafc] dark:bg-[#090d16] text-slate-900 dark:text-slate-100 flex flex-col lg:flex-row font-sans selection:bg-emerald-500/20">
      {/* Top right theme toggle for LoginPage */}
      <div className="absolute top-4 right-4 z-50">
        <button
          onClick={toggleTheme}
          type="button"
          title={isDark ? 'Switch to Light Theme' : 'Switch to Dark Theme'}
          className="p-2 rounded-xl border border-slate-200/90 bg-white/95 text-slate-700 hover:text-black hover:bg-slate-100 dark:border-slate-800 dark:bg-[#0f1422]/95 dark:text-slate-300 dark:hover:text-white shadow-xs transition-colors cursor-pointer"
          aria-label="Toggle theme"
        >
          {isDark ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-600" />}
        </button>
      </div>
      {/* LEFT SIDE: Minimal Intelligence Visual & Telemetry */}
      <div className="hidden lg:flex lg:w-1/2 relative bg-slate-100/90 dark:bg-[#0c0d10] border-r border-slate-200/90 dark:border-slate-800 overflow-hidden flex-col justify-between p-12 transition-colors">
        <canvas ref={canvasRef} className="absolute inset-0 pointer-events-none" />

        {/* Top telemetry indicator */}
        <div className="relative z-10 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg border border-emerald-500/30 bg-emerald-500/10 flex items-center justify-center">
              <Shield className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
            </div>
            <div>
              <span className="font-bold tracking-tight text-sm text-slate-900 dark:text-white font-mono">SENTIAL</span>
              <span className="text-[10px] text-slate-500 font-mono ml-2">CORE PLATFORM</span>
            </div>
          </div>

          <div className="flex items-center gap-2 px-2.5 py-1 rounded-lg bg-white/80 dark:bg-[#0f1422] border border-slate-200/90 dark:border-slate-800 text-[11px] font-mono text-slate-600 dark:text-slate-400 shadow-2xs">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            <span>FABRIC 2.0 // MONGODB ACTIVE</span>
          </div>
        </div>

        {/* Center editorial callout */}
        <div className="relative z-10 max-w-lg space-y-4">
          <div className="inline-block px-2.5 py-0.5 rounded border border-slate-200/90 dark:border-slate-800 bg-white/90 dark:bg-[#0f1422]/90 font-mono text-[11px] text-emerald-600 dark:text-emerald-400 font-semibold shadow-2xs">
            ENTERPRISE INVESTIGATION & OSINT SAAS
          </div>
          <h2 className="text-2xl xl:text-3xl font-bold tracking-tight text-slate-900 dark:text-white leading-tight font-sans">
            Unified threat correlation, multi-engine reconnaissance, and cryptographic evidentiary custody.
          </h2>
          <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed font-mono">
            Modular intelligence operations platform designed for defensive cyber teams, open-source researchers, and sovereign SOC analysts.
          </p>

          <div className="pt-4 grid grid-cols-3 gap-3 border-t border-slate-200/90 dark:border-slate-800 text-xs font-mono">
            <div className="space-y-0.5">
              <span className="text-slate-500 dark:text-slate-400 block text-[10px] flex items-center gap-1">
                <Cpu className="w-3 h-3 text-sky-500 dark:text-sky-400" /> OSINT SUITE
              </span>
              <span className="text-slate-900 dark:text-slate-200 font-semibold">335 Providers</span>
            </div>
            <div className="space-y-0.5">
              <span className="text-slate-500 dark:text-slate-400 block text-[10px] flex items-center gap-1">
                <Shield className="w-3 h-3 text-emerald-600 dark:text-emerald-400" /> THREAT INTEL
              </span>
              <span className="text-slate-900 dark:text-slate-200 font-semibold">33 Engines</span>
            </div>
            <div className="space-y-0.5">
              <span className="text-slate-500 dark:text-slate-400 block text-[10px] flex items-center gap-1">
                <Database className="w-3 h-3 text-purple-600 dark:text-purple-400" /> DATABASE
              </span>
              <span className="text-slate-900 dark:text-slate-200 font-semibold">MongoDB Primary</span>
            </div>
          </div>
        </div>

        {/* Bottom copyright / status */}
        <div className="relative z-10 flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400 font-mono">
          <span className="flex items-center gap-1.5">
            <Fingerprint className="w-3.5 h-3.5 text-slate-400" />
            STRICT TENANT ISOLATION
          </span>
          <span>© 2026 SENTIAL PLATFORM</span>
        </div>
      </div>

      {/* RIGHT SIDE: Authentication Form */}
      <div className="flex-1 flex flex-col justify-center px-6 sm:px-12 lg:px-16 xl:px-24 py-12 relative bg-[#f8fafc] dark:bg-[#090d16] transition-colors">
        <div className="max-w-md w-full mx-auto space-y-6">
          {/* Header */}
          <div className="space-y-2">
            <div className="lg:hidden flex items-center gap-2 mb-4">
              <div className="w-8 h-8 rounded-lg border border-emerald-500/30 bg-emerald-500/10 flex items-center justify-center">
                <Shield className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              </div>
              <span className="font-bold tracking-tight text-sm text-slate-900 dark:text-white font-mono">SENTIAL PLATFORM</span>
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white font-sans">
              Platform Authentication
            </h1>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Enter your authorized credentials to access your tenant workspace.
            </p>
          </div>

          {/* Security Clearance Information */}
          <div className="p-3.5 rounded-2xl border border-slate-200/90 dark:border-slate-800 bg-white dark:bg-[#0f1422] space-y-1.5 shadow-xs">
            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-1.5 text-slate-800 dark:text-slate-200 font-medium">
                <Shield className="w-3.5 h-3.5 text-cyan-600 dark:text-cyan-400" />
                <span>Enterprise Security Clearance</span>
              </div>
              <span className="text-[10px] font-mono text-emerald-600 dark:text-emerald-400 font-semibold">MongoDB Active</span>
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400">
              Sign in with your Super Admin or Organization credentials to access your isolated workspace.
            </p>
          </div>

          {/* Quick Demo Personas */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400 font-medium">
              <span>Quick Login Demo Personas:</span>
              <span className="text-[10px] text-slate-400">Click to fill</span>
            </div>
            <div className="grid grid-cols-2 gap-1.5 text-[11px]">
              <button
                type="button"
                onClick={() => {
                  setEmail('analyst@acme.com');
                  setPassword('Analyst123!');
                  setError(null);
                }}
                className="p-2 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0f1422] hover:border-emerald-500/60 hover:bg-emerald-500/5 text-left transition-all cursor-pointer shadow-2xs group"
              >
                <div className="font-semibold text-slate-800 dark:text-slate-200 group-hover:text-emerald-600 dark:group-hover:text-emerald-400">Lead Analyst</div>
                <div className="text-[10px] text-slate-400 font-mono truncate">analyst@acme.com</div>
              </button>
              <button
                type="button"
                onClick={() => {
                  setEmail('superadmin@sential.io');
                  setPassword('SuperAdmin123!');
                  setError(null);
                }}
                className="p-2 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0f1422] hover:border-purple-500/60 hover:bg-purple-500/5 text-left transition-all cursor-pointer shadow-2xs group"
              >
                <div className="font-semibold text-slate-800 dark:text-slate-200 group-hover:text-purple-600 dark:group-hover:text-purple-400">Super Admin</div>
                <div className="text-[10px] text-slate-400 font-mono truncate">superadmin@sential.io</div>
              </button>
              <button
                type="button"
                onClick={() => {
                  setEmail('admin@acme.com');
                  setPassword('TenantAdmin123!');
                  setError(null);
                }}
                className="p-2 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0f1422] hover:border-sky-500/60 hover:bg-sky-500/5 text-left transition-all cursor-pointer shadow-2xs group"
              >
                <div className="font-semibold text-slate-800 dark:text-slate-200 group-hover:text-sky-600 dark:group-hover:text-sky-400">Tenant Admin</div>
                <div className="text-[10px] text-slate-400 font-mono truncate">admin@acme.com</div>
              </button>
              <button
                type="button"
                onClick={() => {
                  setEmail('user@acme.com');
                  setPassword('User123!');
                  setError(null);
                }}
                className="p-2 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0f1422] hover:border-amber-500/60 hover:bg-amber-500/5 text-left transition-all cursor-pointer shadow-2xs group"
              >
                <div className="font-semibold text-slate-800 dark:text-slate-200 group-hover:text-amber-600 dark:group-hover:text-amber-400">Investigator</div>
                <div className="text-[10px] text-slate-400 font-mono truncate">user@acme.com</div>
              </button>
            </div>
          </div>

          {/* Error Banner */}
          {error && (
            <div className="p-3.5 rounded-xl border border-rose-500/30 bg-rose-500/10 flex items-start gap-2.5 text-xs text-rose-600 dark:text-rose-300 animate-fadeIn">
              <AlertCircle className="w-4 h-4 text-rose-500 dark:text-rose-400 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                Work Email Address
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="analyst@organization.com"
                  className="w-full h-9 pl-9 pr-3 rounded-xl bg-white border border-slate-200/90 text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-slate-900 focus:ring-1 focus:ring-slate-900 dark:bg-[#0f1422] dark:border-slate-800 dark:text-white dark:placeholder:text-slate-500 dark:focus:border-slate-400 dark:focus:ring-slate-400 transition-all font-mono shadow-2xs"
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-medium text-slate-700 dark:text-slate-300">Password</label>
                <span className="text-[11px] text-slate-400 font-mono">Min 8 characters</span>
              </div>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full h-9 pl-9 pr-9 rounded-xl bg-white border border-slate-200/90 text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-slate-900 focus:ring-1 focus:ring-slate-900 dark:bg-[#0f1422] dark:border-slate-800 dark:text-white dark:placeholder:text-slate-500 dark:focus:border-slate-400 dark:focus:ring-slate-400 transition-all font-mono shadow-2xs"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-2.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors cursor-pointer"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between text-xs pt-1">
              <label className="flex items-center gap-2 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="w-3.5 h-3.5 rounded border-slate-300 text-indigo-600 focus:ring-0 dark:border-slate-700 dark:bg-slate-900"
                />
                <span className="text-slate-600 dark:text-slate-400 text-[11px]">Remember active workstation session</span>
              </label>
            </div>

            <Button
              type="submit"
              variant="primary"
              className="w-full h-10 text-xs font-semibold mt-2 rounded-xl bg-slate-900 text-white hover:bg-slate-800 dark:bg-white dark:text-slate-950 dark:hover:bg-slate-100 shadow-xs cursor-pointer"
              isLoading={isLoading}
            >
              <span>Authenticate & Enter Workspace</span>
              <ArrowRight className="w-3.5 h-3.5 ml-1.5" />
            </Button>
          </form>

          {/* Secure Environment Notice */}
          <div className="pt-4 border-t border-slate-200/80 dark:border-slate-800 flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400 font-mono">
            <span className="flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3 text-emerald-600 dark:text-emerald-400" />
              HS256 JWT Security
            </span>
            <span>Zero Synthetic Mock Data</span>
          </div>
        </div>
      </div>
    </div>
  );
};

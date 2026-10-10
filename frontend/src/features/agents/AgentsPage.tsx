import React from 'react';
import {
  Cpu, ShieldAlert, Server, Code2, Link2, AlertCircle,
  ExternalLink, Layers, ArrowUpRight, CheckCircle2, Clock
} from 'lucide-react';
import { useMLServiceStatus } from '../../core/api/mlContractHooks';

export const AgentsPage: React.FC = () => {
  const { data: status, isLoading, error } = useMLServiceStatus();

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200/80 pb-5 dark:border-slate-800/80">
        <div>
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-xl bg-purple-500/10 text-purple-600 dark:text-purple-400">
              <Cpu className="w-5 h-5" />
            </div>
            <h1 className="text-xl font-bold text-slate-900 dark:text-white tracking-tight">
              Machine Learning & AI Integration
            </h1>
          </div>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Decoupled service boundary for external ML and autonomous inference microservices developed by the dedicated ML engineering team.
          </p>
        </div>

        {/* Status Pill */}
        <div className="flex items-center gap-2">
          {isLoading ? (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-100 dark:bg-slate-800 text-xs font-mono text-slate-500">
              <Clock className="w-3.5 h-3.5 animate-spin" />
              Checking Service...
            </div>
          ) : status?.is_configured ? (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 text-xs font-mono font-medium">
              <CheckCircle2 className="w-3.5 h-3.5" />
              External Service Connected
            </div>
          ) : (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20 text-xs font-mono font-medium">
              <AlertCircle className="w-3.5 h-3.5" />
              Integration Pending (Not Configured)
            </div>
          )}
        </div>
      </div>

      {/* Primary Integration Notice */}
      <div className="p-5 rounded-2xl border border-amber-500/20 bg-amber-500/5 dark:bg-amber-500/10">
        <div className="flex items-start gap-3">
          <ShieldAlert className="w-5 h-5 text-amber-600 dark:text-amber-400 mt-0.5 shrink-0" />
          <div className="space-y-1 text-sm">
            <h3 className="font-semibold text-amber-900 dark:text-amber-200">
              AI/ML Capabilities Decoupled to Independent ML Microservice
            </h3>
            <p className="text-amber-800/90 dark:text-amber-300/80 leading-relaxed">
              In accordance with platform architecture guidelines, internal model runtimes and LLM implementations have been removed from the core Intelligence application. Autonomous agents and neural synthesis are being developed independently by the ML team as a dedicated microservice.
            </p>
            <p className="text-xs text-amber-700 dark:text-amber-400 pt-1 font-mono">
              Contract Version: {status?.contract_version || 'v1.0.0'} • Core Application Architecture: Non-AI Intelligence Preserved
            </p>
          </div>
        </div>
      </div>

      {/* Integration Contracts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Evidence Analysis Contract */}
        <div className="p-5 rounded-2xl border border-slate-200/80 dark:border-slate-800 bg-white dark:bg-[#121826] shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-lg bg-blue-500/10 text-blue-600 dark:text-blue-400">
                <Layers className="w-4 h-4" />
              </div>
              <div>
                <h4 className="font-semibold text-slate-900 dark:text-white text-sm">
                  Evidence-Grounded Synthesis Contract
                </h4>
                <span className="text-[11px] font-mono text-slate-400">
                  POST /v1/analyze
                </span>
              </div>
            </div>
            <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-500 uppercase">
              Contract Ready
            </span>
          </div>

          <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
            Standardized contract for submitting cryptographically sealed evidence artifacts (EV-xxx) and investigator queries. Requires citations resolved strictly to verified hashes without fabricated claims.
          </p>

          <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-900/50 border border-slate-200/60 dark:border-slate-800/60 font-mono text-[11px] text-slate-600 dark:text-slate-400 space-y-1">
            <div className="flex justify-between">
              <span className="text-slate-400">Input:</span>
              <span className="text-slate-700 dark:text-slate-300">MLAnalysisRequest</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Response:</span>
              <span className="text-slate-700 dark:text-slate-300">MLAnalysisResponse</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Provenance:</span>
              <span className="text-emerald-600 dark:text-emerald-400">SHA-256 Verified</span>
            </div>
          </div>
        </div>

        {/* Persona Correlation Contract */}
        <div className="p-5 rounded-2xl border border-slate-200/80 dark:border-slate-800 bg-white dark:bg-[#121826] shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-lg bg-purple-500/10 text-purple-600 dark:text-purple-400">
                <Code2 className="w-4 h-4" />
              </div>
              <div>
                <h4 className="font-semibold text-slate-900 dark:text-white text-sm">
                  Social Persona Correlation Contract
                </h4>
                <span className="text-[11px] font-mono text-slate-400">
                  POST /v1/persona-correlation
                </span>
              </div>
            </div>
            <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-500 uppercase">
              Contract Ready
            </span>
          </div>

          <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
            Cross-platform handle correlation contract interfacing Bluesky, Telegram, Reddit, Mastodon, and YouTube. Replaces internal heuristic agents with external ML graph clustering.
          </p>

          <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-900/50 border border-slate-200/60 dark:border-slate-800/60 font-mono text-[11px] text-slate-600 dark:text-slate-400 space-y-1">
            <div className="flex justify-between">
              <span className="text-slate-400">Input:</span>
              <span className="text-slate-700 dark:text-slate-300">MLPersonaCorrelationRequest</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Response:</span>
              <span className="text-slate-700 dark:text-slate-300">MLPersonaCorrelationResponse</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Context:</span>
              <span className="text-emerald-600 dark:text-emerald-400">Tenant-Isolated Context</span>
            </div>
          </div>
        </div>
      </div>

      {/* Deployment & Environment Setup Instructions */}
      <div className="p-5 rounded-2xl border border-slate-200/80 dark:border-slate-800 bg-white dark:bg-[#121826] shadow-xs space-y-4">
        <div className="flex items-center gap-2">
          <Server className="w-4 h-4 text-slate-500" />
          <h4 className="font-semibold text-slate-900 dark:text-white text-sm">
            Integration Configuration for ML Team
          </h4>
        </div>

        <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
          When the ML team deploys the standalone ML microservice, configure the following environment variables in the Intelligence platform runtime:
        </p>

        <div className="p-4 rounded-xl bg-slate-900 text-slate-200 font-mono text-xs overflow-x-auto space-y-2">
          <div><span className="text-slate-500"># Point core application to external ML microservice</span></div>
          <div><span className="text-cyan-400">ML_SERVICE_URL</span>=http://ml-service.internal:8080</div>
          <div><span className="text-cyan-400">ML_SERVICE_API_KEY</span>=your-service-token</div>
          <div><span className="text-cyan-400">ML_SERVICE_TIMEOUT_SECONDS</span>=30</div>
        </div>

        <div className="flex items-center gap-2 text-xs text-slate-500 pt-1">
          <Link2 className="w-3.5 h-3.5" />
          <span>See contract documentation at <code className="font-mono bg-slate-100 dark:bg-slate-800 px-1 py-0.5 rounded text-[11px]">docs/migration/ML_TEAM_INTEGRATION_CONTRACT.md</code></span>
        </div>
      </div>
    </div>
  );
};

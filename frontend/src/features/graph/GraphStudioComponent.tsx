import React, { useState, useMemo, useCallback } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType,
  Handle,
  Position,
  NodeProps,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Entity, Relationship } from '../../types';
import { Badge } from '../../components/ui/Badge';
import {
  Globe,
  Server,
  User,
  Hash,
  Mail,
  Info,
  Filter,
  Network,
  Search,
  Building2,
  FileText,
  Shield,
  Layers,
  ExternalLink,
} from 'lucide-react';

interface Props {
  investigationId?: string;
  entities: Entity[];
  relationships?: Relationship[];
  onRunSearch?: () => void;
  isSearching?: boolean;
}

export type LayoutMode = 'INVESTIGATION_TIERS' | 'SPACED_RADIAL' | 'GRID_COLUMNS';

export const getEntityCategory = (type: string = '') => {
  const t = type.toUpperCase();
  if (['PERSON', 'THREAT_ACTOR', 'USERNAME', 'AUTHOR'].includes(t)) return 'PERSON';
  if (['ORGANIZATION', 'ORG', 'COMPANY', 'GROUP', 'NGO', 'FOUNDATION', 'TERROR_GROUP'].includes(t)) return 'ORGANIZATION';
  if (['VULNERABILITY', 'CVE', 'THREAT_INDICATOR', 'MALWARE'].includes(t)) return 'THREAT_INDICATOR';
  if (['IP', 'IPV4', 'IPV6'].includes(t)) return 'IP';
  if (['HASH', 'SHA256', 'MD5'].includes(t)) return 'HASH';
  if (['EMAIL'].includes(t)) return 'EMAIL';
  if (['URL', 'DOCUMENT'].includes(t)) return 'DOCUMENT';
  return 'DOMAIN';
};

const getEntityCategoryIcon = (category: string) => {
  switch (category) {
    case 'PERSON':
      return User;
    case 'ORGANIZATION':
      return Building2;
    case 'DOCUMENT':
      return FileText;
    case 'THREAT_INDICATOR':
      return Shield;
    case 'IP':
      return Server;
    case 'HASH':
      return Hash;
    case 'EMAIL':
      return Mail;
    case 'DOMAIN':
    default:
      return Globe;
  }
};

const getNodeTheme = (category: string, isHighRisk: boolean) => {
  if (isHighRisk) {
    return {
      border: 'border-rose-500 dark:border-rose-600',
      bg: 'bg-rose-50/95 dark:bg-[#1a0f14]',
      badge: 'bg-rose-100 text-rose-800 dark:bg-rose-950/80 dark:text-rose-300',
      ring: 'ring-rose-500/40',
    };
  }
  switch (category) {
    case 'PERSON':
      return {
        border: 'border-amber-500 dark:border-amber-600',
        bg: 'bg-amber-50/95 dark:bg-[#1a160d]',
        badge: 'bg-amber-100 text-amber-900 dark:bg-amber-950/80 dark:text-amber-300',
        ring: 'ring-amber-500/40',
      };
    case 'ORGANIZATION':
      return {
        border: 'border-indigo-500 dark:border-indigo-600',
        bg: 'bg-indigo-50/95 dark:bg-[#101424]',
        badge: 'bg-indigo-100 text-indigo-900 dark:bg-indigo-950/80 dark:text-indigo-300',
        ring: 'ring-indigo-500/40',
      };
    case 'THREAT_INDICATOR':
      return {
        border: 'border-rose-500 dark:border-rose-600',
        bg: 'bg-rose-50/95 dark:bg-[#1a0f14]',
        badge: 'bg-rose-100 text-rose-800 dark:bg-rose-950/80 dark:text-rose-300',
        ring: 'ring-rose-500/40',
      };
    default:
      return {
        border: 'border-slate-300 dark:border-slate-700',
        bg: 'bg-white dark:bg-[#0f1422]',
        badge: 'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300',
        ring: 'ring-slate-400/40',
      };
  }
};

// =============================================================================
// DISINFOLAB ACTOR ASSETS & VISUAL SILHOUETTES (Direct Match to Diagram)
// =============================================================================
interface ActorAsset {
  role: string;
  isPerson: boolean;
  avatarRing: string;
  avatarBg: string;
  svgBadge: React.ReactNode;
}

const getDisinfoLabAsset = (identifier: string): ActorAsset | null => {
  const id = identifier.toLowerCase().trim();

  // 1. Abdul Malik Mujahid
  if (id.includes('abdul malik') || id.includes('mujahid')) {
    return {
      role: 'President (1990s) ICNA / Founder',
      isPerson: true,
      avatarRing: 'ring-amber-500 border-2 border-white',
      avatarBg: 'bg-amber-100 dark:bg-amber-950',
      svgBadge: (
        <svg viewBox="0 0 100 100" className="w-full h-full">
          <circle cx="50" cy="50" r="48" fill="#e2e8f0" />
          <circle cx="50" cy="40" r="20" fill="#cbd5e1" />
          <path d="M 35 44 Q 50 62 65 44" fill="#94a3b8" />
          <rect x="36" y="34" width="28" height="6" rx="2" fill="#475569" />
          <path d="M 22 84 Q 50 68 78 84" fill="#1e293b" />
        </svg>
      ),
    };
  }

  // 2. Shaik Ubaid
  if (id.includes('shaik ubaid') || id.includes('ubaid')) {
    return {
      role: 'Founder IAMC / Co-Founder Burma TF',
      isPerson: true,
      avatarRing: 'ring-blue-500 border-2 border-white',
      avatarBg: 'bg-blue-100 dark:bg-blue-950',
      svgBadge: (
        <svg viewBox="0 0 100 100" className="w-full h-full">
          <circle cx="50" cy="50" r="48" fill="#e2e8f0" />
          <circle cx="50" cy="38" r="18" fill="#cbd5e1" />
          <path d="M 38 42 Q 50 58 62 42" fill="#64748b" />
          <rect x="38" y="33" width="24" height="5" rx="2" fill="#334155" />
          <path d="M 24 84 Q 50 70 76 84" fill="#0f172a" />
        </svg>
      ),
    };
  }

  // 3. Ajit Sahi
  if (id.includes('ajit sahi') || id.includes('sahi')) {
    return {
      role: 'Advocacy Director, IAMC',
      isPerson: true,
      avatarRing: 'ring-red-500 border-2 border-white',
      avatarBg: 'bg-red-100 dark:bg-red-950',
      svgBadge: (
        <svg viewBox="0 0 100 100" className="w-full h-full">
          <circle cx="50" cy="50" r="48" fill="#f1f5f9" />
          <path d="M 32 28 Q 50 20 68 28" fill="#334155" />
          <circle cx="50" cy="40" r="18" fill="#cbd5e1" />
          <rect x="36" y="36" width="28" height="6" rx="2" fill="#1e293b" />
          <path d="M 22 84 Q 50 68 78 84" fill="#090d16" />
        </svg>
      ),
    };
  }

  // 4. Ahmadullah Siddiqi
  if (id.includes('ahmadullah') || id.includes('siddiqi')) {
    return {
      role: 'Founder SIMI / Exec Dir Sound Vision',
      isPerson: true,
      avatarRing: 'ring-emerald-600 border-2 border-white',
      avatarBg: 'bg-emerald-100 dark:bg-emerald-950',
      svgBadge: (
        <svg viewBox="0 0 100 100" className="w-full h-full">
          <circle cx="50" cy="50" r="48" fill="#e2e8f0" />
          <circle cx="50" cy="38" r="18" fill="#cbd5e1" />
          <path d="M 38 42 Q 50 56 62 42" fill="#475569" />
          <path d="M 24 84 Q 50 68 76 84" fill="#14532d" />
        </svg>
      ),
    };
  }

  // 5. Harsh Mander
  if (id.includes('harsh mander') || id.includes('mander')) {
    return {
      role: 'Advisory Board Member Quill / DOTO',
      isPerson: true,
      avatarRing: 'ring-purple-500 border-2 border-white',
      avatarBg: 'bg-purple-100 dark:bg-purple-950',
      svgBadge: (
        <svg viewBox="0 0 100 100" className="w-full h-full">
          <circle cx="50" cy="50" r="48" fill="#f8fafc" />
          <circle cx="50" cy="38" r="19" fill="#e2e8f0" />
          <rect x="35" y="34" width="30" height="7" rx="3" fill="#1e293b" />
          <path d="M 24 84 Q 50 68 76 84" fill="#312e81" />
        </svg>
      ),
    };
  }

  // 6. Ghulam Nabi Fai
  if (id.includes('ghulam') || id.includes('fai')) {
    return {
      role: 'Convicted ISI Agent by US Govt.',
      isPerson: true,
      avatarRing: 'ring-rose-600 border-2 border-rose-600',
      avatarBg: 'bg-rose-100 dark:bg-rose-950',
      svgBadge: (
        <svg viewBox="0 0 100 100" className="w-full h-full">
          <circle cx="50" cy="50" r="48" fill="#fee2e2" />
          <circle cx="50" cy="38" r="18" fill="#fca5a5" />
          <rect x="36" y="34" width="28" height="6" rx="2" fill="#7f1d1d" />
          <path d="M 22 84 Q 50 68 78 84" fill="#450a0a" />
        </svg>
      ),
    };
  }

  // 7. ICNA
  if (id.includes('icna') || id.includes('islamic circle')) {
    return {
      role: 'Islamic Circle of North America',
      isPerson: false,
      avatarRing: 'ring-emerald-500 border-2 border-emerald-600',
      avatarBg: 'bg-white',
      svgBadge: (
        <svg viewBox="0 0 100 100" className="w-full h-full">
          <circle cx="50" cy="50" r="46" fill="#047857" />
          <circle cx="50" cy="50" r="38" fill="#ffffff" />
          <text x="50" y="58" textAnchor="middle" fill="#047857" fontSize="22" fontWeight="900" fontFamily="sans-serif">
            ICNA
          </text>
        </svg>
      ),
    };
  }

  // 8. Burma Task Force
  if (id.includes('burma task force') || id.includes('burma')) {
    return {
      role: 'Advocacy NGO Front',
      isPerson: false,
      avatarRing: 'ring-yellow-500 border-2 border-yellow-600',
      avatarBg: 'bg-yellow-400',
      svgBadge: (
        <svg viewBox="0 0 100 100" className="w-full h-full">
          <circle cx="50" cy="50" r="46" fill="#eab308" />
          <circle cx="50" cy="50" r="38" fill="#facc15" stroke="#ca8a04" strokeWidth="2" />
          <text x="50" y="46" textAnchor="middle" fill="#000000" fontSize="11" fontWeight="900" fontFamily="sans-serif">
            BURMA
          </text>
          <text x="50" y="60" textAnchor="middle" fill="#000000" fontSize="10" fontWeight="800" fontFamily="sans-serif">
            TASK FORCE
          </text>
        </svg>
      ),
    };
  }

  // 9. IAMC
  if (id.includes('iamc') || id.includes('indian american muslim')) {
    return {
      role: 'Indian American Muslim Council',
      isPerson: false,
      avatarRing: 'ring-blue-600 border-2 border-blue-700',
      avatarBg: 'bg-white',
      svgBadge: (
        <svg viewBox="0 0 100 100" className="w-full h-full">
          <circle cx="50" cy="50" r="46" fill="#1d4ed8" />
          <circle cx="50" cy="50" r="38" fill="#ffffff" />
          <text x="50" y="56" textAnchor="middle" fill="#dc2626" fontSize="18" fontWeight="900" fontFamily="sans-serif">
            IAMC
          </text>
        </svg>
      ),
    };
  }

  // 10. Justice For All
  if (id.includes('justice for all')) {
    return {
      role: 'Project Front Entity',
      isPerson: false,
      avatarRing: 'ring-orange-500 border-2 border-orange-600',
      avatarBg: 'bg-white',
      svgBadge: (
        <svg viewBox="0 0 100 100" className="w-full h-full">
          <circle cx="50" cy="50" r="46" fill="#ea580c" />
          <circle cx="50" cy="50" r="38" fill="#ffffff" />
          <text x="50" y="48" textAnchor="middle" fill="#1e293b" fontSize="13" fontWeight="900" fontFamily="sans-serif">
            justice
          </text>
          <text x="50" y="62" textAnchor="middle" fill="#ea580c" fontSize="10" fontWeight="800" fontFamily="sans-serif">
            FOR ALL
          </text>
        </svg>
      ),
    };
  }

  // 11. Sound Vision
  if (id.includes('sound vision')) {
    return {
      role: 'Media Front of ICNA',
      isPerson: false,
      avatarRing: 'ring-teal-500 border-2 border-teal-600',
      avatarBg: 'bg-white',
      svgBadge: (
        <svg viewBox="0 0 100 100" className="w-full h-full">
          <circle cx="50" cy="50" r="46" fill="#0f766e" />
          <circle cx="50" cy="50" r="38" fill="#ffffff" />
          <text x="50" y="55" textAnchor="middle" fill="#0f766e" fontSize="11" fontWeight="800" fontFamily="sans-serif">
            Sound Vision
          </text>
        </svg>
      ),
    };
  }

  // 12. SIMI
  if (id.includes('simi')) {
    return {
      role: 'Students Islamic Movement of India',
      isPerson: false,
      avatarRing: 'ring-emerald-700 border-2 border-emerald-800',
      avatarBg: 'bg-emerald-700',
      svgBadge: (
        <svg viewBox="0 0 100 100" className="w-full h-full">
          <circle cx="50" cy="50" r="46" fill="#065f46" />
          <text x="50" y="58" textAnchor="middle" fill="#ffffff" fontSize="22" fontWeight="900" fontFamily="sans-serif">
            SIMI
          </text>
        </svg>
      ),
    };
  }

  // 13. I.S.I.
  if (id.includes('isi') || id.includes('i.s.i.')) {
    return {
      role: 'Inter-Services Intelligence',
      isPerson: false,
      avatarRing: 'ring-emerald-800 border-2 border-emerald-900',
      avatarBg: 'bg-emerald-900',
      svgBadge: (
        <svg viewBox="0 0 100 100" className="w-full h-full">
          <circle cx="50" cy="50" r="46" fill="#064e3b" />
          <circle cx="50" cy="50" r="38" fill="#ffffff" />
          <path d="M 45 35 A 15 15 0 1 0 65 55 A 12 12 0 1 1 45 35" fill="#064e3b" />
          <polygon points="62,35 65,42 72,42 67,46 69,53 62,49 56,53 58,46 53,42 60,42" fill="#064e3b" />
          <text x="50" y="80" textAnchor="middle" fill="#064e3b" fontSize="12" fontWeight="900" fontFamily="sans-serif">
            I.S.I.
          </text>
        </svg>
      ),
    };
  }

  // 14. Globally Designated Terror Groups
  if (id.includes('terror') || id.includes('designated') || id.includes('lashkar') || id.includes('jamat')) {
    return {
      role: 'Jamat-e-Islami • LeT • HM',
      isPerson: false,
      avatarRing: 'ring-rose-600 border-2 border-rose-700',
      avatarBg: 'bg-rose-50',
      svgBadge: (
        <svg viewBox="0 0 100 100" className="w-full h-full">
          <polygon points="50,10 90,85 10,85" fill="#e11d48" />
          <text x="50" y="72" textAnchor="middle" fill="#ffffff" fontSize="42" fontWeight="900" fontFamily="sans-serif">
            !
          </text>
        </svg>
      ),
    };
  }

  // 15. Helping Hand
  if (id.includes('helping hand')) {
    return {
      role: 'Sister NGO to ICNA',
      isPerson: false,
      avatarRing: 'ring-sky-500 border-2 border-sky-600',
      avatarBg: 'bg-sky-50',
      svgBadge: (
        <svg viewBox="0 0 100 100" className="w-full h-full">
          <circle cx="50" cy="50" r="46" fill="#0284c7" />
          <circle cx="50" cy="50" r="38" fill="#ffffff" />
          <text x="50" y="55" textAnchor="middle" fill="#0284c7" fontSize="10" fontWeight="900" fontFamily="sans-serif">
            HELPING HAND
          </text>
        </svg>
      ),
    };
  }

  // 16. CAG
  if (id.includes('cag') || id.includes('coalition against genocide')) {
    return {
      role: 'Coalition Against Genocide',
      isPerson: false,
      avatarRing: 'ring-rose-500 border-2 border-rose-600',
      avatarBg: 'bg-white',
      svgBadge: (
        <svg viewBox="0 0 100 100" className="w-full h-full">
          <circle cx="50" cy="50" r="46" fill="#e11d48" />
          <circle cx="50" cy="50" r="38" fill="#ffffff" />
          <text x="50" y="58" textAnchor="middle" fill="#e11d48" fontSize="16" fontWeight="900" fontFamily="sans-serif">
            CAG
          </text>
        </svg>
      ),
    };
  }

  // 17. Stand with Kashmir
  if (id.includes('stand with kashmir')) {
    return {
      role: 'Digital Campaign Wing',
      isPerson: false,
      avatarRing: 'ring-yellow-500 border-2 border-yellow-600',
      avatarBg: 'bg-white',
      svgBadge: (
        <svg viewBox="0 0 100 100" className="w-full h-full">
          <circle cx="50" cy="50" r="46" fill="#f59e0b" />
          <circle cx="50" cy="50" r="38" fill="#ffffff" />
          <text x="50" y="55" textAnchor="middle" fill="#d97706" fontSize="9" fontWeight="900" fontFamily="sans-serif">
            Stand with Kashmir
          </text>
        </svg>
      ),
    };
  }

  // 18. Free Kashmir
  if (id.includes('free kashmir')) {
    return {
      role: 'Digital Front Project',
      isPerson: false,
      avatarRing: 'ring-slate-900 border-2 border-slate-950',
      avatarBg: 'bg-slate-950',
      svgBadge: (
        <svg viewBox="0 0 100 100" className="w-full h-full">
          <circle cx="50" cy="50" r="46" fill="#020617" />
          <text x="50" y="47" textAnchor="middle" fill="#ffffff" fontSize="10" fontWeight="900" fontFamily="sans-serif">
            FREE
          </text>
          <text x="50" y="62" textAnchor="middle" fill="#ffffff" fontSize="9" fontWeight="900" fontFamily="sans-serif">
            KASHMIR
          </text>
        </svg>
      ),
    };
  }

  // 19. Quill / DOTO
  if (id.includes('quill') || id.includes('doto')) {
    return {
      role: 'Documentation Foundation & Database',
      isPerson: false,
      avatarRing: 'ring-red-600 border-2 border-red-700',
      avatarBg: 'bg-red-50',
      svgBadge: (
        <svg viewBox="0 0 100 100" className="w-full h-full">
          <rect x="10" y="10" width="80" height="80" rx="16" fill="#dc2626" />
          <text x="50" y="46" textAnchor="middle" fill="#ffffff" fontSize="13" fontWeight="900" fontFamily="sans-serif">
            QUILL
          </text>
          <text x="50" y="64" textAnchor="middle" fill="#ffffff" fontSize="11" fontWeight="800" fontFamily="sans-serif">
            DOTO
          </text>
        </svg>
      ),
    };
  }

  // 20. Save India
  if (id.includes('save india')) {
    return {
      role: 'Campaign Project / IMAN Net',
      isPerson: false,
      avatarRing: 'ring-orange-500 border-2 border-orange-600',
      avatarBg: 'bg-orange-50',
      svgBadge: (
        <svg viewBox="0 0 100 100" className="w-full h-full">
          <rect x="10" y="15" width="80" height="70" rx="16" fill="#f97316" />
          <text x="50" y="55" textAnchor="middle" fill="#ffffff" fontSize="12" fontWeight="900" fontFamily="sans-serif">
            Save India
          </text>
        </svg>
      ),
    };
  }

  return null;
};

// Extract real avatar image from metadata, properties, or platform conventions
export const extractEntityAvatar = (ent: any): string | null => {
  if (!ent) return null;
  const meta = ent.metadata || {};
  const direct =
    meta.avatar_url ||
    meta.image_url ||
    meta.profile_image ||
    meta.profile_pic ||
    meta.thumbnail_url ||
    meta.avatar ||
    meta.image ||
    meta.userpic ||
    meta.photo_url ||
    ent.avatar_url ||
    ent.image_url ||
    null;

  if (direct && typeof direct === 'string' && direct.trim().length > 0) {
    return direct.trim();
  }

  const val = (ent.value || ent.name || '').trim();
  const platform = (meta.platform || meta.source || (Array.isArray(ent.sources) ? ent.sources.join(' ') : '') || '').toLowerCase();

  // Social handles with @ (e.g. indiaisnextsuperpower@twitter/x or username@twitchinteractive)
  if (val.includes('@')) {
    const parts = val.split('@');
    const handle = parts[0].replace(/^@/, '').trim();
    const domainOrNet = parts[1].toLowerCase().trim();

    if (handle) {
      if (domainOrNet.includes('twitter') || domainOrNet.includes('x.com') || domainOrNet === 'x') {
        return `https://unavatar.io/x/${handle}`;
      }
      if (domainOrNet.includes('youtube')) {
        return `https://unavatar.io/youtube/${handle}`;
      }
      if (domainOrNet.includes('telegram') || domainOrNet === 't.me') {
        return `https://t.me/i/userpic/320/${handle}.jpg`;
      }
      if (domainOrNet.includes('github')) {
        return `https://github.com/${handle}.png`;
      }
      if (domainOrNet.includes('instagram')) {
        return `https://unavatar.io/instagram/${handle}`;
      }
      if (domainOrNet.includes('twitch')) {
        return `https://unavatar.io/twitch/${handle}`;
      }
      if (domainOrNet.includes('reddit')) {
        return `https://unavatar.io/reddit/${handle}`;
      }
      if (domainOrNet.includes('tiktok')) {
        return `https://unavatar.io/tiktok/${handle}`;
      }
      return `https://unavatar.io/${handle}`;
    }
  }

  // Pure username if platform is specified in metadata/sources
  if (ent.type?.toUpperCase() === 'USERNAME' || ent.type?.toUpperCase() === 'PERSON') {
    const clean = val.replace(/^@/, '').trim();
    if (clean) {
      if (platform.includes('twitter') || platform.includes('x.com') || platform === 'x') return `https://unavatar.io/x/${clean}`;
      if (platform.includes('youtube')) return `https://unavatar.io/youtube/${clean}`;
      if (platform.includes('telegram')) return `https://t.me/i/userpic/320/${clean}.jpg`;
      if (platform.includes('github')) return `https://github.com/${clean}.png`;
      if (platform.includes('twitch')) return `https://unavatar.io/twitch/${clean}`;
      if (platform.includes('instagram')) return `https://unavatar.io/instagram/${clean}`;
    }
  }

  return null;
};

// =============================================================================
// INTEL NODE COMPONENT (DisinfoLab Circular Portraits & Emblem Badges)
// =============================================================================
const IntelNode: React.FC<NodeProps> = ({ data, selected }) => {
  const category = getEntityCategory(data.type);
  const Icon = getEntityCategoryIcon(category);
  const confidence = data.confidence || 0.85;
  const isHighRisk = confidence >= 0.88 && ['THREAT_INDICATOR', 'VULNERABILITY'].includes(data.type?.toUpperCase());
  const theme = getNodeTheme(category, isHighRisk);

  const displayName = data.value || data.name || 'Unknown Entity';
  const actorAsset = getDisinfoLabAsset(displayName);
  const avatarUrl = extractEntityAvatar(data);
  const [imageError, setImageError] = useState(false);

  const roleText = actorAsset?.role || data.metadata?.role || data.metadata?.title || data.metadata?.category || data.sources?.[0] || '';

  return (
    <div
      className={`px-3 py-3 rounded-2xl border-2 shadow-lg transition-all font-sans min-w-[210px] max-w-[250px] select-none text-center ${theme.bg} ${theme.border} ${
        selected
          ? 'ring-4 ring-indigo-500/50 dark:ring-indigo-400/50 shadow-xl scale-105'
          : 'hover:shadow-xl hover:border-indigo-400 dark:hover:border-indigo-500'
      }`}
    >
      {/* 4 Multi-directional handles */}
      <Handle type="target" position={Position.Top} className="!w-2.5 !h-2.5 !bg-indigo-500 !border-2 !border-white dark:!border-slate-900" />
      <Handle type="target" position={Position.Left} id="left" className="!w-2 !h-2 !bg-indigo-400 !border-white dark:!border-slate-900" />

      {/* Prominent Circular Avatar Portrait or Emblem Logo */}
      <div className="relative mx-auto my-1 flex justify-center items-center">
        <div
          className={`w-14 h-14 rounded-full overflow-hidden shadow-md flex items-center justify-center ring-3 ${
            actorAsset?.avatarRing || theme.ring
          } ${actorAsset?.avatarBg || 'bg-slate-100 dark:bg-slate-800'}`}
        >
          {actorAsset?.svgBadge ? (
            actorAsset.svgBadge
          ) : avatarUrl && !imageError ? (
            <img
              src={avatarUrl}
              alt={displayName}
              className="w-full h-full object-cover"
              onError={() => setImageError(true)}
              loading="lazy"
            />
          ) : (
            <div className="flex flex-col items-center justify-center text-slate-700 dark:text-slate-200">
              <Icon className="w-6 h-6 mb-0.5" />
              <span className="text-[9px] font-mono font-black uppercase">
                {displayName.slice(0, 2).toUpperCase()}
              </span>
            </div>
          )}
        </div>

        {/* Confidence Badge */}
        <span
          className={`absolute -bottom-1 -right-1 text-[9px] font-mono font-extrabold px-1.5 py-0.5 rounded-full shadow-xs ${theme.badge}`}
        >
          {Math.round(confidence * 100)}%
        </span>
      </div>

      {/* Actor / Entity Name */}
      <h4
        className="text-xs font-black text-slate-900 dark:text-white leading-tight mt-1.5 break-words line-clamp-2"
        title={displayName}
      >
        {displayName}
      </h4>

      {/* Prominent Role Subtitle Badge */}
      {roleText && (
        <div className="mt-1.5 px-2 py-0.5 rounded-md bg-slate-200/80 dark:bg-slate-800 text-[10px] font-mono font-bold text-slate-800 dark:text-slate-200 line-clamp-2 leading-tight">
          {roleText}
        </div>
      )}

      {/* Footer Category Tag */}
      <div className="flex items-center justify-between mt-2 pt-1 border-t border-slate-200/60 dark:border-slate-800 text-[9px] font-mono text-slate-500">
        <span className="font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400">
          {actorAsset?.isPerson ? 'PERSON' : category}
        </span>
        {data.sources && (
          <span className="text-slate-400">{data.sources.length} sources</span>
        )}
      </div>

      <Handle type="source" position={Position.Bottom} className="!w-2.5 !h-2.5 !bg-indigo-500 !border-2 !border-white dark:!border-slate-900" />
      <Handle type="source" position={Position.Right} id="right" className="!w-2 !h-2 !bg-indigo-400 !border-white dark:!border-slate-900" />
    </div>
  );
};

const nodeTypes = {
  intelNode: IntelNode,
};

// Exact Coordinates matching DisinfoLab Reference Graphic
const DISINFOLAB_COORDINATES: Record<string, { x: number; y: number }> = {
  'globally designated terror groups': { x: 50, y: 40 },
  'helping hand for relief and development': { x: 440, y: 40 },
  'icna': { x: 800, y: 30 },
  'i.s.i.': { x: 1140, y: 30 },

  'burma task force': { x: 440, y: 220 },
  'shaik ubaid': { x: 640, y: 250 },
  'abdul malik mujahid': { x: 880, y: 250 },

  'ajit sahi': { x: 60, y: 350 },
  'iamc': { x: 260, y: 350 },
  'ahmadullah siddiqi': { x: 640, y: 440 },
  'justice for all': { x: 880, y: 480 },

  'cag': { x: 60, y: 560 },
  'quill foundation / doto database': { x: 260, y: 540 },
  'simi': { x: 640, y: 620 },
  'sound vision': { x: 880, y: 670 },

  'harsh mander': { x: 260, y: 720 },
  'save india': { x: 470, y: 730 },
  'stand with kashmir': { x: 680, y: 780 },
  'free kashmir / kashmir action': { x: 880, y: 830 },
  'ghulam nabi fai': { x: 1080, y: 780 },
};

export const GraphStudioComponent: React.FC<Props> = ({
  investigationId,
  entities = [],
  relationships = [],
  onRunSearch,
  isSearching,
}) => {
  const [filterCategory, setFilterCategory] = useState<string>('ALL');
  const [maxNodes, setMaxNodes] = useState<number>(35);
  const [layoutMode, setLayoutMode] = useState<LayoutMode>('INVESTIGATION_TIERS');
  const [searchFilter, setSearchFilter] = useState<string>('');
  const [selectedEntity, setSelectedEntity] = useState<Entity | null>(entities[0] || null);

  // 1. Filter entities by category, search text, and limit
  const filteredEntities = useMemo(() => {
    let list = entities;

    if (filterCategory !== 'ALL') {
      list = list.filter((e) => getEntityCategory(e.type) === filterCategory);
    }

    if (searchFilter.trim()) {
      const q = searchFilter.toLowerCase();
      list = list.filter((e) =>
        (e.value || (e as any).name || '').toLowerCase().includes(q) ||
        (e.type || '').toLowerCase().includes(q)
      );
    }

    return list.slice(0, maxNodes);
  }, [entities, filterCategory, searchFilter, maxNodes]);

  // 2. DisinfoLab-style layout algorithm (Guaranteed spacious and non-overlapping)
  const initialNodes: Node[] = useMemo(() => {
    if (filteredEntities.length === 0) return [];

    const nodesResult: Node[] = [];

    // Check if entities match DisinfoLab Kashmir dataset
    const isDisinfoLabNetwork = filteredEntities.some((e) => {
      const val = (e.value || (e as any).name || '').toLowerCase();
      return ['abdul malik mujahid', 'shaik ubaid', 'icna', 'iamc', 'simi', 'sound vision', 'ghulam nabi fai'].includes(val);
    });

    if (isDisinfoLabNetwork && layoutMode === 'INVESTIGATION_TIERS') {
      filteredEntities.forEach((ent, idx) => {
        const val = (ent.value || (ent as any).name || '').toLowerCase().trim();
        const fixedPos = DISINFOLAB_COORDINATES[val];
        const entId = ent.id || `node-${val}`;

        if (fixedPos) {
          nodesResult.push({
            id: entId,
            type: 'intelNode',
            position: { x: fixedPos.x, y: fixedPos.y },
            data: ent,
          });
        } else {
          // Extra nodes placed nicely below
          nodesResult.push({
            id: entId,
            type: 'intelNode',
            position: { x: 100 + (idx % 4) * 320, y: 950 + Math.floor(idx / 4) * 220 },
            data: ent,
          });
        }
      });
      return nodesResult;
    }

    if (layoutMode === 'INVESTIGATION_TIERS') {
      const tiers: Record<number, Entity[]> = { 1: [], 2: [], 3: [], 4: [], 5: [] };

      filteredEntities.forEach((ent, idx) => {
        const cat = getEntityCategory(ent.type);
        if (idx === 0) {
          tiers[1].push(ent);
        } else if (cat === 'ORGANIZATION') {
          tiers[1].push(ent);
        } else if (cat === 'PERSON') {
          tiers[2].push(ent);
        } else if (cat === 'THREAT_INDICATOR') {
          tiers[3].push(ent);
        } else if (cat === 'IP') {
          tiers[4].push(ent);
        } else {
          tiers[5].push(ent);
        }
      });

      const tierYOffsets: Record<number, number> = {
        1: 60,
        2: 280,
        3: 500,
        4: 720,
        5: 940,
      };

      const nodeCardWidth = 320; // 320px width per card eliminates crowding

      Object.entries(tiers).forEach(([tStr, tierList]) => {
        const tNum = Number(tStr);
        const yBase = tierYOffsets[tNum];
        const count = tierList.length;
        if (count === 0) return;

        const maxPerRow = 4;
        tierList.forEach((ent, i) => {
          const rowIdx = Math.floor(i / maxPerRow);
          const colIdx = i % maxPerRow;
          const itemsInThisRow = Math.min(maxPerRow, count - rowIdx * maxPerRow);

          const startX = 640 - (itemsInThisRow * nodeCardWidth) / 2;
          const x = startX + colIdx * nodeCardWidth;
          const y = yBase + rowIdx * 160;

          const entId = ent.id || `node-${ent.value || (ent as any).name}`;
          nodesResult.push({
            id: entId,
            type: 'intelNode',
            position: { x, y },
            data: ent,
          });
        });
      });
    } else if (layoutMode === 'SPACED_RADIAL') {
      const centerX = 640;
      const centerY = 480;

      filteredEntities.forEach((ent, idx) => {
        const entId = ent.id || `node-${idx}-${ent.value || (ent as any).name}`;
        if (idx === 0) {
          nodesResult.push({
            id: entId,
            type: 'intelNode',
            position: { x: centerX - 110, y: centerY - 60 },
            data: ent,
          });
          return;
        }

        const ringIndex = Math.floor((idx - 1) / 7);
        const indexInRing = (idx - 1) % 7;
        const ringCount = Math.min(7, filteredEntities.length - 1 - ringIndex * 7);

        const radius = 340 + ringIndex * 280;
        const angle = (indexInRing / Math.max(1, ringCount)) * 2 * Math.PI;

        const x = centerX + Math.cos(angle) * radius - 110;
        const y = centerY + Math.sin(angle) * radius - 60;

        nodesResult.push({
          id: entId,
          type: 'intelNode',
          position: { x, y },
          data: ent,
        });
      });
    } else {
      // GRID_COLUMNS
      const colXMap: Record<string, number> = {
        ORGANIZATION: 80,
        PERSON: 420,
        THREAT_INDICATOR: 760,
        IP: 1100,
        DOMAIN: 1440,
        DOCUMENT: 1780,
      };

      const categoryYMap: Record<string, number> = {};

      filteredEntities.forEach((ent, idx) => {
        const cat = getEntityCategory(ent.type);
        const colX = colXMap[cat] || 80;
        const curY = categoryYMap[cat] || 60;
        categoryYMap[cat] = curY + 160;

        const entId = ent.id || `node-${idx}-${ent.value || (ent as any).name}`;
        nodesResult.push({
          id: entId,
          type: 'intelNode',
          position: { x: colX, y: curY },
          data: ent,
        });
      });
    }

    return nodesResult;
  }, [filteredEntities, layoutMode]);

  // 3. Generate clear directed edges with labeled pills (DisinfoLab standard)
  const initialEdges: Edge[] = useMemo(() => {
    if (filteredEntities.length <= 1) return [];

    const entityValueMap = new Map<string, string>();
    filteredEntities.forEach((ent) => {
      const entId = ent.id || `node-${(ent.value || (ent as any).name || '').toLowerCase().trim()}`;
      if (ent.value) entityValueMap.set(ent.value.toLowerCase().trim(), entId);
      if ((ent as any).name) entityValueMap.set((ent as any).name.toLowerCase().trim(), entId);
      if (ent.id) entityValueMap.set(ent.id.toLowerCase().trim(), entId);
    });

    const edgesResult: Edge[] = [];
    const seenEdges = new Set<string>();

    const getEdgeStyle = (relType: string) => {
      const rt = (relType || '').toUpperCase();
      if (['FOUNDER', 'CHAIR', 'PRESIDENT', 'DIRECTOR', 'LEADERSHIP', 'MEMBER', 'CO_FOUNDER', 'ADVOCACY_DIRECTOR'].includes(rt)) {
        return { stroke: '#059669', color: '#059669', labelBg: '#ecfdf5', labelStroke: '#34d399' };
      }
      if (['OWNS', 'AFFILIATED_WITH', 'ASSOCIATED_WITH', 'SISTER_NGO', 'PARTNER'].includes(rt)) {
        return { stroke: '#2563eb', color: '#2563eb', labelBg: '#eff6ff', labelStroke: '#60a5fa' };
      }
      if (['FUNDING', 'SPONSORS', 'USES', 'POWERED_BY', 'EVENTS_AND_SEMINARS', 'PROJECT', 'PROJECT_OF', 'WORKS_WITH'].includes(rt)) {
        return { stroke: '#d97706', color: '#d97706', labelBg: '#fffbeb', labelStroke: '#fbbf24' };
      }
      if (['EXPOSED_BY', 'THREAT', 'ATTRIBUTED_TO', 'MALICIOUS', 'CONVICTED'].includes(rt)) {
        return { stroke: '#dc2626', color: '#dc2626', labelBg: '#fef2f2', labelStroke: '#f87171' };
      }
      if (['NEXUS', 'SEMINAR_CIRCUIT', 'RESOLVES_TO', 'HOSTED_ON'].includes(rt)) {
        return { stroke: '#7c3aed', color: '#7c3aed', labelBg: '#f5f3ff', labelStroke: '#a78bfa' };
      }
      return { stroke: '#64748b', color: '#64748b', labelBg: '#f8fafc', labelStroke: '#94a3b8' };
    };

    if (relationships && relationships.length > 0) {
      relationships.forEach((rel, rIdx) => {
        const srcVal = (rel.source_entity_value || '').toLowerCase().trim();
        const tgtVal = (rel.target_entity_value || '').toLowerCase().trim();
        const srcId = entityValueMap.get(srcVal);
        const tgtId = entityValueMap.get(tgtVal);

        if (srcId && tgtId && srcId !== tgtId) {
          const edgeKey = `${srcId}-${tgtId}`;
          if (!seenEdges.has(edgeKey)) {
            seenEdges.add(edgeKey);
            const style = getEdgeStyle(rel.relationship_type);
            const labelText = rel.metadata?.role || rel.relationship_type.replace(/_/g, ' ');

            edgesResult.push({
              id: `edge-${rIdx}-${srcId}-${tgtId}`,
              source: srcId,
              target: tgtId,
              label: labelText,
              type: 'smoothstep',
              markerEnd: {
                type: MarkerType.ArrowClosed,
                width: 15,
                height: 15,
                color: style.color,
              },
              style: {
                stroke: style.stroke,
                strokeWidth: 2.2,
              },
              labelStyle: {
                fill: '#0f172a',
                fontWeight: 800,
                fontSize: 10,
                fontFamily: 'monospace',
              },
              labelBgStyle: {
                fill: style.labelBg,
                stroke: style.labelStroke,
                strokeWidth: 1.5,
                rx: 6,
                ry: 6,
              },
              labelBgPadding: [6, 3],
            });
          }
        }
      });
    }

    if (edgesResult.length === 0 && initialNodes.length > 1) {
      const rootId = initialNodes[0].id;
      initialNodes.slice(1).forEach((node) => {
        const targetId = node.id;
        const cat = getEntityCategory(node.data?.type);
        const relLabel =
          cat === 'PERSON'
            ? 'KEY ACTOR'
            : cat === 'ORGANIZATION'
            ? 'AFFILIATED ORG'
            : cat === 'THREAT_INDICATOR'
            ? 'INDICATOR'
            : 'CORRELATED';

        const style = getEdgeStyle(relLabel);

        edgesResult.push({
          id: `e-synth-${rootId}-${targetId}`,
          source: rootId,
          target: targetId,
          label: relLabel,
          type: 'smoothstep',
          markerEnd: {
            type: MarkerType.ArrowClosed,
            width: 14,
            height: 14,
            color: style.color,
          },
          style: {
            stroke: style.stroke,
            strokeWidth: 1.8,
          },
          labelStyle: {
            fill: '#0f172a',
            fontWeight: 800,
            fontSize: 9,
            fontFamily: 'monospace',
          },
          labelBgStyle: {
            fill: style.labelBg,
            stroke: style.labelStroke,
            strokeWidth: 1,
            rx: 6,
            ry: 6,
          },
          labelBgPadding: [5, 2],
        });
      });
    }

    return edgesResult;
  }, [filteredEntities, relationships, initialNodes]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  React.useEffect(() => {
    setNodes(initialNodes);
    setEdges(initialEdges);
    if (!selectedEntity && filteredEntities.length > 0) {
      setSelectedEntity(filteredEntities[0]);
    }
  }, [initialNodes, initialEdges, filteredEntities]);

  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      const found = entities.find(
        (e) => (e.id || `node-${(e.value || (e as any).name || '').toLowerCase().trim()}`) === node.id || e.value === node.data?.value
      );
      if (found) {
        setSelectedEntity(found);
      }
    },
    [entities]
  );

  if (entities.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-slate-300 dark:border-slate-800 bg-white dark:bg-slate-900/40 p-12 text-center space-y-4">
        <div className="w-14 h-14 rounded-full bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 flex items-center justify-center mx-auto text-slate-500">
          <Network className="w-7 h-7" />
        </div>
        <div className="space-y-1.5 max-w-md mx-auto">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider font-mono">
            No Entity Relationships Discovered
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed font-sans">
            There are no correlated graph entities or relationship links mapped for this investigation yet. Execute an intelligence search to automatically populate the relationship topology.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Investigative Topology Header & Filter Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-3.5 rounded-xl border border-slate-200 bg-white shadow-2xs dark:border-slate-800 dark:bg-[#0f1422] text-xs">
        <div className="flex flex-wrap items-center gap-2.5">
          <div className="flex items-center gap-1 bg-slate-100 dark:bg-slate-800 p-1 rounded-lg">
            <button
              type="button"
              onClick={() => setLayoutMode('INVESTIGATION_TIERS')}
              className={`px-2.5 py-1 rounded-md text-[11px] font-mono font-bold transition-colors ${
                layoutMode === 'INVESTIGATION_TIERS'
                  ? 'bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-xs'
                  : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
              }`}
              title="DisinfoLab Hierarchical Investigation Network"
            >
              🏛️ Investigative Tiers
            </button>
            <button
              type="button"
              onClick={() => setLayoutMode('SPACED_RADIAL')}
              className={`px-2.5 py-1 rounded-md text-[11px] font-mono font-bold transition-colors ${
                layoutMode === 'SPACED_RADIAL'
                  ? 'bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-xs'
                  : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
              }`}
              title="Spaced Multi-Ring Concentric Layout"
            >
              ⭕ Spaced Radial
            </button>
            <button
              type="button"
              onClick={() => setLayoutMode('GRID_COLUMNS')}
              className={`px-2.5 py-1 rounded-md text-[11px] font-mono font-bold transition-colors ${
                layoutMode === 'GRID_COLUMNS'
                  ? 'bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-xs'
                  : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
              }`}
              title="Category Columns Layout"
            >
              📊 Category Columns
            </button>
          </div>

          <div className="flex items-center gap-1.5">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="h-8 px-2.5 rounded-lg bg-white border border-slate-200 text-xs text-slate-800 font-mono focus:border-indigo-500 dark:bg-slate-900 dark:border-slate-800 dark:text-slate-200"
            >
              <option value="ALL">All Categories ({entities.length})</option>
              <option value="ORGANIZATION">Organizations & Groups</option>
              <option value="PERSON">Key Persons & Actors</option>
              <option value="THREAT_INDICATOR">Threat Indicators & IOCs</option>
              <option value="DOMAIN">Domains & URLs</option>
              <option value="IP">IP & Infrastructure</option>
            </select>
          </div>

          <div className="flex items-center gap-1.5">
            <span className="text-[11px] font-mono text-slate-400">Density:</span>
            <select
              value={maxNodes}
              onChange={(e) => setMaxNodes(Number(e.target.value))}
              className="h-8 px-2 rounded-lg bg-white border border-slate-200 text-xs text-slate-800 font-mono focus:border-indigo-500 dark:bg-slate-900 dark:border-slate-800 dark:text-slate-200"
            >
              <option value={20}>Top 20 (Clean)</option>
              <option value={35}>Top 35 (Balanced)</option>
              <option value={70}>All (Extended)</option>
            </select>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Find entity..."
              value={searchFilter}
              onChange={(e) => setSearchFilter(e.target.value)}
              className="h-8 pl-8 pr-2.5 rounded-lg bg-white border border-slate-200 text-xs font-mono text-slate-800 focus:outline-none dark:bg-slate-900 dark:border-slate-800 dark:text-slate-200"
            />
          </div>
          <Badge variant="mono" size="sm">
            {initialNodes.length} Visible Nodes
          </Badge>
          <Badge variant="accent" size="sm">
            {initialEdges.length} Links
          </Badge>
        </div>
      </div>

      {/* Main Flow Canvas & Telemetry Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* ReactFlow Interactive Canvas */}
        <div className="lg:col-span-3 h-[680px] rounded-2xl border border-slate-200 bg-slate-50/60 dark:border-slate-800 dark:bg-[#090d16] relative overflow-hidden shadow-inner">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={onNodeClick}
            nodeTypes={nodeTypes}
            fitView
            minZoom={0.2}
            maxZoom={1.8}
            defaultEdgeOptions={{
              type: 'smoothstep',
            }}
          >
            <Background gap={24} size={1.2} color="#94a3b8" className="opacity-25" />
            <Controls className="!bg-white dark:!bg-slate-900 !border !border-slate-200 dark:!border-slate-800 !rounded-xl !shadow-sm" />
            <MiniMap
              className="!bg-white dark:!bg-slate-900 !border !border-slate-200 dark:!border-slate-800 !rounded-xl !shadow-sm"
              nodeColor={(n) => {
                const cat = getEntityCategory(n.data?.type);
                if (cat === 'ORGANIZATION') return '#6366f1';
                if (cat === 'PERSON') return '#f59e0b';
                if (cat === 'THREAT_INDICATOR') return '#f43f5e';
                if (cat === 'IP') return '#3b82f6';
                return '#64748b';
              }}
            />
          </ReactFlow>

          {/* Overlay Legend */}
          <div className="absolute bottom-3 left-3 bg-white/90 dark:bg-slate-900/90 backdrop-blur-xs p-2 rounded-lg border border-slate-200 dark:border-slate-800 text-[10px] font-mono flex items-center gap-3 shadow-sm select-none">
            <div className="flex items-center gap-1">
              <span className="w-2.5 h-2.5 rounded-full bg-indigo-500 inline-block" />
              <span>Org</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-500 inline-block" />
              <span>Person</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-500 inline-block" />
              <span>Threat/IOC</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="w-2.5 h-2.5 rounded-full bg-blue-500 inline-block" />
              <span>IP Node</span>
            </div>
          </div>
        </div>

        {/* Node Inspector Panel */}
        <div className="rounded-xl border border-slate-200 bg-white p-4 space-y-4 shadow-2xs dark:border-slate-800 dark:bg-[#0f1422]">
          <div className="flex items-center gap-2 pb-2.5 border-b border-slate-200 dark:border-slate-800">
            <Info className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
            <h3 className="text-xs font-mono font-bold text-slate-900 dark:text-white uppercase tracking-wider">
              Entity Telemetry Inspector
            </h3>
          </div>

          {selectedEntity ? (() => {
            const avatarUrl = extractEntityAvatar(selectedEntity);
            const profileUrl = (selectedEntity.metadata?.profile_url as string) || (selectedEntity.metadata?.url as string) || (selectedEntity.value?.startsWith('http') ? selectedEntity.value : null);
            const platform = (selectedEntity.metadata?.platform as string) || (selectedEntity.metadata?.category as string) || selectedEntity.sources?.[0] || 'Identity Target';
            const handleClean = selectedEntity.value?.includes('@') ? selectedEntity.value.split('@')[0] : selectedEntity.value;

            return (
              <div className="space-y-3.5 text-xs">
                {/* Profile Card Preview */}
                {(avatarUrl || profileUrl) && (
                  <div className="p-3 rounded-xl border border-slate-200/90 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-900/60 space-y-3 shadow-2xs">
                    <div className="flex items-center gap-3">
                      {avatarUrl ? (
                        <div className="relative shrink-0">
                          <img
                            src={avatarUrl}
                            alt={selectedEntity.value}
                            className="w-14 h-14 rounded-xl object-cover border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 shadow-xs"
                            onError={(e) => {
                              (e.target as any).src = `https://api.dicebear.com/7.x/identicon/svg?seed=${encodeURIComponent(selectedEntity.value)}`;
                            }}
                          />
                          <span className="absolute -bottom-1 -right-1 w-3.5 h-3.5 bg-emerald-500 border-2 border-white dark:border-slate-900 rounded-full" title="Active Presence" />
                        </div>
                      ) : (
                        <div className="w-14 h-14 rounded-xl bg-indigo-50 border border-indigo-200 text-indigo-600 flex items-center justify-center font-bold text-base font-mono dark:bg-indigo-950 dark:border-indigo-800 dark:text-indigo-400 shrink-0">
                          {handleClean?.slice(0, 2).toUpperCase()}
                        </div>
                      )}
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center justify-between gap-1">
                          <span className="font-bold text-sm text-slate-900 dark:text-white truncate font-sans">
                            {handleClean}
                          </span>
                          <Badge variant="mono" size="sm" className="text-[10px] shrink-0 uppercase">
                            {platform}
                          </Badge>
                        </div>
                        <p className="text-[11px] text-slate-500 dark:text-slate-400 truncate mt-0.5 font-mono">
                          {selectedEntity.value}
                        </p>
                      </div>
                    </div>

                    {profileUrl && (
                      <a
                        href={profileUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center justify-center gap-1.5 w-full py-2 px-3 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold font-mono transition-colors shadow-xs"
                      >
                        <span>Visit Public Profile</span>
                        <ExternalLink className="w-3.5 h-3.5" />
                      </a>
                    )}
                  </div>
                )}

                <div>
                  <span className="text-slate-400 uppercase text-[10px] block font-mono">Entity Identifier</span>
                  <p className="font-bold text-slate-900 dark:text-white break-all mt-0.5 text-sm font-sans">
                    {selectedEntity.value || (selectedEntity as any).name}
                  </p>
                </div>

              <div className="flex items-center justify-between">
                <span className="text-slate-500 font-mono text-xs">Classification</span>
                <Badge variant="outline" className="font-mono text-[10px] uppercase">
                  {selectedEntity.type}
                </Badge>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-slate-500 font-mono text-xs">Analytic Confidence</span>
                <Badge variant={(selectedEntity.confidence || 0) >= 0.85 ? 'success' : 'warning'} className="font-mono text-[10px]">
                  {Math.round((selectedEntity.confidence || 0.85) * 100)}%
                </Badge>
              </div>

              {selectedEntity.sources && selectedEntity.sources.length > 0 && (
                <div>
                  <span className="text-slate-400 uppercase text-[10px] block font-mono mb-1">Correlated Sources</span>
                  <div className="flex flex-wrap gap-1">
                    {selectedEntity.sources.map((src, i) => (
                      <span
                        key={i}
                        className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700"
                      >
                        {src}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {selectedEntity.metadata && Object.keys(selectedEntity.metadata).length > 0 && (
                <div className="space-y-1.5 pt-2 border-t border-slate-100 dark:border-slate-800">
                  <span className="text-slate-400 uppercase text-[10px] block font-mono">Telemetry Metadata</span>
                  <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200 space-y-1.5 font-mono text-[11px] dark:bg-slate-950 dark:border-slate-800 max-h-56 overflow-y-auto">
                    {Object.entries(selectedEntity.metadata).map(([k, v]) => (
                      <div key={k} className="flex justify-between gap-2 border-b border-slate-100 dark:border-slate-900 pb-1 last:border-0 last:pb-0">
                        <span className="text-slate-500 shrink-0">{k}:</span>
                        <span className="text-slate-800 dark:text-slate-200 font-bold truncate text-right">
                          {typeof v === 'object' ? JSON.stringify(v) : String(v)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })() : (
            <p className="text-xs text-slate-500 font-mono">Click a graph node to inspect telemetry.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default GraphStudioComponent;

import React, { useState, useEffect, useRef, useMemo } from 'react';
import cytoscape, { Core, EventObject } from 'cytoscape';
import { Entity, Relationship } from '../../types';
import { Badge } from '../../components/ui/Badge';
import { apiRequest } from '../../core/api/client';
import {
  Info,
  Filter,
  Network,
  Search,
  Maximize2,
  Minimize2,
  Loader2,
  Link2,
  Focus,
  GitFork,
  Radio,
  Eye,
  EyeOff,
  Compass,
  Download,
  Route,
  Sparkles,
  ZoomIn,
  ZoomOut,
  Sun,
  Moon,
  Plus,
  Layers,
  ChevronDown,
  ChevronUp,
  Activity,
  ShieldAlert,
  Globe,
  User,
  Building2,
  FileText,
  Pin,
  ExternalLink,
} from 'lucide-react';

interface Props {
  investigationId?: string;
  entities: Entity[];
  relationships?: Relationship[];
  onRunSearch?: () => void;
  isSearching?: boolean;
}

export type LayoutName = 'cose' | 'concentric' | 'breadthfirst' | 'circle';

export interface HoverTooltipData {
  type: 'node' | 'edge';
  title: string;
  category?: string;
  entityType?: string;
  degree?: number;
  provenance?: string;
  confidence?: number;
  sourceLabel?: string;
  targetLabel?: string;
  x: number;
  y: number;
}

import { getEntityCategory, extractEntityAvatar } from './categoryUtils';
export { getEntityCategory, extractEntityAvatar };

// Generates crisp, clean SVG icons to render directly inside circular graph nodes
const getCategorySvgIcon = (category: string, color: string = '#ffffff'): string => {
  let content = '';
  switch (category) {
    case 'PHONE':
      content = `<path d="M12 7h6l2.5 5.5-3.5 2.5c2.3 4.6 6 8.3 10.6 10.6l2.5-3.5 5.5 2.5v6c0 1.7-1.3 3-3 3C18 36 12 30 7 15c-0.1-1.7 1.3-3 3-3z" stroke="${color}" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`;
      break;
    case 'EMAIL':
      content = `<rect x="6" y="10" width="36" height="26" rx="4" stroke="${color}" stroke-width="3" fill="none"/><path d="M7 13l17 12 17-12" stroke="${color}" stroke-width="3" stroke-linecap="round" fill="none"/>`;
      break;
    case 'VEHICLE':
      content = `<path d="M7 26l3-9a3 3 0 0 1 2.8-2h22.4a3 3 0 0 1 2.8 2l3 9M5 26h38a3 3 0 0 1 3 3v7a2 2 0 0 1-2 2h-3a4 4 0 0 1-8 0H14a4 4 0 0 1-8 0H4a2 2 0 0 1-2-2v-7a3 3 0 0 1 3-3z" stroke="${color}" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/><circle cx="10" cy="38" r="2.5" fill="${color}"/><circle cx="38" cy="38" r="2.5" fill="${color}"/><line x1="14" y1="21" x2="34" y2="21" stroke="${color}" stroke-width="2"/>`;
      break;
    case 'LOCATION':
      content = `<path d="M24 6c-6.627 0-12 5.373-12 12 0 9 12 24 12 24s12-15 12-24c0-6.627-5.373-12-12-12z" stroke="${color}" stroke-width="2.8" fill="none"/><circle cx="24" cy="18" r="4" fill="${color}"/>`;
      break;
    case 'PERSON':
      content = `<circle cx="24" cy="15" r="7.5" fill="${color}"/><path d="M9 37c0-8.284 6.716-15 15-15s15 6.716 15 15" fill="${color}"/>`;
      break;
    case 'ORGANIZATION':
      content = `<path d="M8 40V12a2 2 0 0 1 2-2h12v30M22 18h14a2 2 0 0 1 2 2v20M6 40h36" stroke="${color}" stroke-width="3" stroke-linecap="round" fill="none"/><line x1="14" y1="18" x2="16" y2="18" stroke="${color}" stroke-width="3"/><line x1="14" y1="26" x2="16" y2="26" stroke="${color}" stroke-width="3"/><line x1="14" y1="34" x2="16" y2="34" stroke="${color}" stroke-width="3"/><line x1="30" y1="26" x2="32" y2="26" stroke="${color}" stroke-width="3"/><line x1="30" y1="34" x2="32" y2="34" stroke="${color}" stroke-width="3"/>`;
      break;
    case 'THREAT_INDICATOR':
      content = `<path d="M24 6l14 5v12c0 9-14 19-14 19S10 32 10 23V11l14-5z" fill="${color}" opacity="0.35" stroke="${color}" stroke-width="3" stroke-linejoin="round"/><line x1="24" y1="16" x2="24" y2="26" stroke="${color}" stroke-width="3.5" stroke-linecap="round"/><circle cx="24" cy="32" r="2.2" fill="${color}"/>`;
      break;
    case 'IP':
      content = `<rect x="6" y="8" width="36" height="12" rx="3" stroke="${color}" stroke-width="3" fill="none"/><rect x="6" y="26" width="36" height="12" rx="3" stroke="${color}" stroke-width="3" fill="none"/><circle cx="13" cy="14" r="2.5" fill="${color}"/><circle cx="13" cy="32" r="2.5" fill="${color}"/><line x1="24" y1="14" x2="35" y2="14" stroke="${color}" stroke-width="2.5"/><line x1="24" y1="32" x2="35" y2="32" stroke="${color}" stroke-width="2.5"/>`;
      break;
    case 'VIDEO':
      content = `<rect x="6" y="9" width="36" height="30" rx="6" stroke="${color}" stroke-width="3" fill="none"/><polygon points="20,17 32,24 20,31" fill="${color}"/>`;
      break;
    case 'POST':
      content = `<path d="M8 10h32a3 3 0 0 1 3 3v18a3 3 0 0 1-3 3H16l-8 7V13a3 3 0 0 1 3-3z" stroke="${color}" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`;
      break;
    case 'IMAGE':
      content = `<rect x="6" y="8" width="36" height="32" rx="4" stroke="${color}" stroke-width="2.5" fill="none"/><circle cx="16" cy="18" r="4" fill="${color}"/><path d="M42 30l-10-10L10 40h32v-10z" fill="${color}" opacity="0.7"/>`;
      break;
    case 'ARTICLE':
    case 'DOCUMENT':
      content = `<path d="M10 6h28a2 2 0 0 1 2 2v32a2 2 0 0 1-2 2H10a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2z" stroke="${color}" stroke-width="2.5" fill="none"/><line x1="15" y1="14" x2="33" y2="14" stroke="${color}" stroke-width="2.5" stroke-linecap="round"/><line x1="15" y1="22" x2="33" y2="22" stroke="${color}" stroke-width="2.5" stroke-linecap="round"/><line x1="15" y1="30" x2="25" y2="30" stroke="${color}" stroke-width="2.5" stroke-linecap="round"/>`;
      break;
    case 'EVIDENCE':
      content = `<path d="M24 5l16 6v14c0 10-16 18-16 18S8 35 8 25V11l16-6z" stroke="${color}" stroke-width="2.5" fill="none"/><path d="M17 24l5 5 10-10" stroke="${color}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>`;
      break;
    case 'KEYWORD':
      content = `<line x1="10" y1="18" x2="38" y2="18" stroke="${color}" stroke-width="2.5"/><line x1="10" y1="30" x2="38" y2="30" stroke="${color}" stroke-width="2.5"/><line x1="18" y1="10" x2="14" y2="38" stroke="${color}" stroke-width="2.5"/><line x1="30" y1="10" x2="26" y2="38" stroke="${color}" stroke-width="2.5"/>`;
      break;
    case 'DOMAIN':
      content = `<circle cx="24" cy="24" r="17" stroke="${color}" stroke-width="3" fill="none"/><ellipse cx="24" cy="24" rx="7.5" ry="17" stroke="${color}" stroke-width="2.5" fill="none"/><line x1="7" y1="24" x2="41" y2="24" stroke="${color}" stroke-width="2.5"/>`;
      break;
    case 'UNKNOWN':
    default:
      content = `<circle cx="24" cy="24" r="16" stroke="${color}" stroke-width="2.5" stroke-dasharray="4 3" fill="none"/><circle cx="24" cy="24" r="5" fill="${color}"/>`;
      break;
  }
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">${content}</svg>`;
  return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`;
};

const CATEGORY_COLORS: Record<string, { bg: string; border: string; glow: string; text: string }> = {
  PHONE: { bg: '#0284c7', border: '#0369a1', glow: 'rgba(2, 132, 199, 0.4)', text: '#ffffff' },
  EMAIL: { bg: '#0d9488', border: '#0f766e', glow: 'rgba(13, 148, 136, 0.4)', text: '#ffffff' },
  PERSON: { bg: '#f59e0b', border: '#d97706', glow: 'rgba(245, 158, 11, 0.4)', text: '#ffffff' },
  ORGANIZATION: { bg: '#6366f1', border: '#4f46e5', glow: 'rgba(99, 102, 241, 0.4)', text: '#ffffff' },
  VEHICLE: { bg: '#8b5cf6', border: '#7c3aed', glow: 'rgba(139, 92, 246, 0.4)', text: '#ffffff' },
  DOMAIN: { bg: '#64748b', border: '#475569', glow: 'rgba(100, 116, 139, 0.4)', text: '#ffffff' },
  IP: { bg: '#2563eb', border: '#1d4ed8', glow: 'rgba(37, 99, 235, 0.4)', text: '#ffffff' },
  LOCATION: { bg: '#06b6d4', border: '#0891b2', glow: 'rgba(6, 182, 212, 0.4)', text: '#ffffff' },
  ARTICLE: { bg: '#10b981', border: '#059669', glow: 'rgba(16, 185, 129, 0.4)', text: '#ffffff' },
  DOCUMENT: { bg: '#10b981', border: '#059669', glow: 'rgba(16, 185, 129, 0.4)', text: '#ffffff' },
  VIDEO: { bg: '#ef4444', border: '#dc2626', glow: 'rgba(239, 68, 68, 0.4)', text: '#ffffff' },
  IMAGE: { bg: '#ec4899', border: '#db2777', glow: 'rgba(236, 72, 153, 0.4)', text: '#ffffff' },
  POST: { bg: '#84cc16', border: '#65a30d', glow: 'rgba(132, 204, 22, 0.4)', text: '#ffffff' },
  EVIDENCE: { bg: '#14b8a6', border: '#0d9488', glow: 'rgba(20, 184, 166, 0.4)', text: '#ffffff' },
  THREAT_INDICATOR: { bg: '#f43f5e', border: '#e11d48', glow: 'rgba(244, 63, 94, 0.4)', text: '#ffffff' },
  HASH: { bg: '#a855f7', border: '#9333ea', glow: 'rgba(168, 85, 247, 0.4)', text: '#ffffff' },
  KEYWORD: { bg: '#71717a', border: '#52525b', glow: 'rgba(113, 113, 122, 0.4)', text: '#ffffff' },
  UNKNOWN: { bg: '#94a3b8', border: '#64748b', glow: 'rgba(148, 163, 184, 0.4)', text: '#ffffff' },
};

const getEntityImage = (ent: any, category: string): string => {
  const avatar = extractEntityAvatar(ent);
  if (avatar) return avatar;
  return getCategorySvgIcon(category, '#ffffff');
};

export const GraphStudioComponent: React.FC<Props> = ({
  investigationId,
  entities = [],
  relationships = [],
}) => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const cyRef = useRef<Core | null>(null);

  // Studio Controls & Configuration
  const [activeLayout, setActiveLayout] = useState<LayoutName>('cose');
  const [filterCategory, setFilterCategory] = useState<string>('ALL');
  const [searchFilter, setSearchFilter] = useState<string>('');
  const [canvasTheme, setCanvasTheme] = useState<'blueprint' | 'cyber'>('blueprint');
  const [showUnlinkedOnCanvas, setShowUnlinkedOnCanvas] = useState<boolean>(false);
  const [unlinkedDrawerOpen, setUnlinkedDrawerOpen] = useState<boolean>(false);
  const [unlinkedCategory, setUnlinkedCategory] = useState<string>('ALL');
  const [unlinkedSearch, setUnlinkedSearch] = useState<string>('');

  const [inspectorOpen, setInspectorOpen] = useState<boolean>(true);
  const [pathfindingMode, setPathfindingMode] = useState<boolean>(false);
  const [pathSource, setPathSource] = useState<string | null>(null);
  const [pathTarget, setPathTarget] = useState<string | null>(null);

  // Inspector & Selection State
  const [selectedEntity, setSelectedEntity] = useState<Entity | null>(null);
  const [selectedEdgeData, setSelectedEdgeData] = useState<any | null>(null);
  const [hoveredTooltip, setHoveredTooltip] = useState<HoverTooltipData | null>(null);
  const [expandedBranches, setExpandedBranches] = useState<Record<string, { nodeIds: string[]; edgeIds: string[] }>>({});
  const [userPinnedEntities, setUserPinnedEntities] = useState<Entity[]>([]);
  const [isExpanding, setIsExpanding] = useState<boolean>(false);
  const [feedback, setFeedback] = useState<{ message: string; type: 'info' | 'success' | 'warning' | 'error' } | null>(null);

  // 1. Calculate Connected Node Keys and Degrees
  const { connectedKeys, degrees, rootCandidate } = useMemo(() => {
    const conn = new Set<string>();
    const deg: Record<string, number> = {};

    (relationships || []).forEach((r) => {
      const s = (r.source_entity_value || (r as any).source_id || '').toLowerCase().trim();
      const t = (r.target_entity_value || (r as any).target_id || '').toLowerCase().trim();
      if (s && t && s !== t) {
        conn.add(s);
        conn.add(t);
        deg[s] = (deg[s] || 0) + 1;
        deg[t] = (deg[t] || 0) + 1;
      }
    });

    let maxDeg = -1;
    let candidate: Entity | null = null;
    entities.forEach((e) => {
      const key = (e.value || (e as any).name || e.id || '').toLowerCase().trim();
      const d = deg[key] || 0;
      if (d > maxDeg) {
        maxDeg = d;
        candidate = e;
      }
    });

    return {
      connectedKeys: conn,
      degrees: deg,
      rootCandidate: candidate || entities[0] || null,
    };
  }, [entities, relationships]);

  // Update selected entity when rootCandidate or entities change
  useEffect(() => {
    const isCurrentEntityValid =
      selectedEntity &&
      entities.some(
        (e) =>
          (e.value || (e as any).name || e.id) ===
          (selectedEntity.value || (selectedEntity as any).name || selectedEntity.id)
      );

    if (!isCurrentEntityValid) {
      setSelectedEntity(rootCandidate);
    }
    setSelectedEdgeData(null);
    setExpandedBranches({});
    setUserPinnedEntities([]);
  }, [entities, rootCandidate]);

  // 2. Separate Connected & Unlinked Entities
  const { connectedEntitiesList, unlinkedEntitiesList, categoryStats } = useMemo(() => {
    const connList: Entity[] = [];
    const unlinkList: Entity[] = [];
    const stats: Record<string, number> = { ALL: entities.length };

    const pinnedKeys = new Set(
      userPinnedEntities.map((p) => (p.value || (p as any).name || p.id || '').toLowerCase().trim())
    );

    entities.forEach((e) => {
      const key = (e.value || (e as any).name || e.id || '').toLowerCase().trim();
      const isConn = connectedKeys.has(key) || pinnedKeys.has(key);
      const cat = getEntityCategory(e.type);
      stats[cat] = (stats[cat] || 0) + 1;

      if (isConn) {
        connList.push(e);
      } else {
        unlinkList.push(e);
      }
    });

    return {
      connectedEntitiesList: connList,
      unlinkedEntitiesList: unlinkList,
      categoryStats: stats,
    };
  }, [entities, connectedKeys, userPinnedEntities]);

  // Filtered entities for Cytoscape Canvas
  const filteredEntities = useMemo(() => {
    // If no relationships exist yet or user toggled unlinked on canvas, show all entities so the canvas is never empty
    const sourceList = (showUnlinkedOnCanvas || connectedEntitiesList.length === 0) ? entities : connectedEntitiesList;
    const filtered = sourceList.filter((e) => {
      if (filterCategory !== 'ALL' && getEntityCategory(e.type) !== filterCategory) return false;
      if (searchFilter.trim()) {
        const q = searchFilter.toLowerCase();
        const matches =
          (e.value || '').toLowerCase().includes(q) ||
          ((e as any).name || '').toLowerCase().includes(q) ||
          (e.type || '').toLowerCase().includes(q);
        if (!matches) return false;
      }
      return true;
    });

    // Ensure rootCandidate is always present if available
    if (rootCandidate && !filtered.some(e => (e.value || (e as any).name || e.id) === (rootCandidate.value || (rootCandidate as any).name || rootCandidate.id))) {
      filtered.unshift(rootCandidate);
    }
    return filtered;
  }, [entities, connectedEntitiesList, showUnlinkedOnCanvas, filterCategory, searchFilter, rootCandidate]);

  // Filtered unlinked list for Unlinked Intelligence Tray
  const filteredUnlinkedTray = useMemo(() => {
    return unlinkedEntitiesList.filter((e) => {
      if (unlinkedCategory !== 'ALL' && getEntityCategory(e.type) !== unlinkedCategory) return false;
      if (unlinkedSearch.trim()) {
        const q = unlinkedSearch.toLowerCase();
        return (
          (e.value || '').toLowerCase().includes(q) ||
          ((e as any).name || '').toLowerCase().includes(q) ||
          (e.type || '').toLowerCase().includes(q)
        );
      }
      return true;
    });
  }, [unlinkedEntitiesList, unlinkedCategory, unlinkedSearch]);

  // 3. Build Cytoscape Elements with embedded images and legible pill labels
  const elements = useMemo(() => {
    const elems: cytoscape.ElementDefinition[] = [];
    const rootVal = (selectedEntity?.value || rootCandidate?.value || '').toLowerCase().trim();

    const entMap = new Map<string, string>();
    filteredEntities.forEach((ent) => {
      const val = (ent.value || (ent as any).name || ent.id || '').trim();
      const id = ent.id || `node_${val.toLowerCase().replace(/[^a-z0-9_-]/g, '_')}`;
      entMap.set(val.toLowerCase(), id);
      if (ent.id) entMap.set(ent.id.toLowerCase(), id);

      const cat = getEntityCategory(ent.type);
      const isRoot = val.toLowerCase() === rootVal;
      const deg = degrees[val.toLowerCase()] || 0;
      const size = isRoot ? 66 : Math.min(68, Math.max(46, 46 + deg * 3));
      const bgImage = getEntityImage(ent, cat);

      elems.push({
        group: 'nodes',
        data: {
          id,
          label: val.length > 28 ? `${val.slice(0, 26)}…` : val,
          fullLabel: val,
          category: cat,
          color: CATEGORY_COLORS[cat]?.bg || '#64748b',
          borderColor: isRoot ? '#4f46e5' : CATEGORY_COLORS[cat]?.border || '#475569',
          borderWidth: isRoot ? 4 : 2.5,
          isRoot,
          size,
          bgImage,
          rawEntity: ent,
        },
      });
    });

    const seenEdges = new Set<string>();
    (relationships || []).forEach((rel, idx) => {
      const srcVal = (rel.source_entity_value || (rel as any).source_id || '').toLowerCase().trim();
      const tgtVal = (rel.target_entity_value || (rel as any).target_id || '').toLowerCase().trim();
      const srcId = entMap.get(srcVal);
      const tgtId = entMap.get(tgtVal);

      if (srcId && tgtId && srcId !== tgtId) {
        const edgeKey = `${srcId}->${tgtId}`;
        if (!seenEdges.has(edgeKey)) {
          seenEdges.add(edgeKey);
          const relType = rel.relationship_type || (rel as any).type || 'RELATED';
          const isInferred = Boolean(rel.metadata?.is_inferred || (rel as any).is_inferred);

          elems.push({
            group: 'edges',
            data: {
              id: (rel as any).id || `edge_${idx}_${srcId}_${tgtId}`,
              source: srcId,
              target: tgtId,
              label: relType.replace(/_/g, ' ').toLowerCase(),
              lineStyle: isInferred ? 'dashed' : 'solid',
              rawRel: rel,
            },
          });
        }
      }
    });

    // Add user-pinned virtual edges to root
    if (rootCandidate) {
      const rootId = entMap.get((rootCandidate.value || '').toLowerCase());
      if (rootId) {
        userPinnedEntities.forEach((pinned, idx) => {
          const pVal = (pinned.value || (pinned as any).name || pinned.id || '').toLowerCase().trim();
          const pId = entMap.get(pVal);
          if (pId && pId !== rootId) {
            const edgeKey = `pinned_${rootId}->${pId}`;
            if (!seenEdges.has(edgeKey)) {
              seenEdges.add(edgeKey);
              elems.push({
                group: 'edges',
                data: {
                  id: `pinned_edge_${idx}`,
                  source: rootId,
                  target: pId,
                  label: 'pinned indicator',
                  lineStyle: 'dashed',
                  rawRel: {
                    source_entity_value: rootCandidate.value,
                    target_entity_value: pinned.value,
                    relationship_type: 'PINNED_INDICATOR',
                    is_inferred: true,
                  },
                },
              });
            }
          }
        });
      }
    }

    return elems;
  }, [filteredEntities, relationships, selectedEntity, rootCandidate, degrees, userPinnedEntities]);

  // 4. Initialize Cytoscape Instance
  useEffect(() => {
    if (!containerRef.current) return;

    const cy = cytoscape({
      container: containerRef.current,
      elements: [],
      style: [
        {
          selector: 'node',
          style: {
            'background-color': 'data(color)',
            'background-image': 'data(bgImage)',
            'background-fit': 'contain',
            'background-clip': 'node',
            'background-width': '62%',
            'background-height': '62%',
            'background-position-x': '50%',
            'background-position-y': '50%',
            label: 'data(label)',
            width: 'data(size)',
            height: 'data(size)',
            'border-width': 'data(borderWidth)',
            'border-color': 'data(borderColor)',
            'border-opacity': 0.95,
            color: canvasTheme === 'cyber' ? '#f1f5f9' : '#0f172a',
            'font-family': 'Inter, system-ui, -apple-system, sans-serif',
            'font-size': '11px',
            'font-weight': 700,
            'text-valign': 'bottom',
            'text-margin-y': 8,
            'text-wrap': 'wrap',
            'text-max-width': '140px',
            'text-background-opacity': 0.96,
            'text-background-color': canvasTheme === 'cyber' ? '#0f172a' : '#ffffff',
            'text-background-padding': '4px',
            'text-background-shape': 'roundrectangle',
            'text-border-opacity': 0.8,
            'text-border-width': 1,
            'text-border-color': canvasTheme === 'cyber' ? '#334155' : '#cbd5e1',
            'overlay-opacity': 0,
            'transition-property': 'background-color, border-color, border-width, opacity',
            'transition-duration': 0.2,
          },
        },
        {
          selector: 'node:selected',
          style: {
            'border-width': 4.5,
            'border-color': '#6366f1',
            'border-opacity': 1,
            'underlay-color': '#6366f1',
            'underlay-padding': 8,
            'underlay-opacity': 0.35,
          },
        },
        {
          selector: 'node[?isRoot]',
          style: {
            'border-width': 4.5,
            'border-color': '#4f46e5',
            'border-opacity': 1,
            'underlay-color': '#4f46e5',
            'underlay-padding': 8,
            'underlay-opacity': 0.3,
            'text-background-color': canvasTheme === 'cyber' ? '#1e1b4b' : '#eff6ff',
            'text-border-color': '#818cf8',
          },
        },
        {
          selector: 'edge',
          style: {
            width: 2.2,
            'line-color': canvasTheme === 'cyber' ? '#475569' : '#94a3b8',
            'line-style': 'data(lineStyle)' as any,
            'target-arrow-color': canvasTheme === 'cyber' ? '#64748b' : '#64748b',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'arrow-scale': 1.2,
            label: 'data(label)',
            color: canvasTheme === 'cyber' ? '#cbd5e1' : '#334155',
            'font-size': '10px',
            'font-weight': 600,
            'font-family': 'Inter, system-ui, sans-serif',
            'text-rotation': 'autorotate',
            'text-background-opacity': 0.94,
            'text-background-color': canvasTheme === 'cyber' ? '#0f172a' : '#f8fafc',
            'text-background-padding': '3px',
            'text-background-shape': 'roundrectangle',
            'text-border-opacity': 0.6,
            'text-border-width': 1,
            'text-border-color': canvasTheme === 'cyber' ? '#334155' : '#cbd5e1',
            opacity: 0.9,
          },
        },
        {
          selector: 'edge:selected',
          style: {
            width: 3.5,
            'line-color': '#6366f1',
            'target-arrow-color': '#6366f1',
            opacity: 1,
          },
        },
        {
          selector: '.highlighted',
          style: {
            'border-width': 4.5,
            'border-color': '#6366f1',
            'line-color': '#6366f1',
            'target-arrow-color': '#6366f1',
            opacity: 1,
            'z-index': 99,
          },
        },
        {
          selector: '.faded',
          style: {
            opacity: 0.12,
          },
        },
      ],
      layout: {
        name: activeLayout,
        animate: true,
        animationDuration: 500,
        nodeRepulsion: (node: any) => 3500000,
        idealEdgeLength: (edge: any) => 220,
        edgeElasticity: (edge: any) => 45,
        gravity: 0.08,
        numIter: 1200,
        padding: 80,
      } as any,
      wheelSensitivity: 0.25,
      minZoom: 0.2,
      maxZoom: 3.0,
    });

    // Node Click Handler
    cy.on('tap', 'node', (evt: EventObject) => {
      const node = evt.target;
      const raw = node.data('rawEntity');
      if (raw) {
        setSelectedEntity(raw);
        setSelectedEdgeData(null);
        setInspectorOpen(true);
      }

      cy.elements().removeClass('highlighted faded');
      const neighborhood = node.neighborhood().add(node);
      cy.elements().not(neighborhood).addClass('faded');
      neighborhood.addClass('highlighted');
    });

    // Edge Click Handler
    cy.on('tap', 'edge', (evt: EventObject) => {
      const edge = evt.target;
      const raw = edge.data('rawRel');
      setSelectedEdgeData(raw || edge.data());
      setSelectedEntity(null);
      setInspectorOpen(true);
    });

    // Canvas Background Click: Reset highlights & close hover tooltips
    cy.on('tap', (evt: EventObject) => {
      if (evt.target === cy) {
        cy.elements().removeClass('highlighted faded');
        setHoveredTooltip(null);
      }
    });

    // Interactive Hover Tooltips
    cy.on('mouseover', 'node', (evt: EventObject) => {
      const node = evt.target;
      const raw = node.data('rawEntity');
      const pos = node.renderedPosition();
      setHoveredTooltip({
        type: 'node',
        title: node.data('fullLabel') || node.data('label'),
        category: node.data('category'),
        entityType: raw?.type || node.data('category'),
        degree: node.degree(),
        provenance: raw?.provenance || raw?.metadata?.source || raw?.provider,
        confidence: raw?.confidence,
        x: pos.x,
        y: pos.y - (node.data('size') / 2) - 10,
      });
    });

    cy.on('mouseout', 'node', () => {
      setHoveredTooltip(null);
    });

    cy.on('mouseover', 'edge', (evt: EventObject) => {
      const edge = evt.target;
      const raw = edge.data('rawRel');
      const mid = edge.renderedMidpoint();
      setHoveredTooltip({
        type: 'edge',
        title: edge.data('label') || 'CONNECTED_TO',
        sourceLabel: edge.source().data('label'),
        targetLabel: edge.target().data('label'),
        confidence: raw?.confidence || raw?.metadata?.confidence,
        provenance: raw?.provenance || raw?.source,
        x: mid.x,
        y: mid.y - 10,
      });
    });

    cy.on('mouseout', 'edge', () => {
      setHoveredTooltip(null);
    });

    cy.on('pan zoom drag', () => {
      setHoveredTooltip(null);
    });

    cyRef.current = cy;

    return () => {
      cy.destroy();
      cyRef.current = null;
    };
  }, [canvasTheme]);

  // Update Cytoscape Elements & Run Layout with Spacious Repulsion
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;

    cy.batch(() => {
      cy.elements().remove();
      cy.add(elements);
    });

    let layoutConfig: any = {
      name: activeLayout,
      animate: true,
      animationDuration: 500,
      padding: 80,
    };

    if (activeLayout === 'cose') {
      layoutConfig = {
        ...layoutConfig,
        nodeRepulsion: (node: any) => (showUnlinkedOnCanvas ? 4500000 : 3200000),
        idealEdgeLength: (edge: any) => 220,
        edgeElasticity: (edge: any) => 45,
        gravity: 0.08,
        numIter: 1200,
        nodeOverlap: 40,
        componentSpacing: 140,
      };
    } else if (activeLayout === 'concentric') {
      layoutConfig = {
        ...layoutConfig,
        concentric: (node: any) => (node.data('isRoot') ? 4 : (node.degree() || 1)),
        levelWidth: () => 1,
        minNodeSpacing: 90,
      };
    }

    const layout = cy.layout(layoutConfig);
    layout.run();
  }, [elements, activeLayout, showUnlinkedOnCanvas]);

  // Robust 1-Hop Graph Expansion: Safe against nonexistent targets
  const handleExpand1Hop = async () => {
    if (!selectedEntity || isExpanding) return;
    setIsExpanding(true);
    setFeedback(null);
    try {
      const entVal = selectedEntity.value || (selectedEntity as any).name || selectedEntity.id;
      const res = await apiRequest<any>(
        `/graph/expand?entity_id=${encodeURIComponent(entVal)}${investigationId ? `&investigation_id=${encodeURIComponent(investigationId)}` : ''}&limit=25`
      );
      const incomingEdges = res.edges || [];
      const incomingNodes = res.nodes || [];

      if (incomingEdges.length === 0) {
        setFeedback({
          message: `No further verified relationships found in graph database for '${entVal}'.`,
          type: 'info',
        });
        return;
      }

      const cy = cyRef.current;
      if (!cy) return;

      const knownNodeIds = new Set<string>();
      cy.nodes().forEach((n) => {
        knownNodeIds.add(n.id());
      });

      const newNodes: cytoscape.ElementDefinition[] = [];
      const newNodeIds: string[] = [];
      const newEdgeIds: string[] = [];

      // 1. Add incoming nodes
      incomingNodes.forEach((nDoc: any) => {
        const val = (nDoc.value || nDoc.name || nDoc.id || '').trim();
        const id = nDoc.id || `node_${val.toLowerCase().replace(/[^a-z0-9_-]/g, '_')}`;

        if (!knownNodeIds.has(id)) {
          const cat = getEntityCategory(nDoc.type);
          const bgImage = getEntityImage(nDoc, cat);
          newNodes.push({
            group: 'nodes',
            data: {
              id,
              label: val.length > 28 ? `${val.slice(0, 26)}…` : val,
              fullLabel: val,
              category: cat,
              color: CATEGORY_COLORS[cat]?.bg || '#64748b',
              borderColor: CATEGORY_COLORS[cat]?.border || '#475569',
              borderWidth: 2.5,
              isRoot: false,
              size: 46,
              bgImage,
              rawEntity: nDoc,
            },
          });
          knownNodeIds.add(id);
          newNodeIds.push(id);
        }
      });

      if (newNodes.length > 0) {
        cy.add(newNodes);
      }

      // 2. Connect edges safely
      incomingEdges.forEach((r: any, idx: number) => {
        const sRaw = (r.source_id || r.source_entity_value || '').toLowerCase().trim();
        const tRaw = (r.target_id || r.target_entity_value || '').toLowerCase().trim();

        const sId = knownNodeIds.has(sRaw)
          ? sRaw
          : knownNodeIds.has(`node_${sRaw.replace(/[^a-z0-9_-]/g, '_')}`)
          ? `node_${sRaw.replace(/[^a-z0-9_-]/g, '_')}`
          : sRaw;

        const tId = knownNodeIds.has(tRaw)
          ? tRaw
          : knownNodeIds.has(`node_${tRaw.replace(/[^a-z0-9_-]/g, '_')}`)
          ? `node_${tRaw.replace(/[^a-z0-9_-]/g, '_')}`
          : tRaw;

        if (!knownNodeIds.has(sId)) {
          const sLabel = r.source_entity_value || sRaw;
          const cat = 'DOMAIN';
          cy.add({
            group: 'nodes',
            data: {
              id: sId,
              label: sLabel.length > 28 ? `${sLabel.slice(0, 26)}…` : sLabel,
              fullLabel: sLabel,
              category: cat,
              color: CATEGORY_COLORS[cat]?.bg || '#64748b',
              borderColor: CATEGORY_COLORS[cat]?.border || '#475569',
              borderWidth: 2,
              size: 42,
              bgImage: getCategorySvgIcon(cat, '#ffffff'),
              rawEntity: { id: sId, value: sLabel, type: cat },
            },
          });
          knownNodeIds.add(sId);
          newNodeIds.push(sId);
        }

        if (!knownNodeIds.has(tId)) {
          const tLabel = r.target_entity_value || tRaw;
          const cat = 'DOMAIN';
          cy.add({
            group: 'nodes',
            data: {
              id: tId,
              label: tLabel.length > 28 ? `${tLabel.slice(0, 26)}…` : tLabel,
              fullLabel: tLabel,
              category: cat,
              color: CATEGORY_COLORS[cat]?.bg || '#64748b',
              borderColor: CATEGORY_COLORS[cat]?.border || '#475569',
              borderWidth: 2,
              size: 42,
              bgImage: getCategorySvgIcon(cat, '#ffffff'),
              rawEntity: { id: tId, value: tLabel, type: cat },
            },
          });
          knownNodeIds.add(tId);
          newNodeIds.push(tId);
        }

        const edgeId = r.id || `exp_edge_${idx}_${sId}_${tId}`;
        if (cy.getElementById(edgeId).length === 0) {
          const rType = r.relationship_type || r.type || 'RELATED';
          cy.add({
            group: 'edges',
            data: {
              id: edgeId,
              source: sId,
              target: tId,
              label: rType.replace(/_/g, ' ').toLowerCase(),
              lineStyle: r.is_inferred ? 'dashed' : 'solid',
              rawRel: r,
            },
          });
          newEdgeIds.push(edgeId);
        }
      });

      // Smooth concentric repositioning around parent
      const parentNode = cy.getElementById(selectedEntity.id || `node_${entVal.toLowerCase().replace(/[^a-z0-9_-]/g, '_')}`);
      if (parentNode.length > 0) {
        const neighborhood = parentNode.neighborhood().add(parentNode);
        const subLayout = neighborhood.layout({
          name: 'concentric',
          concentric: (node: any) => (node.id() === parentNode.id() ? 2 : 1),
          levelWidth: () => 1,
          minNodeSpacing: 90,
          animate: true,
          animationDuration: 400,
        } as any);
        subLayout.run();
      }

      const branchKey = selectedEntity.id || entVal;
      setExpandedBranches((prev) => ({
        ...prev,
        [branchKey]: { nodeIds: newNodeIds, edgeIds: newEdgeIds },
      }));

      setFeedback({
        message: `Expanded ${newNodeIds.length} connected entities & ${newEdgeIds.length} verified paths.`,
        type: 'success',
      });
    } catch (err: any) {
      setFeedback({
        message: `Expansion failed: ${err.message || 'Server error'}.`,
        type: 'error',
      });
    } finally {
      setIsExpanding(false);
    }
  };

  // Branch Collapse
  const handleCollapseBranch = () => {
    if (!selectedEntity) return;
    const branchKey = selectedEntity.id || selectedEntity.value || (selectedEntity as any).name;
    const branchData = expandedBranches[branchKey];
    if (!branchData || !cyRef.current) return;

    const cy = cyRef.current;
    const otherBranchNodeIds = new Set<string>();
    Object.entries(expandedBranches).forEach(([bKey, data]) => {
      if (bKey !== branchKey) {
        data.nodeIds.forEach((id) => otherBranchNodeIds.add(id));
      }
    });

    const nodesToRemove = branchData.nodeIds.filter((nid) => !otherBranchNodeIds.has(nid));
    nodesToRemove.forEach((nid) => cy.remove(cy.getElementById(nid)));
    branchData.edgeIds.forEach((eid) => cy.remove(cy.getElementById(eid)));

    setExpandedBranches((prev) => {
      const next = { ...prev };
      delete next[branchKey];
      return next;
    });

    setFeedback({
      message: `Branch collapsed. Shared nodes preserved.`,
      type: 'info',
    });
  };

  // Pin Unlinked Entity directly into Graph
  const handlePinUnlinkedEntity = (ent: Entity) => {
    setUserPinnedEntities((prev) => {
      const exists = prev.some((p) => (p.value || p.id) === (ent.value || ent.id));
      if (exists) return prev;
      return [...prev, ent];
    });
    setFeedback({
      message: `Pinned '${ent.value || (ent as any).name}' to graph.`,
      type: 'success',
    });
  };

  // Shortest Path Finder
  const handleFindPath = () => {
    const cy = cyRef.current;
    if (!cy || !pathSource || !pathTarget) return;

    const srcNode = cy.getElementById(pathSource);
    const tgtNode = cy.getElementById(pathTarget);
    if (srcNode.length === 0 || tgtNode.length === 0) return;

    const aStar = cy.elements().aStar({
      root: srcNode,
      goal: tgtNode,
      directed: false,
    });

    if (aStar.found) {
      cy.elements().removeClass('highlighted faded');
      cy.elements().not(aStar.path).addClass('faded');
      aStar.path.addClass('highlighted');
      setFeedback({
        message: `Shortest path discovered: ${aStar.distance} hops connecting '${srcNode.data('label')}' to '${tgtNode.data('label')}'.`,
        type: 'success',
      });
    } else {
      setFeedback({
        message: `No connected traversal path found between selected entities.`,
        type: 'warning',
      });
    }
  };

  // Export Graph Image
  const handleExportPNG = () => {
    const cy = cyRef.current;
    if (!cy) return;
    const png64 = cy.png({ full: true, scale: 2, bg: canvasTheme === 'cyber' ? '#090d16' : '#ffffff' });
    const a = document.createElement('a');
    a.href = png64;
    a.download = `investigation_relationship_graph_${Date.now()}.png`;
    a.click();
  };

  if (entities.length === 0) {
    return (
      <div className="rounded-2xl border border-dashed border-slate-300 dark:border-slate-800 bg-white dark:bg-slate-900/40 p-12 text-center space-y-4">
        <div className="w-12 h-12 rounded-full bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 flex items-center justify-center mx-auto text-slate-500">
          <Network className="w-6 h-6" />
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
    <div className="space-y-3 font-sans">
      {/* Modern OSINT Link Analysis Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-3 rounded-2xl border border-slate-200/90 bg-white shadow-2xs dark:border-slate-800 dark:bg-[#0f1422] text-xs">
        <div className="flex flex-wrap items-center gap-2">
          {/* Layout Algorithm Selector */}
          <div className="flex items-center gap-0.5 bg-slate-100 dark:bg-slate-800/90 p-0.5 rounded-xl font-mono">
            <button
              type="button"
              onClick={() => setActiveLayout('cose')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[11px] transition-all cursor-pointer ${
                activeLayout === 'cose'
                  ? 'bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-xs font-bold'
                  : 'text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100'
              }`}
              title="Force-Directed CoSE: Organic physics simulation clustering connected nodes"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Force Network</span>
            </button>
            <button
              type="button"
              onClick={() => setActiveLayout('concentric')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[11px] transition-all cursor-pointer ${
                activeLayout === 'concentric'
                  ? 'bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-xs font-bold'
                  : 'text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100'
              }`}
              title="Concentric: Orbits arranged by node importance and degrees"
            >
              <Radio className="w-3.5 h-3.5" />
              <span>Radial Orbits</span>
            </button>
            <button
              type="button"
              onClick={() => setActiveLayout('breadthfirst')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[11px] transition-all cursor-pointer ${
                activeLayout === 'breadthfirst'
                  ? 'bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-xs font-bold'
                  : 'text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100'
              }`}
              title="Hierarchical: Top-to-bottom command & infrastructure hierarchy"
            >
              <GitFork className="w-3.5 h-3.5" />
              <span>Hierarchy</span>
            </button>
            <button
              type="button"
              onClick={() => setActiveLayout('circle')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[11px] transition-all cursor-pointer ${
                activeLayout === 'circle'
                  ? 'bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-xs font-bold'
                  : 'text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100'
              }`}
              title="Circular: Uniform ring layout"
            >
              <Focus className="w-3.5 h-3.5" />
              <span>Circle</span>
            </button>
          </div>

          {/* Interactive Category Filter Pills */}
          <div className="flex items-center gap-1 overflow-x-auto py-0.5">
            {[
              { id: 'ALL', label: 'All', color: '#6366f1' },
              { id: 'PHONE', label: 'Phones', color: '#0284c7' },
              { id: 'EMAIL', label: 'Emails', color: '#0d9488' },
              { id: 'PERSON', label: 'Identities', color: '#f59e0b' },
              { id: 'ORGANIZATION', label: 'Organizations', color: '#6366f1' },
              { id: 'VEHICLE', label: 'Vehicles', color: '#8b5cf6' },
              { id: 'DOMAIN', label: 'Domains', color: '#64748b' },
              { id: 'IP', label: 'IPs', color: '#2563eb' },
              { id: 'LOCATION', label: 'Locations', color: '#06b6d4' },
              { id: 'ARTICLE', label: 'Articles', color: '#10b981' },
              { id: 'VIDEO', label: 'Videos', color: '#ef4444' },
              { id: 'POST', label: 'Posts', color: '#84cc16' },
              { id: 'THREAT_INDICATOR', label: 'Threats', color: '#f43f5e' },
              { id: 'KEYWORD', label: 'Keywords', color: '#71717a' },
              { id: 'UNKNOWN', label: 'Other', color: '#94a3b8' },
            ]
              .filter((cat) => cat.id === 'ALL' || (categoryStats[cat.id] || 0) > 0)
              .map((cat) => {
                const count = categoryStats[cat.id] || 0;
                const isSelected = filterCategory === cat.id;
                return (
                  <button
                    key={cat.id}
                    type="button"
                    onClick={() => setFilterCategory(cat.id)}
                    className={`flex items-center gap-1 px-2.5 py-1 rounded-lg text-[11px] font-mono font-bold transition-all cursor-pointer border ${
                      isSelected
                        ? 'bg-slate-900 text-white border-slate-900 dark:bg-white dark:text-slate-900 dark:border-white shadow-2xs'
                        : 'bg-slate-50 text-slate-600 border-slate-200 hover:border-slate-300 dark:bg-slate-900 dark:text-slate-400 dark:border-slate-800'
                    }`}
                  >
                    <span className="w-2 h-2 rounded-full inline-block" style={{ backgroundColor: cat.color }} />
                    <span>{cat.label}</span>
                    <span className={`text-[10px] px-1 py-0.2 rounded font-normal ${isSelected ? 'bg-white/20 text-white dark:bg-black/20 dark:text-slate-900' : 'bg-slate-200 dark:bg-slate-800'}`}>
                      {count}
                    </span>
                  </button>
                );
              })}
          </div>

          {/* Toggle Unlinked Isolated Entities Drawer */}
          {unlinkedEntitiesList.length > 0 && (
            <button
              type="button"
              onClick={() => setUnlinkedDrawerOpen((prev) => !prev)}
              className={`flex items-center gap-1.5 h-8 px-3 rounded-xl border text-xs font-mono font-bold transition-all cursor-pointer ${
                unlinkedDrawerOpen
                  ? 'bg-amber-500 text-white border-amber-500 shadow-2xs'
                  : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50 dark:bg-slate-900 dark:border-slate-800 dark:text-slate-300'
              }`}
              title="Inspect unlinked background profiles and entities without cluttering the graph canvas"
            >
              <Layers className="w-3.5 h-3.5" />
              <span>Unlinked Tray ({unlinkedEntitiesList.length})</span>
              {unlinkedDrawerOpen ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
            </button>
          )}

          {/* Pathfinding Mode Toggle */}
          <button
            type="button"
            onClick={() => {
              setPathfindingMode((prev) => !prev);
              if (pathfindingMode && cyRef.current) {
                cyRef.current.elements().removeClass('highlighted faded');
                setPathSource(null);
                setPathTarget(null);
              }
            }}
            className={`flex items-center gap-1.5 h-8 px-3 rounded-xl border text-xs font-mono transition-all cursor-pointer ${
              pathfindingMode
                ? 'bg-indigo-600 text-white border-indigo-600 font-bold shadow-2xs'
                : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50 dark:bg-slate-900 dark:border-slate-800 dark:text-slate-300'
            }`}
            title="Shortest path finder between two target entities"
          >
            <Route className="w-3.5 h-3.5" />
            <span>Pathfinder</span>
          </button>
        </div>

        <div className="flex items-center gap-2">
          {/* In-Graph Search */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Find node..."
              value={searchFilter}
              onChange={(e) => {
                setSearchFilter(e.target.value);
                const q = e.target.value.toLowerCase().trim();
                const cy = cyRef.current;
                if (cy && q) {
                  const match = cy.nodes().filter((n) => n.data('label')?.toLowerCase().includes(q));
                  if (match.length > 0) {
                    cy.center(match);
                    cy.elements().removeClass('highlighted faded');
                    match.addClass('highlighted');
                  }
                }
              }}
              className="h-8 pl-8 pr-3 rounded-xl bg-slate-50 border border-slate-200 text-xs font-mono text-slate-800 focus:outline-none focus:border-indigo-500 dark:bg-slate-900 dark:border-slate-800 dark:text-slate-200 w-36 shadow-inner"
            />
          </div>

          {/* Canvas Blueprint / Cyber Theme Toggle */}
          <button
            type="button"
            onClick={() => setCanvasTheme((prev) => (prev === 'blueprint' ? 'cyber' : 'blueprint'))}
            className="p-2 rounded-xl border border-slate-200 hover:bg-slate-100 text-slate-600 dark:border-slate-800 dark:hover:bg-slate-800 dark:text-slate-300 cursor-pointer transition-colors"
            title={`Toggle Theme: Currently ${canvasTheme.toUpperCase()}`}
          >
            {canvasTheme === 'blueprint' ? <Moon className="w-3.5 h-3.5 text-indigo-500" /> : <Sun className="w-3.5 h-3.5 text-amber-400" />}
          </button>

          {/* Visible Nodes / Edges Counter */}
          <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-[11px] font-mono text-slate-700 dark:text-slate-300">
            <Activity className="w-3.5 h-3.5 text-emerald-500" />
            <span>{filteredEntities.length} nodes</span>
            <span className="text-slate-400">•</span>
            <span>{relationships.length} edges</span>
          </div>

          {/* Canvas Navigation Controls */}
          <div className="flex items-center gap-0.5 border border-slate-200 dark:border-slate-800 rounded-xl p-1 bg-slate-50/50 dark:bg-slate-900/50">
            <button
              type="button"
              onClick={() => cyRef.current?.zoom(cyRef.current.zoom() * 1.25)}
              className="p-1 rounded-lg hover:bg-slate-200 text-slate-600 dark:hover:bg-slate-800 dark:text-slate-300 cursor-pointer"
              title="Zoom In"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
            <button
              type="button"
              onClick={() => cyRef.current?.zoom(cyRef.current.zoom() * 0.8)}
              className="p-1 rounded-lg hover:bg-slate-200 text-slate-600 dark:hover:bg-slate-800 dark:text-slate-300 cursor-pointer"
              title="Zoom Out"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <button
              type="button"
              onClick={() => cyRef.current?.fit(undefined, 70)}
              className="p-1 rounded-lg hover:bg-slate-200 text-slate-600 dark:hover:bg-slate-800 dark:text-slate-300 cursor-pointer"
              title="Fit to Center"
            >
              <Compass className="w-3.5 h-3.5" />
            </button>
            <button
              type="button"
              onClick={handleExportPNG}
              className="p-1 rounded-lg hover:bg-slate-200 text-slate-600 dark:hover:bg-slate-800 dark:text-slate-300 cursor-pointer"
              title="Export High-Resolution PNG for Investigation Report"
            >
              <Download className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Toggle Inspector */}
          <button
            type="button"
            onClick={() => setInspectorOpen((prev) => !prev)}
            className={`flex items-center gap-1.5 h-8 px-3 rounded-xl border text-xs font-mono font-bold transition-all cursor-pointer ${
              inspectorOpen
                ? 'bg-slate-900 text-white border-slate-900 dark:bg-white dark:text-slate-900 dark:border-white shadow-xs'
                : 'border-slate-200 text-slate-600 hover:bg-slate-100 dark:border-slate-800 dark:text-slate-300'
            }`}
          >
            <Info className="w-3.5 h-3.5" />
            <span>Inspector</span>
          </button>
        </div>
      </div>

      {/* Pathfinder Sub-Bar */}
      {pathfindingMode && (
        <div className="flex flex-wrap items-center justify-between gap-3 p-3 rounded-2xl bg-indigo-50/80 border border-indigo-200 dark:bg-indigo-950/30 dark:border-indigo-900/50 text-xs font-mono animate-in fade-in duration-200">
          <div className="flex items-center gap-2">
            <Route className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
            <span className="font-bold text-indigo-950 dark:text-indigo-200">Shortest Path Analyzer:</span>
            <span className="text-slate-600 dark:text-slate-400">Select Origin & Target to calculate optimal link traversal route.</span>
          </div>
          <div className="flex items-center gap-2">
            <select
              value={pathSource || ''}
              onChange={(e) => setPathSource(e.target.value)}
              className="h-8 px-2.5 rounded-xl bg-white border border-indigo-200 text-xs dark:bg-slate-900 dark:border-slate-800"
            >
              <option value="">Select Origin Entity...</option>
              {filteredEntities.map((e) => {
                const id = e.id || `node_${(e.value || (e as any).name || '').toLowerCase().replace(/[^a-z0-9_-]/g, '_')}`;
                return (
                  <option key={id} value={id}>
                    {e.value || (e as any).name}
                  </option>
                );
              })}
            </select>
            <span className="text-indigo-600 font-bold">→</span>
            <select
              value={pathTarget || ''}
              onChange={(e) => setPathTarget(e.target.value)}
              className="h-8 px-2.5 rounded-xl bg-white border border-indigo-200 text-xs dark:bg-slate-900 dark:border-slate-800"
            >
              <option value="">Select Target Entity...</option>
              {filteredEntities.map((e) => {
                const id = e.id || `node_${(e.value || (e as any).name || '').toLowerCase().replace(/[^a-z0-9_-]/g, '_')}`;
                return (
                  <option key={id} value={id}>
                    {e.value || (e as any).name}
                  </option>
                );
              })}
            </select>
            <button
              type="button"
              onClick={handleFindPath}
              disabled={!pathSource || !pathTarget}
              className="h-8 px-4 rounded-xl bg-indigo-600 hover:bg-indigo-700 disabled:opacity-40 text-white font-bold transition-colors cursor-pointer shadow-xs"
            >
              Compute Route
            </button>
          </div>
        </div>
      )}

      {/* Main Graph Canvas and Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-3 relative">
        <div
          className={`${
            inspectorOpen ? 'lg:col-span-3' : 'lg:col-span-4'
          } h-[700px] rounded-2xl border transition-all duration-300 shadow-xs relative overflow-hidden ${
            canvasTheme === 'cyber'
              ? 'bg-[#080c16] border-slate-800 text-white'
              : 'bg-[#f8fafc] border-slate-200 text-slate-900'
          }`}
          style={{
            backgroundImage:
              canvasTheme === 'cyber'
                ? 'radial-gradient(circle, #1e293b 1.3px, transparent 1.3px)'
                : 'radial-gradient(circle, #cbd5e1 1.3px, transparent 1.3px)',
            backgroundSize: '24px 24px',
          }}
        >
          {/* Cytoscape Container */}
          <div ref={containerRef} className="w-full h-full cursor-grab active:cursor-grabbing" />

          {/* Interactive Floating Hover Card Tooltip */}
          {hoveredTooltip && (
            <div
              className="pointer-events-none absolute z-50 transform -translate-x-1/2 -translate-y-full mb-3 px-3.5 py-2.5 rounded-xl shadow-xl border text-xs font-mono transition-opacity duration-150 backdrop-blur-md animate-in fade-in zoom-in-95 duration-100"
              style={{
                left: `${hoveredTooltip.x}px`,
                top: `${hoveredTooltip.y}px`,
                backgroundColor: canvasTheme === 'cyber' ? 'rgba(15, 23, 42, 0.95)' : 'rgba(255, 255, 255, 0.95)',
                borderColor: canvasTheme === 'cyber' ? '#334155' : '#cbd5e1',
                color: canvasTheme === 'cyber' ? '#f8fafc' : '#0f172a',
                maxWidth: '280px',
              }}
            >
              {hoveredTooltip.type === 'node' ? (
                <div className="space-y-1">
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-bold truncate text-[12px]">{hoveredTooltip.title}</span>
                    <Badge variant="outline" className="text-[9px] uppercase">
                      {hoveredTooltip.category}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between text-[10px] text-slate-400 pt-1 border-t border-slate-200/50 dark:border-slate-700/50">
                    <span>Degree: {hoveredTooltip.degree || 0} links</span>
                    {hoveredTooltip.confidence !== undefined && (
                      <span className="text-emerald-500 font-bold">
                        {Math.round(hoveredTooltip.confidence * 100)}% conf
                      </span>
                    )}
                  </div>
                  {hoveredTooltip.provenance && (
                    <div className="text-[9px] text-slate-400 truncate">
                      Source: {hoveredTooltip.provenance}
                    </div>
                  )}
                </div>
              ) : (
                <div className="space-y-1">
                  <div className="font-bold text-indigo-400 text-[11px] uppercase tracking-wider">
                    {hoveredTooltip.title}
                  </div>
                  <div className="text-[10px] text-slate-400 flex items-center gap-1 truncate">
                    <span className="truncate">{hoveredTooltip.sourceLabel}</span>
                    <span>→</span>
                    <span className="truncate">{hoveredTooltip.targetLabel}</span>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Minimalist Legend Overlay */}
          <div className="absolute bottom-4 left-4 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md px-3 py-2 rounded-xl border border-slate-200/90 dark:border-slate-800 text-[10px] font-mono flex items-center gap-3 shadow-xs select-none">
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-purple-500 inline-block" />
              <span className="text-slate-600 dark:text-slate-400">Vehicle</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-cyan-500 inline-block" />
              <span className="text-slate-600 dark:text-slate-400">Location</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-indigo-500 inline-block" />
              <span className="text-slate-600 dark:text-slate-400">Org</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-500 inline-block" />
              <span className="text-slate-600 dark:text-slate-400">Person</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-500 inline-block" />
              <span className="text-slate-600 dark:text-slate-400">Threat</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-blue-500 inline-block" />
              <span className="text-slate-600 dark:text-slate-400">IP</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-teal-500 inline-block" />
              <span className="text-slate-600 dark:text-slate-400">Email</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block" />
              <span className="text-slate-600 dark:text-slate-400">Doc</span>
            </div>
          </div>

          {/* Toggle Canvas vs Tray mode for Unlinked Entities */}
          <div className="absolute top-4 right-4 flex items-center gap-2">
            <button
              type="button"
              onClick={() => setShowUnlinkedOnCanvas((prev) => !prev)}
              className={`px-3 py-1.5 rounded-xl border text-[11px] font-mono font-semibold transition-all cursor-pointer backdrop-blur-md shadow-xs ${
                showUnlinkedOnCanvas
                  ? 'bg-amber-500 text-white border-amber-500'
                  : 'bg-white/90 dark:bg-slate-900/90 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-800 hover:bg-slate-100 dark:hover:bg-slate-800'
              }`}
              title="Display unlinked entities on the canvas periphery"
            >
              {showUnlinkedOnCanvas ? 'Clean Topology (Connected Only)' : 'Display Unlinked on Canvas'}
            </button>
          </div>
        </div>

        {/* Collapsible Inspector Panel */}
        {inspectorOpen && (
          <div className="lg:col-span-1 rounded-2xl border border-slate-200/90 bg-white p-4 space-y-4 shadow-xs dark:border-slate-800 dark:bg-[#0f1422] max-h-[700px] overflow-y-auto">
            {selectedEdgeData ? (
              /* Edge Inspector */
              <div className="space-y-3.5 text-xs">
                <div className="flex items-center justify-between pb-2 border-b border-slate-100 dark:border-slate-800">
                  <div className="flex items-center gap-2">
                    <Link2 className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                    <h3 className="font-mono font-bold text-slate-900 dark:text-white uppercase tracking-wider text-xs">
                      Relationship Provenance
                    </h3>
                  </div>
                  <button
                    type="button"
                    onClick={() => setSelectedEdgeData(null)}
                    className="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-xs cursor-pointer"
                  >
                    ✕
                  </button>
                </div>

                <div>
                  <span className="text-slate-400 uppercase text-[10px] block font-mono">Connection Type</span>
                  <p className="font-mono font-bold text-slate-900 dark:text-white mt-0.5 text-sm uppercase">
                    {selectedEdgeData.relationship_type || selectedEdgeData.label || 'CONNECTED'}
                  </p>
                </div>

                <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 dark:bg-slate-900/60 dark:border-slate-800 space-y-2 font-mono text-[11px]">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Source:</span>
                    <span className="font-semibold text-slate-800 dark:text-slate-200 truncate max-w-[140px]">
                      {selectedEdgeData.source_entity_value || selectedEdgeData.source_id || selectedEdgeData.source}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Target:</span>
                    <span className="font-semibold text-slate-800 dark:text-slate-200 truncate max-w-[140px]">
                      {selectedEdgeData.target_entity_value || selectedEdgeData.target_id || selectedEdgeData.target}
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-slate-500 font-mono text-xs">Evidence Basis</span>
                  <Badge
                    variant={selectedEdgeData.basis === 'DIRECT_OBSERVATION' ? 'success' : 'warning'}
                    className="font-mono text-[10px] uppercase"
                  >
                    {selectedEdgeData.basis || (selectedEdgeData.is_inferred ? 'INFERRED' : 'DIRECT OBSERVATION')}
                  </Badge>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-slate-500 font-mono text-xs">Confidence</span>
                  <Badge variant="mono" className="font-mono text-[10px]">
                    {Math.round((selectedEdgeData.confidence || 0.9) * 100)}%
                  </Badge>
                </div>

                {selectedEdgeData.evidence_ids && selectedEdgeData.evidence_ids.length > 0 && (
                  <div className="space-y-1.5 pt-2 border-t border-slate-100 dark:border-slate-800">
                    <span className="text-slate-400 uppercase text-[10px] block font-mono">Supporting Evidence</span>
                    <div className="flex flex-wrap gap-1">
                      {selectedEdgeData.evidence_ids.map((evId: string, idx: number) => (
                        <span
                          key={idx}
                          className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-200 dark:bg-indigo-950/60 dark:text-indigo-300 dark:border-indigo-800"
                        >
                          Evidence #{evId.slice(0, 8)}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : selectedEntity ? (() => {
              const branchKey = selectedEntity.id || selectedEntity.value || (selectedEntity as any).name;
              const hasActiveBranch = Boolean(expandedBranches[branchKey]);
              const category = getEntityCategory(selectedEntity.type);
              const displayName = selectedEntity.value || (selectedEntity as any).name || 'Entity';

              // Determine precise evidentiary verification status
              const srcList = selectedEntity.sources || [];
              const isOnlySearchQuery = srcList.length === 1 && (srcList[0] === 'search_query' || srcList[0] === 'seed_input');
              const isGraphLead = srcList.includes('relationship_graph') || Boolean((selectedEntity.metadata as any)?.is_graph_lead);
              const isSeedTarget = Boolean((selectedEntity.metadata as any)?.is_search_target) || Boolean((selectedEntity.metadata as any)?.is_seed_input);
              const verificationStatus = (selectedEntity.metadata as any)?.verification_status;

              let statusLabel = 'Confidence Unassessed';
              let statusVariant: 'outline' | 'mono' | 'success' | 'warning' = 'mono';

              if (isOnlySearchQuery || isSeedTarget || verificationStatus === 'UNASSESSED') {
                statusLabel = 'Unassessed Seed Input';
                statusVariant = 'warning';
              } else if (isGraphLead) {
                statusLabel = 'Uncorroborated Graph Lead';
                statusVariant = 'mono';
              } else if (selectedEntity.confidence != null && selectedEntity.confidence > 0) {
                const pct = Math.round(selectedEntity.confidence * 100);
                if (srcList.some((s: string) => s.toLowerCase().includes('registry') || s.toLowerCase().includes('itu') || s.toLowerCase().includes('telecom') || s.toLowerCase().includes('database'))) {
                  statusLabel = `Registry Corroborated (${pct}%)`;
                  statusVariant = 'success';
                } else if (pct >= 85) {
                  statusLabel = `High Confidence (${pct}%)`;
                  statusVariant = 'success';
                } else {
                  statusLabel = `Corroborated (${pct}%)`;
                  statusVariant = 'mono';
                }
              } else {
                statusLabel = 'Confidence Not Assessed';
                statusVariant = 'mono';
              }

              return (
                <div className="space-y-4 text-xs">
                  <div className="flex items-center justify-between pb-2 border-b border-slate-100 dark:border-slate-800">
                    <div className="flex items-center gap-2">
                      <Info className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                      <h3 className="font-mono font-bold text-slate-900 dark:text-white uppercase tracking-wider text-xs">
                        Entity Dossier
                      </h3>
                    </div>
                    <button
                      type="button"
                      onClick={() => setInspectorOpen(false)}
                      className="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-xs cursor-pointer"
                      title="Close Inspector"
                    >
                      ✕
                    </button>
                  </div>

                  {/* Header Title & Classification */}
                  <div className="space-y-1">
                    <span className="text-slate-400 uppercase text-[10px] block font-mono">Entity Identifier</span>
                    <p className="font-bold text-slate-900 dark:text-white text-sm font-sans break-words leading-tight">
                      {displayName}
                    </p>
                    <div className="flex flex-wrap items-center gap-1.5 pt-1">
                      <Badge variant="outline" className="font-mono text-[10px] uppercase">
                        {category}
                      </Badge>
                      <Badge variant={statusVariant} className="font-mono text-[10px]">
                        {statusLabel}
                      </Badge>
                    </div>
                  </div>

                  {/* Expansion Actions */}
                  <div className="flex items-center gap-2 pt-1">
                    <button
                      type="button"
                      onClick={handleExpand1Hop}
                      disabled={isExpanding}
                      className="flex-1 inline-flex items-center justify-center gap-1.5 py-2 px-3 rounded-xl bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-mono text-xs font-semibold transition-colors cursor-pointer shadow-xs"
                      title="Expand verified 1-hop relationships"
                    >
                      {isExpanding ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Maximize2 className="w-3.5 h-3.5" />}
                      <span>Expand 1-Hop</span>
                    </button>

                    <button
                      type="button"
                      onClick={handleCollapseBranch}
                      disabled={!hasActiveBranch}
                      className="inline-flex items-center justify-center gap-1.5 py-2 px-3 rounded-xl border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 disabled:opacity-30 text-slate-700 dark:text-slate-300 font-mono text-xs font-medium transition-colors cursor-pointer"
                      title="Collapse expanded branch"
                    >
                      <Minimize2 className="w-3.5 h-3.5" />
                      <span>Collapse</span>
                    </button>
                  </div>

                  {/* Feedback Banner */}
                  {feedback && (
                    <div
                      className={`p-2.5 rounded-xl border text-[11px] font-mono ${
                        feedback.type === 'success'
                          ? 'bg-emerald-50 text-emerald-800 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800'
                          : feedback.type === 'error'
                          ? 'bg-rose-50 text-rose-800 border-rose-200 dark:bg-rose-950/40 dark:text-rose-300 dark:border-rose-800'
                          : 'bg-slate-50 text-slate-700 border-slate-200 dark:bg-slate-900 dark:text-slate-300 dark:border-slate-800'
                      }`}
                    >
                      {feedback.message}
                    </div>
                  )}

                  {/* Correlated Sources */}
                  {selectedEntity.sources && selectedEntity.sources.length > 0 && (
                    <div className="space-y-1.5">
                      <span className="text-slate-400 uppercase text-[10px] block font-mono">Provenance & Sources</span>
                      <div className="flex flex-wrap gap-1">
                        {selectedEntity.sources.map((src: string, i: number) => (
                          <span
                            key={i}
                            className="text-[10px] font-mono px-2 py-0.5 rounded-lg bg-slate-100 text-slate-700 border border-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700"
                          >
                            {src}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Telemetry Attributes */}
                  {selectedEntity.metadata && Object.keys(selectedEntity.metadata).length > 0 && (
                    <div className="space-y-1.5 pt-2 border-t border-slate-100 dark:border-slate-800">
                      <span className="text-slate-400 uppercase text-[10px] block font-mono">Verified Attributes</span>
                      <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5 font-mono text-[11px] dark:bg-slate-900 dark:border-slate-800 max-h-48 overflow-y-auto">
                        {Object.entries(selectedEntity.metadata)
                          .filter(([_, v]) => v !== null && v !== undefined && v !== '')
                          .map(([k, v]) => (
                            <div key={k} className="flex justify-between gap-2 border-b border-slate-100 dark:border-slate-800 pb-1 last:border-0 last:pb-0">
                              <span className="text-slate-400 shrink-0">{k}:</span>
                              <span className="text-slate-700 dark:text-slate-300 font-semibold truncate text-right">
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
              <div className="text-center py-12 space-y-2 text-slate-400">
                <Network className="w-8 h-8 mx-auto opacity-40 text-indigo-500" />
                <p className="text-xs font-mono">Select any node or connection on the canvas to inspect provenance.</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Unlinked Intelligence Entities Drawer */}
      {unlinkedDrawerOpen && (
        <div className="p-4 rounded-2xl border border-amber-200 dark:border-amber-900/60 bg-amber-50/40 dark:bg-amber-950/20 space-y-3 animate-in fade-in duration-200">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-amber-200/60 dark:border-amber-900/40 pb-3">
            <div className="space-y-0.5">
              <div className="flex items-center gap-2">
                <Layers className="w-4 h-4 text-amber-600 dark:text-amber-400" />
                <h4 className="font-mono font-bold text-xs text-slate-900 dark:text-white uppercase tracking-wider">
                  Isolated Intelligence Identifiers ({unlinkedEntitiesList.length})
                </h4>
              </div>
              <p className="text-[11px] text-slate-500 dark:text-slate-400">
                Discovered indicators awaiting direct relationship correlation. Click to inspect or pin to the active link analysis canvas.
              </p>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="text"
                placeholder="Filter unlinked..."
                value={unlinkedSearch}
                onChange={(e) => setUnlinkedSearch(e.target.value)}
                className="h-7 px-2.5 rounded-lg bg-white border border-amber-300 text-xs font-mono text-slate-800 dark:bg-slate-900 dark:border-slate-800 dark:text-slate-200 w-36 shadow-xs"
              />
              <button
                type="button"
                onClick={() => setUnlinkedDrawerOpen(false)}
                className="text-xs text-amber-800 dark:text-amber-300 hover:underline font-mono cursor-pointer"
              >
                Close Drawer
              </button>
            </div>
          </div>

          {/* Cards Grid of Unlinked Entities */}
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-2.5 max-h-56 overflow-y-auto pr-1">
            {filteredUnlinkedTray.map((ent, idx) => {
              const val = ent.value || (ent as any).name || ent.id || '';
              const cat = getEntityCategory(ent.type);
              const avatar = extractEntityAvatar(ent);
              const isPinned = userPinnedEntities.some((p) => (p.value || p.id) === (ent.value || ent.id));

              return (
                <div
                  key={idx}
                  className="p-2.5 rounded-xl bg-white dark:bg-slate-900 border border-amber-200/80 dark:border-amber-900/40 flex items-center justify-between gap-2 shadow-2xs hover:border-amber-400 transition-colors"
                >
                  <div className="flex items-center gap-2 truncate">
                    <div
                      className="w-7 h-7 rounded-full flex items-center justify-center shrink-0 border"
                      style={{
                        backgroundColor: CATEGORY_COLORS[cat]?.bg || '#64748b',
                        borderColor: CATEGORY_COLORS[cat]?.border || '#475569',
                      }}
                    >
                      {avatar ? (
                        <img src={avatar} alt="" className="w-full h-full rounded-full object-cover" />
                      ) : (
                        <span className="text-[10px] text-white font-bold">{cat.slice(0, 1)}</span>
                      )}
                    </div>
                    <div className="truncate">
                      <p className="font-mono text-xs font-semibold text-slate-800 dark:text-slate-200 truncate">
                        {val}
                      </p>
                      <span className="text-[9px] font-mono text-slate-400 uppercase">{ent.type}</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-1 shrink-0">
                    <button
                      type="button"
                      onClick={() => {
                        setSelectedEntity(ent);
                        setSelectedEdgeData(null);
                        setInspectorOpen(true);
                      }}
                      className="p-1 rounded text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 cursor-pointer"
                      title="Inspect Entity Details"
                    >
                      <Info className="w-3.5 h-3.5" />
                    </button>
                    <button
                      type="button"
                      onClick={() => handlePinUnlinkedEntity(ent)}
                      disabled={isPinned}
                      className={`p-1 rounded cursor-pointer ${
                        isPinned
                          ? 'text-emerald-500'
                          : 'text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400'
                      }`}
                      title={isPinned ? 'Already Pinned to Graph' : 'Pin to Graph Canvas'}
                    >
                      <Pin className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default GraphStudioComponent;

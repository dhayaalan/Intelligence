import React, { useState, useMemo, useCallback, useRef } from 'react';
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
  ReactFlowInstance,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Entity, Relationship } from '../../types';
import { Badge } from '../../components/ui/Badge';
import { apiRequest } from '../../core/api/client';
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
  Maximize2,
  Minimize2,
  Loader2,
  Link2,
  Focus,
  GitFork,
  Radio,
  Eye,
  EyeOff,
  ChevronRight,
  ChevronLeft,
  Share2,
  Compass,
} from 'lucide-react';

interface Props {
  investigationId?: string;
  entities: Entity[];
  relationships?: Relationship[];
  onRunSearch?: () => void;
  isSearching?: boolean;
}

export type LayoutMode = 'FOCUS' | 'RADIAL' | 'NETWORK' | 'HIERARCHY';

export const getEntityCategory = (type: string = ''): string => {
  const t = type.toUpperCase();
  if (['PERSON', 'THREAT_ACTOR', 'USERNAME', 'AUTHOR', 'ACTOR'].includes(t)) return 'PERSON';
  if (['ORGANIZATION', 'ORG', 'COMPANY', 'GROUP', 'NGO', 'FOUNDATION', 'TERROR_GROUP', 'GOVERNMENT'].includes(t)) return 'ORGANIZATION';
  if (['VULNERABILITY', 'CVE', 'THREAT_INDICATOR', 'MALWARE', 'THREAT'].includes(t)) return 'THREAT_INDICATOR';
  if (['IP', 'IPV4', 'IPV6'].includes(t)) return 'IP';
  if (['HASH', 'SHA256', 'MD5'].includes(t)) return 'HASH';
  if (['EMAIL'].includes(t)) return 'EMAIL';
  if (['URL', 'DOCUMENT', 'ARTICLE', 'NEWS'].includes(t)) return 'DOCUMENT';
  return 'DOMAIN';
};

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
      return `https://unavatar.io/${handle}`;
    }
  }

  if (ent.type?.toUpperCase() === 'USERNAME' || ent.type?.toUpperCase() === 'PERSON') {
    const clean = val.replace(/^@/, '').trim();
    if (clean) {
      if (platform.includes('twitter') || platform.includes('x.com') || platform === 'x') return `https://unavatar.io/x/${clean}`;
      if (platform.includes('youtube')) return `https://unavatar.io/youtube/${clean}`;
      if (platform.includes('github')) return `https://github.com/${clean}.png`;
    }
  }

  return null;
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

const getCategoryStyles = (category: string) => {
  switch (category) {
    case 'PERSON':
      return {
        iconBg: 'bg-amber-100 text-amber-700 dark:bg-amber-950/80 dark:text-amber-300',
        dot: 'bg-amber-500',
        border: 'hover:border-amber-400',
      };
    case 'ORGANIZATION':
      return {
        iconBg: 'bg-indigo-100 text-indigo-700 dark:bg-indigo-950/80 dark:text-indigo-300',
        dot: 'bg-indigo-500',
        border: 'hover:border-indigo-400',
      };
    case 'THREAT_INDICATOR':
      return {
        iconBg: 'bg-rose-100 text-rose-700 dark:bg-rose-950/80 dark:text-rose-300',
        dot: 'bg-rose-500',
        border: 'hover:border-rose-400',
      };
    case 'IP':
      return {
        iconBg: 'bg-blue-100 text-blue-700 dark:bg-blue-950/80 dark:text-blue-300',
        dot: 'bg-blue-500',
        border: 'hover:border-blue-400',
      };
    case 'EMAIL':
      return {
        iconBg: 'bg-teal-100 text-teal-700 dark:bg-teal-950/80 dark:text-teal-300',
        dot: 'bg-teal-500',
        border: 'hover:border-teal-400',
      };
    case 'DOCUMENT':
      return {
        iconBg: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950/80 dark:text-emerald-300',
        dot: 'bg-emerald-500',
        border: 'hover:border-emerald-400',
      };
    case 'DOMAIN':
    default:
      return {
        iconBg: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300',
        dot: 'bg-slate-500',
        border: 'hover:border-slate-400',
      };
  }
};

// =============================================================================
// COMPACT NODE COMPONENT (Clean, Uncluttered OSINT Graph Standard)
// =============================================================================
const CompactGraphNode: React.FC<NodeProps> = ({ data, selected }) => {
  const category = getEntityCategory(data.type);
  const Icon = getEntityCategoryIcon(category);
  const styles = getCategoryStyles(category);
  const isRoot = Boolean(data.isRoot || data.is_seed);
  const displayName = data.value || data.name || 'Unknown Entity';

  return (
    <div
      className={`group relative flex items-center gap-2 px-2.5 py-1.5 rounded-full border transition-all duration-150 select-none cursor-pointer bg-white dark:bg-[#0f1422] shadow-2xs max-w-[200px] ${
        selected
          ? 'border-indigo-600 ring-2 ring-indigo-500/40 dark:border-indigo-400 shadow-md scale-105 z-20'
          : isRoot
          ? 'border-indigo-500 ring-2 ring-indigo-500/20 shadow-xs'
          : 'border-slate-200 dark:border-slate-800 hover:border-slate-400 dark:hover:border-slate-600'
      }`}
      title={`${displayName} (${category})`}
    >
      {/* 4 Multi-directional handles */}
      <Handle type="target" position={Position.Top} className="!w-2 !h-2 !bg-indigo-500 !border-white dark:!border-slate-900" />
      <Handle type="target" position={Position.Left} id="left" className="!w-1.5 !h-1.5 !bg-indigo-400 !border-white dark:!border-slate-900" />

      {/* Semantic Icon Badge */}
      <div className={`w-6 h-6 rounded-full flex items-center justify-center shrink-0 ${styles.iconBg}`}>
        <Icon className="w-3.5 h-3.5" />
      </div>

      {/* Truncated Short Label */}
      <div className="min-w-0 flex-1 pr-1">
        <p className="text-xs font-semibold text-slate-900 dark:text-slate-100 truncate leading-tight">
          {displayName}
        </p>
        <div className="flex items-center gap-1 mt-0.5">
          <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${styles.dot}`} />
          <span className="text-[9px] font-mono uppercase tracking-wider text-slate-400 truncate">
            {isRoot ? '★ ROOT' : category}
          </span>
        </div>
      </div>

      <Handle type="source" position={Position.Bottom} className="!w-2 !h-2 !bg-indigo-500 !border-white dark:!border-slate-900" />
      <Handle type="source" position={Position.Right} id="right" className="!w-1.5 !h-1.5 !bg-indigo-400 !border-white dark:!border-slate-900" />
    </div>
  );
};

const nodeTypes = {
  compactNode: CompactGraphNode,
};

export const getEdgeStyle = (relType: string) => {
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
  return { stroke: '#64748b', color: '#64748b', labelBg: '#f8fafc', labelStroke: '#cbd5e1' };
};

export const GraphStudioComponent: React.FC<Props> = ({
  investigationId,
  entities = [],
  relationships = [],
  onRunSearch,
  isSearching,
}) => {
  const [filterCategory, setFilterCategory] = useState<string>('ALL');
  const [layoutMode, setLayoutMode] = useState<LayoutMode>('FOCUS');
  const [searchFilter, setSearchFilter] = useState<string>('');
  const [showUnlinked, setShowUnlinked] = useState<boolean>(false);
  const [showMinimap, setShowMinimap] = useState<boolean>(false);
  const [inspectorOpen, setInspectorOpen] = useState<boolean>(true);
  const [selectedEntity, setSelectedEntity] = useState<Entity | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<Edge | null>(null);
  const [expandedBranches, setExpandedBranches] = useState<Record<string, { nodeIds: string[]; edgeIds: string[] }>>({});
  const [isExpanding, setIsExpanding] = useState<boolean>(false);
  const [expansionFeedback, setExpansionFeedback] = useState<{ message: string; type: 'info' | 'success' | 'warning' | 'error' } | null>(null);
  const reactFlowInstanceRef = useRef<ReactFlowInstance | null>(null);

  // 1. Identify Connected Components and Node Degrees
  const { connectedNodeKeys, nodeDegrees, rootEntityCandidate } = useMemo(() => {
    const degrees: Record<string, number> = {};
    const connected = new Set<string>();

    (relationships || []).forEach((rel) => {
      const src = (rel.source_entity_value || (rel as any).source_id || '').toLowerCase().trim();
      const tgt = (rel.target_entity_value || (rel as any).target_id || '').toLowerCase().trim();
      if (src && tgt && src !== tgt) {
        connected.add(src);
        connected.add(tgt);
        degrees[src] = (degrees[src] || 0) + 1;
        degrees[tgt] = (degrees[tgt] || 0) + 1;
      }
    });

    // Find candidate root: entity with highest degree or first connected entity
    let maxDeg = -1;
    let candidate: Entity | null = null;
    entities.forEach((ent) => {
      const val = (ent.value || (ent as any).name || ent.id || '').toLowerCase().trim();
      const deg = degrees[val] || 0;
      if (deg > maxDeg) {
        maxDeg = deg;
        candidate = ent;
      }
    });

    return {
      connectedNodeKeys: connected,
      nodeDegrees: degrees,
      rootEntityCandidate: candidate || entities[0] || null,
    };
  }, [entities, relationships]);

  // Set initial selected entity to root candidate
  React.useEffect(() => {
    if (!selectedEntity && rootEntityCandidate) {
      setSelectedEntity(rootEntityCandidate);
    }
  }, [rootEntityCandidate, selectedEntity]);

  // 2. Filter entities: By default, Main Graph displays Connected Entities
  const { visibleEntities, unlinkedCount } = useMemo(() => {
    let unlinked = 0;
    const filtered: Entity[] = [];

    entities.forEach((ent) => {
      const val = (ent.value || (ent as any).name || ent.id || '').toLowerCase().trim();
      const isConnected = connectedNodeKeys.has(val);

      if (!isConnected) {
        unlinked += 1;
      }

      // Check category filter
      if (filterCategory !== 'ALL' && getEntityCategory(ent.type) !== filterCategory) {
        return;
      }

      // Check text search
      if (searchFilter.trim()) {
        const q = searchFilter.toLowerCase();
        const matches =
          (ent.value || '').toLowerCase().includes(q) ||
          ((ent as any).name || '').toLowerCase().includes(q) ||
          (ent.type || '').toLowerCase().includes(q);
        if (!matches) return;
      }

      // If showUnlinked is false, exclude unlinked entities from main view
      if (!showUnlinked && !isConnected) {
        return;
      }

      filtered.push(ent);
    });

    return { visibleEntities: filtered, unlinkedCount: unlinked };
  }, [entities, connectedNodeKeys, filterCategory, searchFilter, showUnlinked]);

  // 3. Layout Generation based on actual graph structure
  const initialNodes: Node[] = useMemo(() => {
    if (visibleEntities.length === 0) return [];

    const nodesResult: Node[] = [];
    const rootVal = (selectedEntity?.value || selectedEntity?.id || rootEntityCandidate?.value || '').toLowerCase().trim();

    // Map for fast lookups
    const entKey = (e: Entity) => (e.value || (e as any).name || e.id || '').toLowerCase().trim();

    // FOCUS LAYOUT (Default: Central seed + bounded concentric neighbors)
    if (layoutMode === 'FOCUS') {
      const centerX = 500;
      const centerY = 350;

      // Group neighbors: 1-hop directly connected to selected entity
      const directNeighbors: Entity[] = [];
      const outerEntities: Entity[] = [];
      let rootNodeAdded = false;

      visibleEntities.forEach((ent) => {
        const key = entKey(ent);
        if (key === rootVal) {
          nodesResult.push({
            id: ent.id || `node-${key}`,
            type: 'compactNode',
            position: { x: centerX - 80, y: centerY - 20 },
            data: { ...ent, isRoot: true },
          });
          rootNodeAdded = true;
          return;
        }

        // Check if directly connected to root
        const isDirect = (relationships || []).some((r) => {
          const s = (r.source_entity_value || (r as any).source_id || '').toLowerCase().trim();
          const t = (r.target_entity_value || (r as any).target_id || '').toLowerCase().trim();
          return (s === rootVal && t === key) || (t === rootVal && s === key);
        });

        if (isDirect) {
          directNeighbors.push(ent);
        } else {
          outerEntities.push(ent);
        }
      });

      // If root wasn't in visibleEntities, pick the first entity
      if (!rootNodeAdded && visibleEntities.length > 0) {
        const first = visibleEntities[0];
        nodesResult.push({
          id: first.id || `node-${entKey(first)}`,
          type: 'compactNode',
          position: { x: centerX - 80, y: centerY - 20 },
          data: { ...first, isRoot: true },
        });
      }

      // Arrange 1-hop neighbors in inner ring (radius 220)
      const innerRadius = 220;
      const innerCount = directNeighbors.length;
      directNeighbors.forEach((ent, idx) => {
        const angle = (idx / Math.max(1, innerCount)) * 2 * Math.PI;
        const x = Math.round(centerX + Math.cos(angle) * innerRadius - 80);
        const y = Math.round(centerY + Math.sin(angle) * innerRadius - 20);
        nodesResult.push({
          id: ent.id || `node-${entKey(ent)}`,
          type: 'compactNode',
          position: { x, y },
          data: ent,
        });
      });

      // Arrange outer entities in orbit ring (radius 380)
      const outerRadius = 380;
      const outerCount = outerEntities.length;
      outerEntities.forEach((ent, idx) => {
        const angle = (idx / Math.max(1, outerCount)) * 2 * Math.PI + 0.2;
        const x = Math.round(centerX + Math.cos(angle) * outerRadius - 80);
        const y = Math.round(centerY + Math.sin(angle) * outerRadius - 20);
        nodesResult.push({
          id: ent.id || `node-${entKey(ent)}`,
          type: 'compactNode',
          position: { x, y },
          data: ent,
        });
      });
    } else if (layoutMode === 'RADIAL') {
      const centerX = 500;
      const centerY = 350;

      visibleEntities.forEach((ent, idx) => {
        const key = entKey(ent);
        if (idx === 0) {
          nodesResult.push({
            id: ent.id || `node-${key}`,
            type: 'compactNode',
            position: { x: centerX - 80, y: centerY - 20 },
            data: { ...ent, isRoot: true },
          });
          return;
        }

        const ring = Math.floor((idx - 1) / 8);
        const posInRing = (idx - 1) % 8;
        const ringTotal = Math.min(8, visibleEntities.length - 1 - ring * 8);
        const radius = 200 + ring * 180;
        const angle = (posInRing / Math.max(1, ringTotal)) * 2 * Math.PI;

        const x = Math.round(centerX + Math.cos(angle) * radius - 80);
        const y = Math.round(centerY + Math.sin(angle) * radius - 20);

        nodesResult.push({
          id: ent.id || `node-${key}`,
          type: 'compactNode',
          position: { x, y },
          data: ent,
        });
      });
    } else if (layoutMode === 'HIERARCHY') {
      // Top-to-bottom directional tiers based on category role
      const tiers: Record<number, Entity[]> = { 1: [], 2: [], 3: [], 4: [] };
      visibleEntities.forEach((ent) => {
        const cat = getEntityCategory(ent.type);
        if (cat === 'ORGANIZATION') tiers[1].push(ent);
        else if (cat === 'PERSON') tiers[2].push(ent);
        else if (['THREAT_INDICATOR', 'IP'].includes(cat)) tiers[3].push(ent);
        else tiers[4].push(ent);
      });

      const tierY = { 1: 60, 2: 220, 3: 380, 4: 540 };
      const colWidth = 220;

      Object.entries(tiers).forEach(([tStr, list]) => {
        const tNum = Number(tStr) as 1 | 2 | 3 | 4;
        const y = tierY[tNum];
        const count = list.length;
        const totalW = count * colWidth;
        const startX = Math.max(60, 500 - totalW / 2);

        list.forEach((ent, i) => {
          const x = Math.round(startX + i * colWidth);
          nodesResult.push({
            id: ent.id || `node-${entKey(ent)}`,
            type: 'compactNode',
            position: { x, y },
            data: ent,
          });
        });
      });
    } else {
      // NETWORK / FORCE-DIRECTED SIMULATION
      const cols = Math.ceil(Math.sqrt(visibleEntities.length * 1.5));
      visibleEntities.forEach((ent, idx) => {
        const row = Math.floor(idx / cols);
        const col = idx % cols;
        const x = 80 + col * 240 + (row % 2 === 1 ? 50 : 0);
        const y = 80 + row * 160;
        nodesResult.push({
          id: ent.id || `node-${entKey(ent)}`,
          type: 'compactNode',
          position: { x, y },
          data: ent,
        });
      });
    }

    return nodesResult;
  }, [visibleEntities, layoutMode, selectedEntity, rootEntityCandidate, relationships]);

  // 4. Edges generation
  const initialEdges: Edge[] = useMemo(() => {
    if (visibleEntities.length <= 1 || !relationships || relationships.length === 0) return [];

    const entityValueMap = new Map<string, string>();
    visibleEntities.forEach((ent) => {
      const entId = ent.id || `node-${(ent.value || (ent as any).name || '').toLowerCase().trim()}`;
      if (ent.value) entityValueMap.set(ent.value.toLowerCase().trim(), entId);
      if ((ent as any).name) entityValueMap.set((ent as any).name.toLowerCase().trim(), entId);
      if (ent.id) entityValueMap.set(ent.id.toLowerCase().trim(), entId);
    });

    const edgesResult: Edge[] = [];
    const seenEdges = new Set<string>();

    relationships.forEach((rel, rIdx) => {
      const srcVal = (rel.source_entity_value || (rel as any).source_id || '').toLowerCase().trim();
      const tgtVal = (rel.target_entity_value || (rel as any).target_id || '').toLowerCase().trim();
      const srcId = entityValueMap.get(srcVal);
      const tgtId = entityValueMap.get(tgtVal);

      if (srcId && tgtId && srcId !== tgtId) {
        const edgeKey = `${srcId}-${tgtId}`;
        if (!seenEdges.has(edgeKey)) {
          seenEdges.add(edgeKey);
          const style = getEdgeStyle(rel.relationship_type);
          const labelText = (rel.relationship_type || 'CONNECTED').replace(/_/g, ' ').toLowerCase();
          const isInferred = Boolean(rel.metadata?.is_inferred || rel.metadata?.basis === 'INFERRED' || (rel as any).is_inferred);

          edgesResult.push({
            id: (rel as any).id || `edge-${rIdx}-${srcId}-${tgtId}`,
            source: srcId,
            target: tgtId,
            label: labelText,
            type: 'smoothstep',
            data: rel,
            markerEnd: {
              type: MarkerType.ArrowClosed,
              width: 12,
              height: 12,
              color: style.color,
            },
            style: {
              stroke: style.stroke,
              strokeWidth: 1.8,
              strokeDasharray: isInferred ? '5,4' : undefined,
            },
            labelStyle: {
              fill: '#334155',
              fontWeight: 600,
              fontSize: 9,
              fontFamily: 'monospace',
            },
            labelBgStyle: {
              fill: style.labelBg,
              stroke: style.labelStroke,
              strokeWidth: 1,
              rx: 4,
              ry: 4,
            },
            labelBgPadding: [4, 2],
          });
        }
      }
    });

    return edgesResult;
  }, [visibleEntities, relationships]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  React.useEffect(() => {
    setNodes(initialNodes);
    setEdges(initialEdges);
  }, [initialNodes, initialEdges]);

  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      setSelectedEdge(null);
      const found = entities.find(
        (e) => (e.id || `node-${(e.value || (e as any).name || '').toLowerCase().trim()}`) === node.id || e.value === node.data?.value
      ) || node.data;
      if (found) {
        setSelectedEntity(found);
        setInspectorOpen(true);
      }
    },
    [entities]
  );

  const onEdgeClick = useCallback(
    (_: React.MouseEvent, edge: Edge) => {
      setSelectedEdge(edge);
      setSelectedEntity(null);
      setInspectorOpen(true);
    },
    []
  );

  // 1-Hop Graph Expansion
  const handleExpand1Hop = async () => {
    if (!selectedEntity || isExpanding) return;
    setIsExpanding(true);
    setExpansionFeedback(null);
    try {
      const entVal = selectedEntity.value || (selectedEntity as any).name || selectedEntity.id;
      const res = await apiRequest<any>(
        `/graph/expand?entity_id=${encodeURIComponent(entVal)}${investigationId ? `&investigation_id=${encodeURIComponent(investigationId)}` : ''}&limit=25`
      );
      const incomingEdges = res.edges || [];
      const incomingNodes = res.nodes || [];

      if (incomingEdges.length === 0) {
        setExpansionFeedback({
          message: `No further verified relationships discovered for '${entVal}'.`,
          type: 'info',
        });
        return;
      }

      const currentNodes = [...nodes];
      const currentEdges = [...edges];
      const existingNodeIds = new Set(currentNodes.map((n) => n.id));
      const existingEdgeIds = new Set(currentEdges.map((e) => e.id));

      const parentNode = currentNodes.find(
        (n) => n.id === selectedEntity.id || n.data?.value === entVal
      );
      const parentPos = parentNode ? parentNode.position : { x: 500, y: 350 };

      const newNodeIds: string[] = [];
      const newEdgeIds: string[] = [];
      const radius = 200;
      const angleStep = (2 * Math.PI) / Math.max(1, incomingNodes.length);

      incomingNodes.forEach((nDoc: any, i: number) => {
        const nId = nDoc.id || `node-${(nDoc.value || '').toLowerCase().trim()}`;
        if (!existingNodeIds.has(nId)) {
          const angle = i * angleStep;
          const pos = {
            x: Math.round(parentPos.x + radius * Math.cos(angle)),
            y: Math.round(parentPos.y + radius * Math.sin(angle)),
          };
          currentNodes.push({
            id: nId,
            type: 'compactNode',
            position: pos,
            data: nDoc,
          });
          existingNodeIds.add(nId);
          newNodeIds.push(nId);
        }
      });

      incomingEdges.forEach((r: any) => {
        const edgeId = r.id || `e-${r.source_id || r.source_entity_value}-${r.target_id || r.target_entity_value}`;
        if (!existingEdgeIds.has(edgeId)) {
          const srcId = r.source_id || `node-${(r.source_entity_value || '').toLowerCase().trim()}`;
          const tgtId = r.target_id || `node-${(r.target_entity_value || '').toLowerCase().trim()}`;
          const relLabel = (r.relationship_type || r.type || 'connected').replace(/_/g, ' ').toLowerCase();
          const style = getEdgeStyle(relLabel);
          const isInferred = Boolean(r.is_inferred || r.basis === 'INFERRED');

          currentEdges.push({
            id: edgeId,
            source: srcId,
            target: tgtId,
            label: relLabel,
            type: 'smoothstep',
            data: r,
            markerEnd: {
              type: MarkerType.ArrowClosed,
              width: 12,
              height: 12,
              color: style.color,
            },
            style: {
              stroke: style.stroke,
              strokeWidth: 1.8,
              strokeDasharray: isInferred ? '5,4' : undefined,
            },
            labelStyle: {
              fill: '#334155',
              fontWeight: 600,
              fontSize: 9,
              fontFamily: 'monospace',
            },
            labelBgStyle: {
              fill: style.labelBg,
              stroke: style.labelStroke,
              strokeWidth: 1,
              rx: 4,
              ry: 4,
            },
            labelBgPadding: [4, 2],
          });
          existingEdgeIds.add(edgeId);
          newEdgeIds.push(edgeId);
        }
      });

      setNodes(currentNodes);
      setEdges(currentEdges);
      const branchKey = selectedEntity.id || entVal;
      setExpandedBranches((prev) => ({
        ...prev,
        [branchKey]: { nodeIds: newNodeIds, edgeIds: newEdgeIds },
      }));
      setExpansionFeedback({
        message: `Expanded ${newNodeIds.length} entities and ${newEdgeIds.length} verified connections.`,
        type: 'success',
      });
    } catch (err: any) {
      setExpansionFeedback({
        message: `Expansion failed: ${err.message || 'Server error'}. Retry available.`,
        type: 'error',
      });
    } finally {
      setIsExpanding(false);
    }
  };

  // Branch Collapse: Preserves Shared Nodes
  const handleCollapseBranch = () => {
    if (!selectedEntity) return;
    const branchKey = selectedEntity.id || selectedEntity.value || (selectedEntity as any).name;
    const branchData = expandedBranches[branchKey];
    if (!branchData) return;

    // Identify shared nodes across other expanded branches
    const otherBranchNodeIds = new Set<string>();
    Object.entries(expandedBranches).forEach(([bKey, data]) => {
      if (bKey !== branchKey) {
        data.nodeIds.forEach((id) => otherBranchNodeIds.add(id));
      }
    });

    const initialNodeIds = new Set(initialNodes.map((n) => n.id));
    const nodesToRemove = new Set(
      branchData.nodeIds.filter((nid) => !otherBranchNodeIds.has(nid) && !initialNodeIds.has(nid))
    );
    const edgesToRemove = new Set(branchData.edgeIds);

    setNodes((prev) => prev.filter((n) => !nodesToRemove.has(n.id)));
    setEdges((prev) => prev.filter((e) => !edgesToRemove.has(e.id)));
    setExpandedBranches((prev) => {
      const next = { ...prev };
      delete next[branchKey];
      return next;
    });
    setExpansionFeedback({
      message: `Branch collapsed successfully. Shared entities preserved.`,
      type: 'info',
    });
  };

  const handleFitView = () => {
    if (reactFlowInstanceRef.current) {
      reactFlowInstanceRef.current.fitView({ padding: 0.2, duration: 400 });
    }
  };

  if (entities.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-slate-300 dark:border-slate-800 bg-white dark:bg-slate-900/40 p-12 text-center space-y-4">
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
    <div className="space-y-3">
      {/* Clean, Streamlined Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-3 rounded-xl border border-slate-200 bg-white shadow-2xs dark:border-slate-800 dark:bg-[#0f1422] text-xs">
        <div className="flex flex-wrap items-center gap-2">
          {/* Layout Mode Selector */}
          <div className="flex items-center gap-0.5 bg-slate-100 dark:bg-slate-800 p-0.5 rounded-lg">
            <button
              type="button"
              onClick={() => setLayoutMode('FOCUS')}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-mono font-medium transition-colors ${
                layoutMode === 'FOCUS'
                  ? 'bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-2xs font-semibold'
                  : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
              }`}
              title="Focus: Selected entity and bounded connections"
            >
              <Focus className="w-3.5 h-3.5" />
              <span>Focus</span>
            </button>
            <button
              type="button"
              onClick={() => setLayoutMode('RADIAL')}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-mono font-medium transition-colors ${
                layoutMode === 'RADIAL'
                  ? 'bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-2xs font-semibold'
                  : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
              }`}
              title="Radial: Concentric rings around center"
            >
              <Radio className="w-3.5 h-3.5" />
              <span>Radial</span>
            </button>
            <button
              type="button"
              onClick={() => setLayoutMode('NETWORK')}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-mono font-medium transition-colors ${
                layoutMode === 'NETWORK'
                  ? 'bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-2xs font-semibold'
                  : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
              }`}
              title="Network: Connected graph topology"
            >
              <Share2 className="w-3.5 h-3.5" />
              <span>Network</span>
            </button>
            <button
              type="button"
              onClick={() => setLayoutMode('HIERARCHY')}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-mono font-medium transition-colors ${
                layoutMode === 'HIERARCHY'
                  ? 'bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-2xs font-semibold'
                  : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
              }`}
              title="Hierarchy: Directional parent-child tiers"
            >
              <GitFork className="w-3.5 h-3.5" />
              <span>Hierarchy</span>
            </button>
          </div>

          {/* Category Filter */}
          <div className="flex items-center gap-1">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="h-7 px-2 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-700 font-mono focus:border-indigo-500 dark:bg-slate-900 dark:border-slate-800 dark:text-slate-200"
            >
              <option value="ALL">All Types</option>
              <option value="ORGANIZATION">Organizations</option>
              <option value="PERSON">Persons / Actors</option>
              <option value="THREAT_INDICATOR">Threat Indicators</option>
              <option value="DOMAIN">Domains / URLs</option>
              <option value="IP">IP Addresses</option>
              <option value="EMAIL">Emails</option>
            </select>
          </div>

          {/* Toggle Unlinked Entities */}
          {unlinkedCount > 0 && (
            <button
              type="button"
              onClick={() => setShowUnlinked((prev) => !prev)}
              className={`flex items-center gap-1.5 h-7 px-2.5 rounded-lg border text-xs font-mono transition-colors ${
                showUnlinked
                  ? 'bg-indigo-50 border-indigo-200 text-indigo-700 dark:bg-indigo-950/60 dark:border-indigo-800 dark:text-indigo-300'
                  : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50 dark:bg-slate-900 dark:border-slate-800 dark:text-slate-300'
              }`}
              title="Toggle visibility of isolated entities with no mapped relationships"
            >
              {showUnlinked ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3 text-slate-400" />}
              <span>Unlinked ({unlinkedCount})</span>
            </button>
          )}
        </div>

        <div className="flex items-center gap-2">
          {/* In-Graph Search */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-2 text-slate-400" />
            <input
              type="text"
              placeholder="Find entity..."
              value={searchFilter}
              onChange={(e) => setSearchFilter(e.target.value)}
              className="h-7 pl-7 pr-2 rounded-lg bg-slate-50 border border-slate-200 text-xs font-mono text-slate-800 focus:outline-none focus:border-indigo-500 dark:bg-slate-900 dark:border-slate-800 dark:text-slate-200 w-36"
            />
          </div>

          {/* Canvas Stats Pill */}
          <div className="flex items-center gap-1.5 px-2 py-1 rounded-md bg-slate-100 dark:bg-slate-800 text-[11px] font-mono text-slate-600 dark:text-slate-300">
            <span>{nodes.length} nodes</span>
            <span className="text-slate-400">•</span>
            <span>{edges.length} edges</span>
          </div>

          {/* Fit View Action */}
          <button
            type="button"
            onClick={handleFitView}
            className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-600 dark:border-slate-800 dark:hover:bg-slate-800 dark:text-slate-300 transition-colors"
            title="Fit graph to viewport"
          >
            <Compass className="w-4 h-4" />
          </button>

          {/* Toggle Inspector */}
          <button
            type="button"
            onClick={() => setInspectorOpen((prev) => !prev)}
            className={`flex items-center gap-1 h-7 px-2 rounded-lg border text-xs font-mono transition-colors ${
              inspectorOpen
                ? 'bg-indigo-50 border-indigo-200 text-indigo-700 dark:bg-indigo-950/60 dark:border-indigo-800 dark:text-indigo-300'
                : 'border-slate-200 text-slate-600 hover:bg-slate-100 dark:border-slate-800 dark:text-slate-300'
            }`}
            title="Toggle Inspector Sidebar"
          >
            <Info className="w-3.5 h-3.5" />
            <span>Inspector</span>
          </button>
        </div>
      </div>

      {/* Main Canvas & Inspector Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-3 relative">
        {/* Canvas Area: Expands to 4 cols when inspector is closed */}
        <div
          className={`${
            inspectorOpen ? 'lg:col-span-3' : 'lg:col-span-4'
          } h-[680px] rounded-xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-[#090d16] relative overflow-hidden transition-all duration-200`}
        >
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={onNodeClick}
            onEdgeClick={onEdgeClick}
            nodeTypes={nodeTypes}
            onInit={(instance) => {
              reactFlowInstanceRef.current = instance;
            }}
            fitView
            minZoom={0.25}
            maxZoom={2.0}
            defaultEdgeOptions={{
              type: 'smoothstep',
            }}
          >
            <Background gap={28} size={1} color="#cbd5e1" className="opacity-40" />
            <Controls className="!bg-white dark:!bg-slate-900 !border !border-slate-200 dark:!border-slate-800 !rounded-lg !shadow-xs" />
            {showMinimap && (
              <MiniMap
                className="!bg-white dark:!bg-slate-900 !border !border-slate-200 dark:!border-slate-800 !rounded-lg !shadow-xs"
                nodeColor={(n) => {
                  const cat = getEntityCategory(n.data?.type);
                  if (cat === 'ORGANIZATION') return '#6366f1';
                  if (cat === 'PERSON') return '#f59e0b';
                  if (cat === 'THREAT_INDICATOR') return '#f43f5e';
                  if (cat === 'IP') return '#3b82f6';
                  return '#94a3b8';
                }}
              />
            )}
          </ReactFlow>

          {/* Minimap Toggle Floating Button */}
          <button
            type="button"
            onClick={() => setShowMinimap((prev) => !prev)}
            className="absolute bottom-3 right-3 px-2 py-1 rounded bg-white/90 dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 text-[10px] font-mono text-slate-600 dark:text-slate-300 shadow-2xs hover:bg-slate-50 transition-colors"
          >
            {showMinimap ? 'Hide Minimap' : 'Show Minimap'}
          </button>

          {/* Minimalist Legend Overlay */}
          <div className="absolute bottom-3 left-3 bg-white/95 dark:bg-slate-900/95 backdrop-blur-xs px-2.5 py-1.5 rounded-lg border border-slate-200 dark:border-slate-800 text-[10px] font-mono flex items-center gap-3 shadow-2xs select-none">
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-indigo-500 inline-block" />
              <span className="text-slate-600 dark:text-slate-400">Org</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-amber-500 inline-block" />
              <span className="text-slate-600 dark:text-slate-400">Person</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-rose-500 inline-block" />
              <span className="text-slate-600 dark:text-slate-400">Threat</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-blue-500 inline-block" />
              <span className="text-slate-600 dark:text-slate-400">IP</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-teal-500 inline-block" />
              <span className="text-slate-600 dark:text-slate-400">Email</span>
            </div>
          </div>
        </div>

        {/* Collapsible Right Inspector Panel */}
        {inspectorOpen && (
          <div className="lg:col-span-1 rounded-xl border border-slate-200 bg-white p-3.5 space-y-3.5 shadow-2xs dark:border-slate-800 dark:bg-[#0f1422] max-h-[680px] overflow-y-auto">
            {selectedEdge ? (
              /* Edge Inspector */
              <div className="space-y-3 text-xs">
                <div className="flex items-center justify-between pb-2 border-b border-slate-100 dark:border-slate-800">
                  <div className="flex items-center gap-1.5">
                    <Link2 className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                    <h3 className="font-mono font-bold text-slate-900 dark:text-white uppercase tracking-wider text-xs">
                      Relationship Provenance
                    </h3>
                  </div>
                  <button
                    type="button"
                    onClick={() => setSelectedEdge(null)}
                    className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-xs"
                  >
                    ✕
                  </button>
                </div>

                <div>
                  <span className="text-slate-400 uppercase text-[10px] block font-mono">Connection Type</span>
                  <p className="font-mono font-bold text-slate-900 dark:text-white mt-0.5 text-sm uppercase">
                    {selectedEdge.label || selectedEdge.data?.relationship_type || 'CONNECTED'}
                  </p>
                </div>

                <div className="p-2 rounded-lg bg-slate-50 border border-slate-200 dark:bg-slate-900/60 dark:border-slate-800 space-y-1 font-mono text-[11px]">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">From:</span>
                    <span className="font-semibold text-slate-800 dark:text-slate-200 truncate max-w-[130px]">
                      {selectedEdge.data?.source_entity_value || selectedEdge.source}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">To:</span>
                    <span className="font-semibold text-slate-800 dark:text-slate-200 truncate max-w-[130px]">
                      {selectedEdge.data?.target_entity_value || selectedEdge.target}
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-slate-500 font-mono text-xs">Evidence Basis</span>
                  <Badge
                    variant={selectedEdge.data?.basis === 'DIRECT_OBSERVATION' ? 'success' : 'warning'}
                    className="font-mono text-[10px] uppercase"
                  >
                    {selectedEdge.data?.basis || (selectedEdge.data?.is_inferred ? 'INFERRED' : 'DIRECT OBSERVATION')}
                  </Badge>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-slate-500 font-mono text-xs">Confidence</span>
                  <Badge variant="mono" className="font-mono text-[10px]">
                    {Math.round((selectedEdge.data?.confidence || 0.9) * 100)}%
                  </Badge>
                </div>

                {selectedEdge.data?.evidence_ids && selectedEdge.data.evidence_ids.length > 0 && (
                  <div className="space-y-1 pt-2 border-t border-slate-100 dark:border-slate-800">
                    <span className="text-slate-400 uppercase text-[10px] block font-mono">Supporting Evidence</span>
                    <div className="flex flex-wrap gap-1">
                      {selectedEdge.data.evidence_ids.map((evId: string, idx: number) => (
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

              return (
                <div className="space-y-3 text-xs">
                  <div className="flex items-center justify-between pb-2 border-b border-slate-100 dark:border-slate-800">
                    <div className="flex items-center gap-1.5">
                      <Info className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                      <h3 className="font-mono font-bold text-slate-900 dark:text-white uppercase tracking-wider text-xs">
                        Entity Inspector
                      </h3>
                    </div>
                    <button
                      type="button"
                      onClick={() => setInspectorOpen(false)}
                      className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-xs"
                      title="Close Inspector"
                    >
                      ✕
                    </button>
                  </div>

                  {/* Header Title & Classification */}
                  <div>
                    <span className="text-slate-400 uppercase text-[10px] block font-mono">Entity Identifier</span>
                    <p className="font-bold text-slate-900 dark:text-white mt-0.5 text-sm font-sans break-words">
                      {displayName}
                    </p>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge variant="outline" className="font-mono text-[10px] uppercase">
                        {category}
                      </Badge>
                      <Badge variant={(selectedEntity.confidence || 0) >= 0.85 ? 'success' : 'mono'} className="font-mono text-[10px]">
                        {Math.round((selectedEntity.confidence || 0.85) * 100)}% verified
                      </Badge>
                    </div>
                  </div>

                  {/* Expansion Actions */}
                  <div className="flex items-center gap-2 pt-1">
                    <button
                      type="button"
                      onClick={handleExpand1Hop}
                      disabled={isExpanding}
                      className="flex-1 inline-flex items-center justify-center gap-1.5 py-1.5 px-3 rounded-lg bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-mono text-xs font-semibold transition-colors cursor-pointer shadow-2xs"
                      title="Expand verified 1-hop relationships"
                    >
                      {isExpanding ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Maximize2 className="w-3.5 h-3.5" />}
                      <span>Expand 1-Hop</span>
                    </button>

                    <button
                      type="button"
                      onClick={handleCollapseBranch}
                      disabled={!hasActiveBranch}
                      className="inline-flex items-center justify-center gap-1.5 py-1.5 px-2.5 rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 disabled:opacity-30 text-slate-700 dark:text-slate-300 font-mono text-xs font-medium transition-colors cursor-pointer"
                      title="Collapse expanded branch"
                    >
                      <Minimize2 className="w-3.5 h-3.5" />
                      <span>Collapse</span>
                    </button>
                  </div>

                  {/* Feedback Banner */}
                  {expansionFeedback && (
                    <div
                      className={`p-2 rounded-lg border text-[11px] font-mono ${
                        expansionFeedback.type === 'success'
                          ? 'bg-emerald-50 text-emerald-800 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800'
                          : expansionFeedback.type === 'error'
                          ? 'bg-rose-50 text-rose-800 border-rose-200 dark:bg-rose-950/40 dark:text-rose-300 dark:border-rose-800'
                          : 'bg-slate-50 text-slate-700 border-slate-200 dark:bg-slate-900 dark:text-slate-300 dark:border-slate-800'
                      }`}
                    >
                      {expansionFeedback.message}
                    </div>
                  )}

                  {/* Correlated Sources */}
                  {selectedEntity.sources && selectedEntity.sources.length > 0 && (
                    <div className="space-y-1">
                      <span className="text-slate-400 uppercase text-[10px] block font-mono">Provenance & Sources</span>
                      <div className="flex flex-wrap gap-1">
                        {selectedEntity.sources.map((src: string, i: number) => (
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

                  {/* Telemetry Attributes (Filtered clean key-values, no nulls) */}
                  {selectedEntity.metadata && Object.keys(selectedEntity.metadata).length > 0 && (
                    <div className="space-y-1 pt-2 border-t border-slate-100 dark:border-slate-800">
                      <span className="text-slate-400 uppercase text-[10px] block font-mono">Verified Attributes</span>
                      <div className="p-2 rounded-lg bg-slate-50 border border-slate-200 space-y-1 font-mono text-[11px] dark:bg-slate-900 dark:border-slate-800 max-h-48 overflow-y-auto">
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
              <div className="text-center py-8 space-y-2 text-slate-400">
                <Network className="w-7 h-7 mx-auto opacity-50" />
                <p className="text-xs font-mono">Select a node or connection on the canvas to inspect provenance.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default GraphStudioComponent;

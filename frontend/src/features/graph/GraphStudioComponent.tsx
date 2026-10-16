import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import cytoscape, { Core, EventObject } from 'cytoscape';
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
  Compass,
  Download,
  Route,
  Sparkles,
  ZoomIn,
  ZoomOut,
  RefreshCw,
} from 'lucide-react';

interface Props {
  investigationId?: string;
  entities: Entity[];
  relationships?: Relationship[];
  onRunSearch?: () => void;
  isSearching?: boolean;
}

export type LayoutName = 'cose' | 'concentric' | 'breadthfirst' | 'circle';

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
    null;
  if (direct && typeof direct === 'string') return direct.trim();
  return null;
};

const CATEGORY_COLORS: Record<string, { bg: string; border: string; text: string }> = {
  ORGANIZATION: { bg: '#6366f1', border: '#4338ca', text: '#ffffff' },
  PERSON: { bg: '#f59e0b', border: '#d97706', text: '#ffffff' },
  THREAT_INDICATOR: { bg: '#f43f5e', border: '#e11d48', text: '#ffffff' },
  IP: { bg: '#3b82f6', border: '#2563eb', text: '#ffffff' },
  EMAIL: { bg: '#14b8a6', border: '#0d9488', text: '#ffffff' },
  DOCUMENT: { bg: '#10b981', border: '#059669', text: '#ffffff' },
  DOMAIN: { bg: '#64748b', border: '#475569', text: '#ffffff' },
};

export const GraphStudioComponent: React.FC<Props> = ({
  investigationId,
  entities = [],
  relationships = [],
}) => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const cyRef = useRef<Core | null>(null);

  const [activeLayout, setActiveLayout] = useState<LayoutName>('cose');
  const [filterCategory, setFilterCategory] = useState<string>('ALL');
  const [searchFilter, setSearchFilter] = useState<string>('');
  const [showUnlinked, setShowUnlinked] = useState<boolean>(false);
  const [inspectorOpen, setInspectorOpen] = useState<boolean>(true);
  const [pathfindingMode, setPathfindingMode] = useState<boolean>(false);
  const [pathSource, setPathSource] = useState<string | null>(null);
  const [pathTarget, setPathTarget] = useState<string | null>(null);

  const [selectedEntity, setSelectedEntity] = useState<Entity | null>(null);
  const [selectedEdgeData, setSelectedEdgeData] = useState<any | null>(null);
  const [expandedBranches, setExpandedBranches] = useState<Record<string, { nodeIds: string[]; edgeIds: string[] }>>({});
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

  // Set initial selected entity
  useEffect(() => {
    if (!selectedEntity && rootCandidate) {
      setSelectedEntity(rootCandidate);
    }
  }, [rootCandidate, selectedEntity]);

  // 2. Filter Entities
  const { filteredEntities, unlinkedCount } = useMemo(() => {
    let unlinked = 0;
    const list: Entity[] = [];

    entities.forEach((e) => {
      const key = (e.value || (e as any).name || e.id || '').toLowerCase().trim();
      const isConn = connectedKeys.has(key);
      if (!isConn) unlinked += 1;

      if (filterCategory !== 'ALL' && getEntityCategory(e.type) !== filterCategory) return;
      if (searchFilter.trim()) {
        const q = searchFilter.toLowerCase();
        const matches =
          (e.value || '').toLowerCase().includes(q) ||
          ((e as any).name || '').toLowerCase().includes(q) ||
          (e.type || '').toLowerCase().includes(q);
        if (!matches) return;
      }

      if (!showUnlinked && !isConn) return;
      list.push(e);
    });

    return { filteredEntities: list, unlinkedCount: unlinked };
  }, [entities, connectedKeys, filterCategory, searchFilter, showUnlinked]);

  // 3. Build Cytoscape Elements
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
      const size = isRoot ? 54 : Math.min(60, Math.max(34, 34 + deg * 3));

      elems.push({
        group: 'nodes',
        data: {
          id,
          label: val.length > 24 ? `${val.slice(0, 22)}…` : val,
          fullLabel: val,
          category: cat,
          color: CATEGORY_COLORS[cat]?.bg || '#64748b',
          borderColor: isRoot ? '#4f46e5' : CATEGORY_COLORS[cat]?.border || '#475569',
          borderWidth: isRoot ? 4 : 2,
          isRoot,
          size,
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

    return elems;
  }, [filteredEntities, relationships, selectedEntity, rootCandidate, degrees]);

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
            label: 'data(label)',
            width: 'data(size)',
            height: 'data(size)',
            'border-width': 'data(borderWidth)',
            'border-color': 'data(borderColor)',
            'border-opacity': 0.9,
            color: '#1e293b',
            'font-family': 'monospace, sans-serif',
            'font-size': '11px',
            'font-weight': 'bold',
            'text-valign': 'bottom',
            'text-margin-y': 6,
            'text-wrap': 'ellipsis',
            'text-max-width': '120px',
            'overlay-opacity': 0,
            'transition-property': 'background-color, border-color, border-width, opacity',
            'transition-duration': 0.2,
          },
        },
        {
          selector: 'node:selected',
          style: {
            'border-width': 4,
            'border-color': '#0f172a',
            'border-opacity': 1,
            'underlay-color': '#4f46e5',
            'underlay-padding': 4,
            'underlay-opacity': 0.3,
          },
        },
        {
          selector: 'node[?isRoot]',
          style: {
            'border-width': 4,
            'border-color': '#4f46e5',
            'border-opacity': 1,
            'border-style': 'double',
          },
        },
        {
          selector: 'edge',
          style: {
            width: 2,
            'line-color': '#94a3b8',
            'line-style': 'data(lineStyle)' as any,
            'target-arrow-color': '#64748b',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'arrow-scale': 1.1,
            label: 'data(label)',
            color: '#475569',
            'font-size': '9px',
            'font-family': 'monospace',
            'text-rotation': 'autorotate',
            'text-background-opacity': 0.85,
            'text-background-color': '#ffffff',
            'text-background-padding': '3px',
            'text-background-shape': 'roundrectangle',
            'text-border-opacity': 0.4,
            'text-border-width': 1,
            'text-border-color': '#cbd5e1',
            opacity: 0.85,
          },
        },
        {
          selector: 'edge:selected',
          style: {
            width: 3.5,
            'line-color': '#4f46e5',
            'target-arrow-color': '#4f46e5',
            opacity: 1,
          },
        },
        {
          selector: '.highlighted',
          style: {
            'border-width': 4,
            'border-color': '#4f46e5',
            'line-color': '#4f46e5',
            'target-arrow-color': '#4f46e5',
            opacity: 1,
            'z-index': 99,
          },
        },
        {
          selector: '.faded',
          style: {
            opacity: 0.15,
          },
        },
      ],
      layout: {
        name: activeLayout,
        animate: true,
        animationDuration: 500,
        padding: 50,
      } as any,
      wheelSensitivity: 0.25,
      minZoom: 0.2,
      maxZoom: 3.0,
    });

    // Node Click Handlers
    cy.on('tap', 'node', (evt: EventObject) => {
      const node = evt.target;
      const raw = node.data('rawEntity');
      if (raw) {
        setSelectedEntity(raw);
        setSelectedEdgeData(null);
        setInspectorOpen(true);
      }

      // Highlight neighborhood
      cy.elements().removeClass('highlighted faded');
      const neighborhood = node.neighborhood().add(node);
      cy.elements().not(neighborhood).addClass('faded');
      neighborhood.addClass('highlighted');
    });

    // Edge Click Handlers
    cy.on('tap', 'edge', (evt: EventObject) => {
      const edge = evt.target;
      const raw = edge.data('rawRel');
      setSelectedEdgeData(raw || edge.data());
      setSelectedEntity(null);
      setInspectorOpen(true);
    });

    // Canvas Background Click: Reset highlights
    cy.on('tap', (evt: EventObject) => {
      if (evt.target === cy) {
        cy.elements().removeClass('highlighted faded');
      }
    });

    cyRef.current = cy;

    return () => {
      cy.destroy();
      cyRef.current = null;
    };
  }, []);

  // Update Cytoscape Elements when data changes
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;

    cy.batch(() => {
      cy.elements().remove();
      cy.add(elements);
    });

    // Run active layout with animation
    const layout = cy.layout({
      name: activeLayout,
      animate: true,
      animationDuration: 400,
      padding: 60,
    } as any);
    layout.run();
  }, [elements, activeLayout]);

  // 1-Hop Graph Expansion via Neo4j API
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

      const newElemDefs: cytoscape.ElementDefinition[] = [];
      const newNodeIds: string[] = [];
      const newEdgeIds: string[] = [];

      incomingNodes.forEach((nDoc: any) => {
        const val = (nDoc.value || nDoc.name || nDoc.id || '').trim();
        const id = nDoc.id || `node_${val.toLowerCase().replace(/[^a-z0-9_-]/g, '_')}`;

        if (cy.getElementById(id).length === 0) {
          const cat = getEntityCategory(nDoc.type);
          newElemDefs.push({
            group: 'nodes',
            data: {
              id,
              label: val.length > 24 ? `${val.slice(0, 22)}…` : val,
              fullLabel: val,
              category: cat,
              color: CATEGORY_COLORS[cat]?.bg || '#64748b',
              borderColor: CATEGORY_COLORS[cat]?.border || '#475569',
              borderWidth: 2,
              isRoot: false,
              size: 38,
              rawEntity: nDoc,
            },
          });
          newNodeIds.push(id);
        }
      });

      incomingEdges.forEach((r: any, idx: number) => {
        const sVal = (r.source_id || r.source_entity_value || '').toLowerCase().trim();
        const tVal = (r.target_id || r.target_entity_value || '').toLowerCase().trim();
        const sId = cy.getElementById(sVal).length > 0 ? sVal : `node_${sVal.replace(/[^a-z0-9_-]/g, '_')}`;
        const tId = cy.getElementById(tVal).length > 0 ? tVal : `node_${tVal.replace(/[^a-z0-9_-]/g, '_')}`;
        const edgeId = r.id || `edge_exp_${idx}_${sId}_${tId}`;

        if (cy.getElementById(edgeId).length === 0) {
          const relType = r.relationship_type || r.type || 'RELATED';
          newElemDefs.push({
            group: 'edges',
            data: {
              id: edgeId,
              source: sId,
              target: tId,
              label: relType.replace(/_/g, ' ').toLowerCase(),
              lineStyle: r.is_inferred ? 'dashed' : 'solid',
              rawRel: r,
            },
          });
          newEdgeIds.push(edgeId);
        }
      });

      cy.add(newElemDefs);

      // Re-layout with concentric or force around parent
      const parentNode = cy.getElementById(selectedEntity.id || `node_${entVal.toLowerCase().replace(/[^a-z0-9_-]/g, '_')}`);
      if (parentNode.length > 0) {
        const neighborhood = parentNode.neighborhood().add(parentNode);
        const subLayout = neighborhood.layout({
          name: 'concentric',
          concentric: (node: any) => (node.id() === parentNode.id() ? 2 : 1),
          levelWidth: () => 1,
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
        message: `Discovered ${newNodeIds.length} connected entities & ${newEdgeIds.length} verified paths.`,
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

  // Pathfinding Tool (Shortest Path between two nodes)
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
    const png64 = cy.png({ full: true, scale: 2, bg: '#ffffff' });
    const a = document.createElement('a');
    a.href = png64;
    a.download = `investigation_relationship_graph_${Date.now()}.png`;
    a.click();
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
    <div className="space-y-3 font-sans">
      {/* Modern OSINT Link Analysis Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-3 rounded-xl border border-slate-200 bg-white shadow-2xs dark:border-slate-800 dark:bg-[#0f1422] text-xs">
        <div className="flex flex-wrap items-center gap-2">
          {/* Layout Algorithm Selector */}
          <div className="flex items-center gap-0.5 bg-slate-100 dark:bg-slate-800 p-0.5 rounded-lg font-mono">
            <button
              type="button"
              onClick={() => setActiveLayout('cose')}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] transition-colors ${
                activeLayout === 'cose'
                  ? 'bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-2xs font-bold'
                  : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
              }`}
              title="Force-Directed CoSE: Physics simulation clustering connected nodes"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Force Network</span>
            </button>
            <button
              type="button"
              onClick={() => setActiveLayout('concentric')}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] transition-colors ${
                activeLayout === 'concentric'
                  ? 'bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-2xs font-bold'
                  : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
              }`}
              title="Concentric: Orbits arranged by node importance and degrees"
            >
              <Radio className="w-3.5 h-3.5" />
              <span>Radial Orbits</span>
            </button>
            <button
              type="button"
              onClick={() => setActiveLayout('breadthfirst')}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] transition-colors ${
                activeLayout === 'breadthfirst'
                  ? 'bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-2xs font-bold'
                  : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
              }`}
              title="Hierarchical: Top-to-bottom command & infrastructure hierarchy"
            >
              <GitFork className="w-3.5 h-3.5" />
              <span>Hierarchy</span>
            </button>
            <button
              type="button"
              onClick={() => setActiveLayout('circle')}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] transition-colors ${
                activeLayout === 'circle'
                  ? 'bg-white dark:bg-slate-900 text-indigo-600 dark:text-indigo-400 shadow-2xs font-bold'
                  : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
              }`}
              title="Circular: Uniform ring layout"
            >
              <Focus className="w-3.5 h-3.5" />
              <span>Circle</span>
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
              <option value="ALL">All Categories</option>
              <option value="ORGANIZATION">Organizations</option>
              <option value="PERSON">Persons / Actors</option>
              <option value="THREAT_INDICATOR">Threat Indicators</option>
              <option value="DOMAIN">Domains / URLs</option>
              <option value="IP">IP Addresses</option>
              <option value="EMAIL">Emails</option>
            </select>
          </div>

          {/* Toggle Unlinked Isolated Entities */}
          {unlinkedCount > 0 && (
            <button
              type="button"
              onClick={() => setShowUnlinked((prev) => !prev)}
              className={`flex items-center gap-1.5 h-7 px-2.5 rounded-lg border text-xs font-mono transition-colors ${
                showUnlinked
                  ? 'bg-indigo-50 border-indigo-200 text-indigo-700 dark:bg-indigo-950/60 dark:border-indigo-800 dark:text-indigo-300'
                  : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50 dark:bg-slate-900 dark:border-slate-800 dark:text-slate-300'
              }`}
              title="Toggle visibility of isolated background entities with no mapped connections"
            >
              {showUnlinked ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3 text-slate-400" />}
              <span>Unlinked ({unlinkedCount})</span>
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
            className={`flex items-center gap-1.5 h-7 px-2.5 rounded-lg border text-xs font-mono transition-colors ${
              pathfindingMode
                ? 'bg-amber-50 border-amber-300 text-amber-800 dark:bg-amber-950/60 dark:border-amber-800 dark:text-amber-300 font-bold'
                : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50 dark:bg-slate-900 dark:border-slate-800 dark:text-slate-300'
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
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-2 text-slate-400" />
            <input
              type="text"
              placeholder="Find entity..."
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
              className="h-7 pl-7 pr-2 rounded-lg bg-slate-50 border border-slate-200 text-xs font-mono text-slate-800 focus:outline-none focus:border-indigo-500 dark:bg-slate-900 dark:border-slate-800 dark:text-slate-200 w-36"
            />
          </div>

          {/* Visible Nodes / Edges Counter */}
          <div className="flex items-center gap-1 px-2 py-1 rounded-md bg-slate-100 dark:bg-slate-800 text-[11px] font-mono text-slate-600 dark:text-slate-300">
            <span>{filteredEntities.length} nodes</span>
            <span className="text-slate-400">•</span>
            <span>{relationships.length} edges</span>
          </div>

          {/* Canvas Navigation Controls */}
          <div className="flex items-center gap-0.5 border border-slate-200 dark:border-slate-800 rounded-lg p-0.5">
            <button
              type="button"
              onClick={() => cyRef.current?.zoom(cyRef.current.zoom() * 1.25)}
              className="p-1 rounded hover:bg-slate-100 text-slate-600 dark:hover:bg-slate-800 dark:text-slate-300"
              title="Zoom In"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
            <button
              type="button"
              onClick={() => cyRef.current?.zoom(cyRef.current.zoom() * 0.8)}
              className="p-1 rounded hover:bg-slate-100 text-slate-600 dark:hover:bg-slate-800 dark:text-slate-300"
              title="Zoom Out"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <button
              type="button"
              onClick={() => cyRef.current?.fit(undefined, 50)}
              className="p-1 rounded hover:bg-slate-100 text-slate-600 dark:hover:bg-slate-800 dark:text-slate-300"
              title="Fit View"
            >
              <Compass className="w-3.5 h-3.5" />
            </button>
            <button
              type="button"
              onClick={handleExportPNG}
              className="p-1 rounded hover:bg-slate-100 text-slate-600 dark:hover:bg-slate-800 dark:text-slate-300"
              title="Export High-Resolution PNG for Investigation Report"
            >
              <Download className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Toggle Inspector */}
          <button
            type="button"
            onClick={() => setInspectorOpen((prev) => !prev)}
            className={`flex items-center gap-1 h-7 px-2 rounded-lg border text-xs font-mono transition-colors ${
              inspectorOpen
                ? 'bg-indigo-50 border-indigo-200 text-indigo-700 dark:bg-indigo-950/60 dark:border-indigo-800 dark:text-indigo-300'
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
        <div className="flex flex-wrap items-center justify-between gap-3 p-2.5 rounded-lg bg-amber-50/80 border border-amber-200 dark:bg-amber-950/30 dark:border-amber-900/50 text-xs font-mono">
          <div className="flex items-center gap-2">
            <Route className="w-4 h-4 text-amber-600 dark:text-amber-400" />
            <span className="font-bold text-amber-900 dark:text-amber-200">Shortest Path Analyzer:</span>
            <span>Select Source & Target to discover intelligence traversal route.</span>
          </div>
          <div className="flex items-center gap-2">
            <select
              value={pathSource || ''}
              onChange={(e) => setPathSource(e.target.value)}
              className="h-7 px-2 rounded bg-white border border-amber-300 text-xs dark:bg-slate-900 dark:border-slate-800"
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
            <span className="text-amber-600">→</span>
            <select
              value={pathTarget || ''}
              onChange={(e) => setPathTarget(e.target.value)}
              className="h-7 px-2 rounded bg-white border border-amber-300 text-xs dark:bg-slate-900 dark:border-slate-800"
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
              className="h-7 px-3 rounded bg-amber-600 hover:bg-amber-700 disabled:opacity-40 text-white font-bold transition-colors cursor-pointer"
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
          } h-[680px] rounded-xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-[#090d16] relative overflow-hidden transition-all duration-200 shadow-2xs`}
        >
          {/* Cytoscape Container */}
          <div ref={containerRef} className="w-full h-full cursor-grab active:cursor-grabbing" />

          {/* Minimalist Legend Overlay */}
          <div className="absolute bottom-3 left-3 bg-white/95 dark:bg-slate-900/95 backdrop-blur-xs px-2.5 py-1.5 rounded-lg border border-slate-200 dark:border-slate-800 text-[10px] font-mono flex items-center gap-3 shadow-2xs select-none">
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
              <span className="text-slate-600 dark:text-slate-400">Threat/IOC</span>
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
        </div>

        {/* Collapsible Inspector Panel */}
        {inspectorOpen && (
          <div className="lg:col-span-1 rounded-xl border border-slate-200 bg-white p-3.5 space-y-3.5 shadow-2xs dark:border-slate-800 dark:bg-[#0f1422] max-h-[680px] overflow-y-auto">
            {selectedEdgeData ? (
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
                    onClick={() => setSelectedEdgeData(null)}
                    className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-xs"
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

                <div className="p-2 rounded-lg bg-slate-50 border border-slate-200 dark:bg-slate-900/60 dark:border-slate-800 space-y-1 font-mono text-[11px]">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Source:</span>
                    <span className="font-semibold text-slate-800 dark:text-slate-200 truncate max-w-[130px]">
                      {selectedEdgeData.source_entity_value || selectedEdgeData.source_id || selectedEdgeData.source}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Target:</span>
                    <span className="font-semibold text-slate-800 dark:text-slate-200 truncate max-w-[130px]">
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
                  <div className="space-y-1 pt-2 border-t border-slate-100 dark:border-slate-800">
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
                  {feedback && (
                    <div
                      className={`p-2 rounded-lg border text-[11px] font-mono ${
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
                <p className="text-xs font-mono">Select any node or connection on the canvas to inspect provenance.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default GraphStudioComponent;

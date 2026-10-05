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
import { Entity } from '../../types';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
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
} from 'lucide-react';

interface Props {
  investigationId?: string;
  entities: Entity[];
  onRunSearch?: () => void;
  isSearching?: boolean;
}

// Icon helper by entity type
const getEntityIcon = (type: string) => {
  switch (type.toUpperCase()) {
    case 'IP':
    case 'IPV4':
    case 'IPV6':
      return Server;
    case 'THREAT_ACTOR':
    case 'PERSON':
      return User;
    case 'HASH':
    case 'SHA256':
    case 'MD5':
      return Hash;
    case 'EMAIL':
      return Mail;
    case 'DOMAIN':
    default:
      return Globe;
  }
};

// Custom intelligence node component for React Flow
const IntelNode: React.FC<NodeProps> = ({ data, selected }) => {
  const Icon = getEntityIcon(data.type);
  const confidence = data.confidence || 0.8;
  const isMalicious = confidence >= 0.85;
  const isSuspicious = confidence >= 0.6 && confidence < 0.85;

  const displayName = data.value || data.name || 'Unknown Entity';

  return (
    <div
      className={`px-3 py-2 rounded-lg border bg-white shadow-md transition-all font-mono min-w-[170px] select-none dark:bg-zinc-900 ${
        selected
          ? 'border-black ring-2 ring-black/20 dark:border-white dark:ring-white/20'
          : isMalicious
          ? 'border-red-300 dark:border-red-900'
          : isSuspicious
          ? 'border-amber-300 dark:border-amber-900'
          : 'border-zinc-200 dark:border-zinc-800'
      }`}
    >
      <Handle type="target" position={Position.Top} className="!w-2 !h-2 !bg-zinc-400 !border-white" />

      <div className="flex items-center justify-between gap-2 mb-1.5">
        <div className="flex items-center gap-1.5">
          <div
            className={`w-5 h-5 rounded flex items-center justify-center ${
              isMalicious
                ? 'bg-red-50 text-red-600 dark:bg-red-950 dark:text-red-400'
                : isSuspicious
                ? 'bg-amber-50 text-amber-600 dark:bg-amber-950 dark:text-amber-400'
                : 'bg-zinc-100 text-zinc-800 dark:bg-zinc-800 dark:text-zinc-200'
            }`}
          >
            <Icon className="w-3 h-3" />
          </div>
          <span className="text-[10px] text-zinc-500 font-bold uppercase tracking-wider">{data.type}</span>
        </div>

        <span
          className={`text-[9px] px-1 py-0.2 rounded font-bold ${
            isMalicious
              ? 'bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300'
              : isSuspicious
              ? 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300'
              : 'bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300'
          }`}
        >
          {Math.round(confidence * 100)}%
        </span>
      </div>

      <p className="text-xs font-bold text-zinc-950 dark:text-zinc-100 truncate max-w-[150px]">
        {displayName}
      </p>

      <div className="flex items-center justify-between mt-1 text-[10px] text-zinc-500">
        <span>{isMalicious ? 'CRITICAL' : isSuspicious ? 'ELEVATED' : 'OBSERVED'}</span>
        {data.sources && <span>{data.sources.length} src</span>}
      </div>

      <Handle type="source" position={Position.Bottom} className="!w-2 !h-2 !bg-zinc-400 !border-white" />
    </div>
  );
};

const nodeTypes = {
  intelNode: IntelNode,
};

export const GraphStudioComponent: React.FC<Props> = ({
  investigationId,
  entities = [],
  onRunSearch,
  isSearching,
}) => {
  const [filterType, setFilterType] = useState<string>('ALL');
  const [selectedEntity, setSelectedEntity] = useState<Entity | null>(entities[0] || null);

  // Filter entities based on select
  const filteredEntities = useMemo(() => {
    if (filterType === 'ALL') return entities;
    return entities.filter((e) => e.type.toUpperCase() === filterType);
  }, [entities, filterType]);

  // Compute radial layout for nodes
  const initialNodes: Node[] = useMemo(() => {
    if (filteredEntities.length === 0) return [];

    const centerX = 380;
    const centerY = 240;

    return filteredEntities.map((ent, idx) => {
      let x = centerX;
      let y = centerY;

      if (idx > 0) {
        const count = filteredEntities.length - 1;
        const angle = ((idx - 1) / Math.max(1, count)) * 2 * Math.PI;
        const radius = 220 + (idx % 2 === 0 ? 35 : -35);
        x = centerX + Math.cos(angle) * radius;
        y = centerY + Math.sin(angle) * radius;
      }

      return {
        id: ent.id || `node-${idx}-${ent.value || (ent as any).name}`,
        type: 'intelNode',
        position: { x, y },
        data: ent,
      };
    });
  }, [filteredEntities]);

  // Generate relationship edges from center root to all nodes
  const initialEdges: Edge[] = useMemo(() => {
    if (filteredEntities.length <= 1) return [];
    const rootId = filteredEntities[0].id || `node-0-${filteredEntities[0].value || (filteredEntities[0] as any).name}`;

    return filteredEntities.slice(1).map((ent, idx) => {
      const entId = ent.id || `node-${idx + 1}-${ent.value || (ent as any).name}`;
      const relLabel =
        ent.type.toUpperCase() === 'IP'
          ? 'RESOLVES_TO'
          : ent.type.toUpperCase() === 'THREAT_ACTOR'
          ? 'ATTRIBUTED_TO'
          : ent.type.toUpperCase() === 'HASH'
          ? 'PAYLOAD_DROPPED'
          : 'ASSOCIATED';

      const isHighRisk = (ent.confidence || 0) >= 0.85;

      return {
        id: `e-${rootId}-${entId}`,
        source: rootId,
        target: entId,
        label: relLabel,
        type: 'smoothstep',
        animated: isHighRisk,
        style: {
          stroke: isHighRisk ? '#dc2626' : '#71717a',
          strokeWidth: 1.5,
        },
        labelStyle: {
          fill: '#09090b',
          fontWeight: 700,
          fontFamily: 'monospace',
          fontSize: 9,
        },
        labelBgStyle: {
          fill: '#ffffff',
          stroke: '#e4e4e7',
          strokeWidth: 1,
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: isHighRisk ? '#dc2626' : '#71717a',
        },
      };
    });
  }, [filteredEntities]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // Sync state if entities change
  React.useEffect(() => {
    setNodes(initialNodes);
    setEdges(initialEdges);
    if (!selectedEntity && filteredEntities.length > 0) {
      setSelectedEntity(filteredEntities[0]);
    }
  }, [initialNodes, initialEdges, filteredEntities]);

  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      const found = entities.find((e) => (e.id || `node-${entities.indexOf(e)}-${e.value || (e as any).name}`) === node.id);
      if (found) {
        setSelectedEntity(found);
      }
    },
    [entities]
  );

  if (entities.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-zinc-300 dark:border-zinc-800 bg-white dark:bg-zinc-900/40 p-12 text-center font-mono space-y-4">
        <div className="w-14 h-14 rounded-full bg-zinc-100 dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 flex items-center justify-center mx-auto text-zinc-500">
          <Network className="w-7 h-7" />
        </div>
        <div className="space-y-1.5 max-w-md mx-auto">
          <h3 className="text-sm font-bold text-zinc-950 dark:text-zinc-50 uppercase tracking-wider">
            No Entity Relationships Discovered
          </h3>
          <p className="text-xs text-zinc-500 dark:text-zinc-400 leading-relaxed">
            There are no correlated graph entities or relationship links mapped for this investigation yet. Execute an intelligence search to automatically populate the relationship topology.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Controls Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-3 rounded-lg border border-zinc-200 bg-white shadow-sm dark:border-zinc-800 dark:bg-zinc-900 text-xs">
        <div className="flex items-center gap-2">
          <Filter className="w-3.5 h-3.5 text-zinc-500" />
          <span className="text-zinc-600 dark:text-zinc-400 font-mono">Filter Category:</span>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="h-8 px-2.5 rounded-md bg-white border border-zinc-200 text-xs text-zinc-800 font-mono focus:border-black dark:bg-zinc-950 dark:border-zinc-800 dark:text-zinc-200"
          >
            <option value="ALL">All Intelligence ({entities.length})</option>
            <option value="DOMAIN">Domains</option>
            <option value="IP">IP Addresses</option>
            <option value="THREAT_ACTOR">Threat Actors</option>
            <option value="HASH">Malware Hashes</option>
            <option value="EMAIL">Email Handles</option>
          </select>
        </div>

        <div className="flex items-center gap-2 text-xs font-mono">
          <Badge variant="default">ReactFlow Graph Active</Badge>
          <span className="text-zinc-500">
            {nodes.length} Nodes • {edges.length} Edges
          </span>
        </div>
      </div>

      {/* Main Canvas + Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* Interactive React Flow Canvas */}
        <div className="lg:col-span-3 rounded-lg border border-zinc-200 bg-zinc-50 dark:border-zinc-800 dark:bg-[#090a0d] relative overflow-hidden h-[540px] shadow-sm">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={onNodeClick}
            nodeTypes={nodeTypes}
            fitView
            minZoom={0.2}
            maxZoom={2.5}
          >
            <Background color="#cbd5e1" gap={20} size={1} />
            <Controls className="!bg-white !border !border-zinc-200 !shadow-sm !rounded-md" />
            <MiniMap
              className="!bg-white !border !border-zinc-200 !rounded-md !shadow-sm"
              nodeColor={(n) => {
                const conf = (n.data?.confidence as number) || 0.8;
                if (conf >= 0.85) return '#ef4444';
                if (conf >= 0.6) return '#f59e0b';
                return '#18181b';
              }}
            />
          </ReactFlow>
        </div>

        {/* Node Inspector Panel */}
        <div className="rounded-lg border border-zinc-200 bg-white p-4 space-y-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
          <div className="flex items-center gap-2 pb-2 border-b border-zinc-200 dark:border-zinc-800">
            <Info className="w-4 h-4 text-zinc-700 dark:text-zinc-300" />
            <h3 className="text-xs font-mono font-semibold text-zinc-950 dark:text-white uppercase tracking-wider">
              Entity Telemetry Inspector
            </h3>
          </div>

          {selectedEntity ? (
            <div className="space-y-3 text-xs">
              <div>
                <span className="text-zinc-500 uppercase text-[10px] block font-mono">Entity Target</span>
                <p className="font-bold text-zinc-950 dark:text-white break-all mt-0.5 text-sm">
                  {selectedEntity.value || (selectedEntity as any).name}
                </p>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-zinc-600 dark:text-zinc-400">Classification</span>
                <Badge variant="outline">{selectedEntity.type}</Badge>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-zinc-600 dark:text-zinc-400">Analytic Confidence</span>
                <Badge variant={(selectedEntity.confidence || 0) >= 0.85 ? 'destructive' : 'warning'}>
                  {Math.round((selectedEntity.confidence || 0.8) * 100)}%
                </Badge>
              </div>

              {selectedEntity.sources && selectedEntity.sources.length > 0 && (
                <div>
                  <span className="text-zinc-500 uppercase text-[10px] block font-mono mb-1">Sources</span>
                  <div className="flex flex-wrap gap-1">
                    {selectedEntity.sources.map((src, i) => (
                      <span
                        key={i}
                        className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-zinc-100 text-zinc-600 border border-zinc-200 dark:bg-zinc-800 dark:text-zinc-400 dark:border-zinc-700"
                      >
                        {src}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {selectedEntity.metadata && Object.keys(selectedEntity.metadata).length > 0 && (
                <div className="space-y-1.5 pt-2 border-t border-zinc-200 dark:border-zinc-800">
                  <span className="text-zinc-500 uppercase text-[10px] block font-mono">Metadata</span>
                  <div className="p-2.5 rounded-md bg-zinc-50 border border-zinc-200 space-y-1 font-mono text-[11px] dark:bg-zinc-950 dark:border-zinc-800">
                    {Object.entries(selectedEntity.metadata).map(([k, v]) => (
                      <div key={k} className="flex justify-between gap-2">
                        <span className="text-zinc-500">{k}:</span>
                        <span className="text-zinc-800 dark:text-zinc-300 font-bold truncate max-w-[130px]">
                          {typeof v === 'object' ? JSON.stringify(v) : String(v)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <p className="text-xs text-zinc-500 font-mono">Click a graph node to inspect telemetry.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default GraphStudioComponent;

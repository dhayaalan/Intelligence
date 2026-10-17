import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiRequest } from '../../core/api/client';
import { GraphStudioComponent } from './GraphStudioComponent';
import { Share2, FolderGit2, AlertCircle } from 'lucide-react';
import { Badge } from '../../components/ui/Badge';
import { Entity, Relationship, Investigation } from '../../types';

interface InvestigationGraphResponse {
  investigation_id: string;
  target: string;
  target_type: string;
  entities: Entity[];
  relationships: Relationship[];
}

export const GraphStudioPage: React.FC = () => {
  const [selectedInvId, setSelectedInvId] = useState<string>('');

  // 1. Fetch investigations list to allow scoping to a specific case
  const { data: investigations = [] } = useQuery({
    queryKey: ['investigations'],
    queryFn: () => apiRequest<Investigation[]>('/investigations'),
  });

  const activeId = selectedInvId || (investigations[0]?.id ?? '');

  // 2. Fetch strictly investigation-scoped graph nodes and edges
  const { data: graphData, isLoading: isGraphLoading } = useQuery({
    queryKey: ['investigation-graph', activeId],
    queryFn: () => apiRequest<InvestigationGraphResponse>(`/investigations/${activeId}/graph`),
    enabled: Boolean(activeId),
  });

  const entities = graphData?.entities || [];
  const relationships = graphData?.relationships || [];

  return (
    <div className="space-y-6 w-full">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-zinc-200 dark:border-zinc-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-mono text-zinc-500 uppercase tracking-wider">INTELLIGENCE</span>
            <span className="text-zinc-300 dark:text-zinc-700">//</span>
            <span className="text-xs font-mono text-black dark:text-white font-bold">CASE GRAPH</span>
          </div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-zinc-950 dark:text-white flex items-center gap-2 font-sans">
            <Share2 className="w-6 h-6 text-zinc-700 dark:text-zinc-300" />
            <span>Relationship Graph Studio</span>
          </h1>
          <p className="text-xs text-zinc-600 dark:text-zinc-400 mt-1">
            Investigation-scoped node correlation mapping verified entities and evidentiary links.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {investigations.length > 0 && (
            <div className="flex items-center gap-2">
              <FolderGit2 className="w-4 h-4 text-slate-400" />
              <select
                value={activeId}
                onChange={(e) => setSelectedInvId(e.target.value)}
                className="h-9 px-3 text-xs font-mono bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              >
                {investigations.map((inv) => (
                  <option key={inv.id} value={inv.id}>
                    {inv.title || inv.target}
                  </option>
                ))}
              </select>
            </div>
          )}
          <Badge variant="default">
            {relationships.length} EDGES • {entities.length} NODES
          </Badge>
        </div>
      </div>

      {investigations.length === 0 ? (
        <div className="p-12 text-center rounded-2xl border border-dashed border-slate-300 dark:border-slate-800 bg-white/50 dark:bg-slate-950/40">
          <AlertCircle className="w-10 h-10 mx-auto text-slate-400 mb-3" />
          <h3 className="text-sm font-bold text-slate-900 dark:text-white mb-1">No Active Investigations</h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 max-w-sm mx-auto">
            Execute a search or initialize an investigation to visualize correlated relationship topologies.
          </p>
        </div>
      ) : (
        <GraphStudioComponent
          investigationId={activeId}
          entities={entities}
          relationships={relationships}
          isSearching={isGraphLoading}
        />
      )}
    </div>
  );
};

export default GraphStudioPage;

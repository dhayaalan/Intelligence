import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiRequest } from '../../core/api/client';
import { GraphStudioComponent } from './GraphStudioComponent';
import { Share2 } from 'lucide-react';
import { Badge } from '../../components/ui/Badge';
import { Entity } from '../../types';

export const GraphStudioPage: React.FC = () => {
  const { data: entities = [], isLoading } = useQuery({
    queryKey: ['entities'],
    queryFn: () => apiRequest<Entity[]>('/entities'),
  });

  return (
    <div className="space-y-6 w-full">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-zinc-200 dark:border-zinc-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-mono text-zinc-500 uppercase tracking-wider">INTELLIGENCE</span>
            <span className="text-zinc-300 dark:text-zinc-700">//</span>
            <span className="text-xs font-mono text-black dark:text-white font-bold">CORRELATION</span>
          </div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-zinc-950 dark:text-white flex items-center gap-2 font-sans">
            <Share2 className="w-6 h-6 text-zinc-700 dark:text-zinc-300" />
            <span>Relationship Graph Studio</span>
          </h1>
          <p className="text-xs text-zinc-600 dark:text-zinc-400 mt-1">
            Interactive multi-hop node correlation mapping DNS infrastructure, autonomous systems, and threat actors.
          </p>
        </div>

        <Badge variant="default">GRAPH ENGINE ACTIVE</Badge>
      </div>

      <GraphStudioComponent investigationId="global" entities={entities} />
    </div>
  );
};

export default GraphStudioPage;

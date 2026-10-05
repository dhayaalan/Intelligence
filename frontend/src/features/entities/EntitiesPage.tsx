import React, { useState, useEffect, useMemo } from 'react';
import { Layers, Search, Filter, Globe, Server, Mail, Hash, User, Clock } from 'lucide-react';
import { apiRequest } from '../../core/api/client';
import { Badge } from '../../components/ui/Badge';
import { Card, CardContent } from '../../components/ui/Card';
import { Pagination } from '../../components/ui/Pagination';
import { formatDate } from '../../lib/utils';

interface Entity {
  id: string;
  tenant_id: string;
  investigation_id?: string;
  type: string;
  value: string;
  confidence: number;
  sources: string[];
  metadata: Record<string, any>;
  first_seen: string;
  last_seen: string;
}

const getEntityIcon = (type: string) => {
  switch (type.toUpperCase()) {
    case 'DOMAIN':
      return <Globe className="w-3.5 h-3.5" />;
    case 'IP':
    case 'IPV4':
    case 'IPV6':
      return <Server className="w-3.5 h-3.5" />;
    case 'EMAIL':
      return <Mail className="w-3.5 h-3.5" />;
    case 'HASH':
    case 'SHA256':
    case 'MD5':
      return <Hash className="w-3.5 h-3.5" />;
    case 'THREAT_ACTOR':
    case 'PERSON':
      return <User className="w-3.5 h-3.5" />;
    default:
      return <Layers className="w-3.5 h-3.5" />;
  }
};

const getConfidenceBadge = (confidence: number): 'success' | 'info' | 'warning' | 'destructive' => {
  if (confidence >= 0.9) return 'success';
  if (confidence >= 0.7) return 'info';
  if (confidence >= 0.5) return 'warning';
  return 'destructive';
};

export const EntitiesPage: React.FC = () => {
  const [entities, setEntities] = useState<Entity[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState('ALL');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(12);

  useEffect(() => {
    const fetchEntities = async () => {
      try {
        const data = await apiRequest<Entity[]>('/entities');
        setEntities(data);
      } catch (err) {
        console.error('Failed to load entities', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchEntities();
  }, []);

  const filteredEntities = useMemo(() => {
    return entities.filter((ent) => {
      const matchesSearch = ent.value.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesType = typeFilter === 'ALL' || ent.type.toUpperCase() === typeFilter;
      return matchesSearch && matchesType;
    });
  }, [entities, searchTerm, typeFilter]);

  const paginatedEntities = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return filteredEntities.slice(start, start + pageSize);
  }, [filteredEntities, currentPage, pageSize]);

  const entityTypes = useMemo(() => {
    const types = new Set(entities.map((e) => e.type.toUpperCase()));
    return ['ALL', ...Array.from(types).sort()];
  }, [entities]);

  if (isLoading) {
    return (
      <div className="w-full space-y-4">
        <div className="h-6 w-48 bg-zinc-200 dark:bg-zinc-800 rounded animate-pulse" />
        <div className="h-4 w-96 bg-zinc-100 dark:bg-zinc-800/60 rounded animate-pulse" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="h-32 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="w-full space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-zinc-200 dark:border-zinc-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-mono text-zinc-500 uppercase tracking-wider">INTELLIGENCE</span>
            <span className="text-zinc-300 dark:text-zinc-700">//</span>
            <span className="text-xs font-mono text-black dark:text-white font-bold">ENTITIES</span>
          </div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-zinc-950 dark:text-white flex items-center gap-2 font-sans">
            <Layers className="w-6 h-6 text-zinc-700 dark:text-zinc-300" />
            <span>Normalized Entity Explorer</span>
          </h1>
          <p className="text-xs text-zinc-600 dark:text-zinc-400 mt-1">
            Unified catalog of extracted technical and human indicators across active investigations.
          </p>
        </div>

        <Badge variant="default" size="md">{entities.length} Normalized Entities</Badge>
      </div>

      {/* Search & Filter Controls */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-zinc-400 dark:text-zinc-500 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Filter entities by value or identifier..."
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setCurrentPage(1);
            }}
            className="w-full h-9 pl-9 pr-3 rounded-md bg-white border border-zinc-200 text-xs text-zinc-900 placeholder:text-zinc-400 focus:outline-none focus:ring-1 focus:ring-black dark:focus:ring-white font-mono dark:bg-zinc-950 dark:border-zinc-800 dark:text-zinc-100 transition-colors shadow-2xs"
          />
        </div>

        <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
          <Filter className="w-3.5 h-3.5 text-zinc-400 dark:text-zinc-500 shrink-0" />
          {entityTypes.map((type) => (
            <button
              key={type}
              onClick={() => {
                setTypeFilter(type);
                setCurrentPage(1);
              }}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium whitespace-nowrap transition-all ${
                typeFilter === type
                  ? 'bg-slate-900 text-white font-semibold shadow-xs dark:bg-white dark:text-slate-950'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100 dark:text-slate-400 dark:hover:text-white dark:hover:bg-slate-800'
              }`}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      {/* Entity Grid */}
      {filteredEntities.length === 0 ? (
        <div className="text-center py-16 text-zinc-500 text-xs font-mono border border-dashed border-zinc-200 dark:border-zinc-800 rounded-xl">
          <Layers className="w-8 h-8 mx-auto mb-3 text-zinc-400 dark:text-zinc-600" />
          {entities.length === 0
            ? 'No entities extracted. Entities are automatically normalized from search results.'
            : 'No entities match the current filter criteria.'}
        </div>
      ) : (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {paginatedEntities.map((ent) => (
              <Card key={ent.id} className="hover:border-zinc-300 dark:hover:border-zinc-700 transition-all group cursor-default">
                <CardContent className="p-4 sm:p-5 space-y-2.5">
                  <div className="flex items-center justify-between">
                    <Badge variant="mono" size="sm">
                      <span className="text-zinc-500 dark:text-zinc-400">{getEntityIcon(ent.type)}</span>
                      {ent.type}
                    </Badge>
                    <Badge variant={getConfidenceBadge(ent.confidence)} size="sm">
                      {(ent.confidence * 100).toFixed(0)}% Confidence
                    </Badge>
                  </div>

                  <div>
                    <h4 className="text-xs font-mono font-semibold text-zinc-950 dark:text-white break-all group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                      {ent.value}
                    </h4>
                    <p className="text-[10px] text-zinc-500 dark:text-zinc-400 font-mono mt-0.5">
                      {ent.sources.length} source{ent.sources.length !== 1 ? 's' : ''}
                    </p>
                  </div>

                  {/* Sources */}
                  {ent.sources.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {ent.sources.slice(0, 3).map((src, i) => (
                        <span
                          key={i}
                          className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-zinc-100 text-zinc-600 border border-zinc-200 dark:bg-zinc-800 dark:text-zinc-400 dark:border-zinc-700"
                        >
                          {src}
                        </span>
                      ))}
                      {ent.sources.length > 3 && (
                        <span className="text-[10px] font-mono text-zinc-500">+{ent.sources.length - 3} more</span>
                      )}
                    </div>
                  )}

                  <div className="pt-2 border-t border-zinc-100 dark:border-zinc-800 flex items-center justify-between text-[10px] text-zinc-500 dark:text-zinc-400 font-mono">
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3 text-zinc-400" />
                      {formatDate(ent.first_seen)}
                    </span>
                    <span>
                      Last: {formatDate(ent.last_seen)}
                    </span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Pagination Controls */}
          <Card className="p-0 overflow-hidden">
            <Pagination
              currentPage={currentPage}
              totalPages={Math.ceil(filteredEntities.length / pageSize)}
              totalItems={filteredEntities.length}
              pageSize={pageSize}
              onPageChange={setCurrentPage}
              onPageSizeChange={(sz) => {
                setPageSize(sz);
                setCurrentPage(1);
              }}
              pageSizeOptions={[12, 24, 48]}
            />
          </Card>
        </div>
      )}
    </div>
  );
};

export default EntitiesPage;

import React, { useState } from 'react';
import { Dialog } from '../../components/ui/Dialog';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import {
  useNewsWatchlists,
  useCreateNewsWatchlist,
  useDeleteNewsWatchlist,
} from '../../core/api/newsHooks';
import { Eye, Plus, Trash2, Clock, Globe, Shield, Loader2 } from 'lucide-react';

interface WatchlistsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectTopic?: (topic: string) => void;
}

export const WatchlistsModal: React.FC<WatchlistsModalProps> = ({
  isOpen,
  onClose,
  onSelectTopic,
}) => {
  const { data: watchlists = [], isLoading } = useNewsWatchlists();
  const createMutation = useCreateNewsWatchlist();
  const deleteMutation = useDeleteNewsWatchlist();

  const [isCreating, setIsCreating] = useState(false);
  const [topicQuery, setTopicQuery] = useState('');
  const [entitiesStr, setEntitiesStr] = useState('');
  const [domainsStr, setDomainsStr] = useState('');
  const [intervalHours, setIntervalHours] = useState(6);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topicQuery.trim()) return;

    const monitored_entities = entitiesStr
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean);
    const monitored_domains = domainsStr
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean);

    try {
      await createMutation.mutateAsync({
        topic_query: topicQuery.trim(),
        monitored_entities,
        monitored_domains,
        check_interval_hours: intervalHours,
      });
      setTopicQuery('');
      setEntitiesStr('');
      setDomainsStr('');
      setIsCreating(false);
    } catch (err) {
      console.error('Failed to create watchlist', err);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteMutation.mutateAsync(id);
    } catch (err) {
      console.error('Failed to delete watchlist', err);
    }
  };

  return (
    <Dialog
      isOpen={isOpen}
      onClose={onClose}
      title="Scoped Topic Watchlists"
      description="Monitor critical queries, entities, and sources with scheduled background intelligence sweeps."
      maxWidth="max-w-2xl"
    >
      <div className="space-y-4">
        {/* Header action */}
        <div className="flex items-center justify-between pb-2 border-b border-slate-200 dark:border-slate-800">
          <span className="text-xs font-medium text-slate-500 dark:text-slate-400">
            {watchlists.length} active topic watchlists
          </span>
          {!isCreating && (
            <Button
              size="sm"
              variant="outline"
              onClick={() => setIsCreating(true)}
              className="text-xs text-emerald-600 dark:text-emerald-400 border-emerald-500/30 hover:bg-emerald-500/10"
            >
              <Plus className="w-3.5 h-3.5 mr-1" />
              New Topic Watchlist
            </Button>
          )}
        </div>

        {/* Create Form */}
        {isCreating && (
          <form
            onSubmit={handleCreate}
            className="p-4 rounded-xl border border-emerald-500/30 bg-emerald-500/5 space-y-3"
          >
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-bold text-slate-900 dark:text-slate-100 flex items-center space-x-1.5">
                <Eye className="w-3.5 h-3.5 text-emerald-500" />
                <span>Create Scoped Watchlist</span>
              </h4>
              <button
                type="button"
                onClick={() => setIsCreating(false)}
                className="text-xs text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
              >
                Cancel
              </button>
            </div>

            <div>
              <label className="block text-[11px] font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Topic Query (Root Scope) *
              </label>
              <input
                type="text"
                value={topicQuery}
                onChange={(e) => setTopicQuery(e.target.value)}
                placeholder="e.g., India election EVM or Chennai flood viral video"
                required
                className="w-full px-3 py-1.5 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-[11px] font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Monitored Entities (comma-separated)
                </label>
                <input
                  type="text"
                  value={entitiesStr}
                  onChange={(e) => setEntitiesStr(e.target.value)}
                  placeholder="e.g. Election Commission, EVM"
                  className="w-full px-3 py-1.5 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Specific Outlets / Domains
                </label>
                <input
                  type="text"
                  value={domainsStr}
                  onChange={(e) => setDomainsStr(e.target.value)}
                  placeholder="e.g. reuters.com, ndtv.com"
                  className="w-full px-3 py-1.5 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>
            </div>

            <div className="flex items-center justify-between pt-1">
              <div className="flex items-center space-x-2 text-xs text-slate-600 dark:text-slate-400">
                <Clock className="w-3.5 h-3.5" />
                <span>Check Interval:</span>
                <select
                  value={intervalHours}
                  onChange={(e) => setIntervalHours(Number(e.target.value))}
                  className="px-2 py-1 text-xs rounded border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900"
                >
                  <option value={1}>Every 1 hour</option>
                  <option value={3}>Every 3 hours</option>
                  <option value={6}>Every 6 hours</option>
                  <option value={12}>Every 12 hours</option>
                  <option value={24}>Every 24 hours</option>
                </select>
              </div>

              <Button
                type="submit"
                size="sm"
                disabled={createMutation.isPending}
                className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs"
              >
                {createMutation.isPending ? 'Saving...' : 'Activate Watchlist'}
              </Button>
            </div>
          </form>
        )}

        {/* List */}
        {isLoading ? (
          <div className="py-8 flex items-center justify-center space-x-2 text-xs text-slate-400">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>Loading watchlists...</span>
          </div>
        ) : watchlists.length === 0 ? (
          <div className="py-8 text-center text-xs text-slate-400">
            No active topic watchlists. Create one above to automatically track developments.
          </div>
        ) : (
          <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
            {watchlists.map((w) => (
              <div
                key={w.id}
                className="p-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50 hover:border-slate-300 dark:hover:border-slate-700 transition-colors flex items-start justify-between"
              >
                <div className="space-y-1.5">
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-bold text-slate-900 dark:text-slate-100 font-mono">
                      {w.topic_query}
                    </span>
                    <Badge variant="outline" className="text-[10px] text-emerald-600 border-emerald-500/30">
                      ACTIVE
                    </Badge>
                  </div>

                  <div className="flex flex-wrap items-center gap-1.5 text-[11px] text-slate-500 dark:text-slate-400">
                    <span className="flex items-center space-x-1">
                      <Clock className="w-3 h-3" />
                      <span>Every {w.check_interval_hours}h</span>
                    </span>
                    <span>•</span>
                    <span>Created by {w.created_by}</span>
                  </div>

                  {(w.monitored_entities.length > 0 || w.monitored_domains.length > 0) && (
                    <div className="flex flex-wrap gap-1 pt-1">
                      {w.monitored_entities.map((ent) => (
                        <span
                          key={ent}
                          className="px-1.5 py-0.5 rounded text-[10px] bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300"
                        >
                          {ent}
                        </span>
                      ))}
                      {w.monitored_domains.map((dom) => (
                        <span
                          key={dom}
                          className="px-1.5 py-0.5 rounded text-[10px] bg-sky-500/10 text-sky-600 dark:text-sky-400 border border-sky-500/20"
                        >
                          {dom}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <div className="flex items-center space-x-1 ml-3 shrink-0">
                  {onSelectTopic && (
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => {
                        onSelectTopic(w.topic_query);
                        onClose();
                      }}
                      className="text-xs text-emerald-600 hover:text-emerald-700 h-7 px-2"
                    >
                      Search Now
                    </Button>
                  )}
                  <button
                    onClick={() => handleDelete(w.id)}
                    disabled={deleteMutation.isPending}
                    className="p-1.5 text-slate-400 hover:text-rose-500 dark:hover:text-rose-400 transition-colors"
                    title="Delete Watchlist"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Dialog>
  );
};

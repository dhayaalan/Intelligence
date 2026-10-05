import React, { useState, useMemo } from 'react';
import { ToolItem } from '../../core/api/hooks';
import { ToolCard } from './ToolCard';
import { SearchInput } from '../common/SearchInput';
import { FilterBar, FilterOption } from '../common/FilterBar';
import { EmptyState } from '../common/EmptyState';
import { Wrench } from 'lucide-react';

export interface ToolGridProps {
  tools: ToolItem[];
  onRunTool?: (tool: ToolItem) => void;
  onConfigureTool?: (tool: ToolItem) => void;
  onViewDetails?: (tool: ToolItem) => void;
  className?: string;
}

export const ToolGrid: React.FC<ToolGridProps> = ({
  tools,
  onRunTool,
  onConfigureTool,
  onViewDetails,
  className = '',
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [selectedStatus, setSelectedStatus] = useState('ALL');

  const categories = useMemo(() => {
    const counts: Record<string, number> = {};
    tools.forEach((t) => {
      counts[t.category] = (counts[t.category] || 0) + 1;
    });

    const opts: FilterOption[] = [
      { label: 'All Categories', value: 'ALL', count: tools.length },
    ];
    Object.keys(counts)
      .sort()
      .forEach((cat) => {
        opts.push({ label: cat, value: cat, count: counts[cat] });
      });
    return opts;
  }, [tools]);

  const statusOptions: FilterOption[] = [
    { label: 'All', value: 'ALL' },
    { label: 'Available', value: 'AVAILABLE' },
    { label: 'Config Required', value: 'CONFIG_REQUIRED' },
  ];

  const filteredTools = useMemo(() => {
    return tools.filter((tool) => {
      const matchesSearch =
        !searchQuery ||
        tool.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        tool.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        tool.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
        tool.provider.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesCat =
        selectedCategory === 'ALL' || tool.category === selectedCategory;

      const matchesStatus =
        selectedStatus === 'ALL' || tool.status === selectedStatus;

      return matchesSearch && matchesCat && matchesStatus;
    });
  }, [tools, searchQuery, selectedCategory, selectedStatus]);

  const hasActiveFilters =
    Boolean(searchQuery) ||
    selectedCategory !== 'ALL' ||
    selectedStatus !== 'ALL';

  const handleClearFilters = () => {
    setSearchQuery('');
    setSelectedCategory('ALL');
    setSelectedStatus('ALL');
  };

  return (
    <div className={`space-y-4 ${className}`}>
      <div className="flex flex-col sm:flex-row gap-3">
        <SearchInput
          value={searchQuery}
          onChange={setSearchQuery}
          placeholder="Filter tools by capability, category, or engine..."
          className="flex-1"
        />
      </div>

      <FilterBar
        categories={categories}
        selectedCategory={selectedCategory}
        onSelectCategory={setSelectedCategory}
        statusOptions={statusOptions}
        selectedStatus={selectedStatus}
        onSelectStatus={setSelectedStatus}
        hasActiveFilters={hasActiveFilters}
        onClearFilters={handleClearFilters}
        extraControls={
          <span className="text-xs text-muted-foreground font-mono">
            {filteredTools.length} / {tools.length} Tools
          </span>
        }
      />

      {filteredTools.length === 0 ? (
        <EmptyState
          icon={Wrench}
          title="No tools match filters"
          description="Adjust your search query or selected category to inspect other available engines."
          action={
            hasActiveFilters ? (
              <button
                type="button"
                onClick={handleClearFilters}
                className="text-xs text-primary hover:underline"
              >
                Clear all active filters
              </button>
            ) : undefined
          }
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredTools.map((tool) => (
            <ToolCard
              key={tool.id}
              tool={tool}
              onRun={onRunTool}
              onConfigure={onConfigureTool}
              onViewDetails={onViewDetails}
            />
          ))}
        </div>
      )}
    </div>
  );
};

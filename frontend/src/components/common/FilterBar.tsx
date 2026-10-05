import React from 'react';
import { Filter, X } from 'lucide-react';
import { Button } from '../ui/Button';

export interface FilterOption {
  label: string;
  value: string;
  count?: number;
}

export interface FilterBarProps {
  categories?: FilterOption[];
  selectedCategory?: string;
  onSelectCategory?: (category: string) => void;
  statusOptions?: FilterOption[];
  selectedStatus?: string;
  onSelectStatus?: (status: string) => void;
  onClearFilters?: () => void;
  hasActiveFilters?: boolean;
  className?: string;
  extraControls?: React.ReactNode;
}

export const FilterBar: React.FC<FilterBarProps> = ({
  categories = [],
  selectedCategory = 'ALL',
  onSelectCategory,
  statusOptions = [],
  selectedStatus = 'ALL',
  onSelectStatus,
  onClearFilters,
  hasActiveFilters = false,
  className = '',
  extraControls,
}) => {
  return (
    <div
      className={`flex flex-wrap items-center justify-between gap-3 p-2.5 rounded-lg border border-border/60 bg-card/40 ${className}`}
    >
      <div className="flex flex-wrap items-center gap-1.5">
        <div className="flex items-center gap-1 text-xs font-medium text-muted-foreground mr-1.5">
          <Filter className="h-3.5 w-3.5" />
          <span>Filters:</span>
        </div>

        {categories.length > 0 && onSelectCategory && (
          <div className="flex items-center gap-1 overflow-x-auto py-0.5 max-w-xl">
            {categories.map((cat) => {
              const isSelected = selectedCategory === cat.value;
              return (
                <button
                  key={cat.value}
                  type="button"
                  onClick={() => onSelectCategory(cat.value)}
                  className={`px-2.5 py-1 rounded-md text-xs font-medium transition-colors whitespace-nowrap ${
                    isSelected
                      ? 'bg-primary text-primary-foreground shadow-sm'
                      : 'bg-muted/50 text-muted-foreground hover:text-foreground hover:bg-muted'
                  }`}
                >
                  {cat.label}
                  {typeof cat.count === 'number' && (
                    <span
                      className={`ml-1.5 text-[10px] px-1.5 py-0.2 rounded-full ${
                        isSelected
                          ? 'bg-primary-foreground/20 text-primary-foreground'
                          : 'bg-background/80 text-muted-foreground'
                      }`}
                    >
                      {cat.count}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        )}

        {statusOptions.length > 0 && onSelectStatus && (
          <div className="flex items-center gap-1 border-l border-border/60 pl-2 ml-1">
            {statusOptions.map((st) => {
              const isSelected = selectedStatus === st.value;
              return (
                <button
                  key={st.value}
                  type="button"
                  onClick={() => onSelectStatus(st.value)}
                  className={`px-2 py-1 rounded-md text-xs font-medium transition-colors ${
                    isSelected
                      ? 'bg-zinc-800 text-zinc-100 border border-zinc-700'
                      : 'text-muted-foreground hover:text-foreground hover:bg-muted/40'
                  }`}
                >
                  {st.label}
                </button>
              );
            })}
          </div>
        )}

        {hasActiveFilters && onClearFilters && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onClearFilters}
            className="h-7 px-2 text-xs text-muted-foreground hover:text-destructive gap-1 ml-1"
          >
            <X className="h-3 w-3" />
            Clear
          </Button>
        )}
      </div>

      {extraControls && <div className="flex items-center gap-2">{extraControls}</div>}
    </div>
  );
};

import React from 'react';
import { Pagination } from '../ui/Pagination';
import { EmptyState } from './EmptyState';
import { LoadingState } from './LoadingState';

export interface Column<T> {
  key: string;
  header: React.ReactNode;
  render?: (row: T, index: number) => React.ReactNode;
  className?: string;
  headerClassName?: string;
}

export interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  loading?: boolean;
  emptyTitle?: string;
  emptyDescription?: string;
  emptyAction?: React.ReactNode;
  totalItems?: number;
  page?: number;
  pageSize?: number;
  onPageChange?: (page: number) => void;
  onRowClick?: (row: T) => void;
  keyExtractor?: (row: T, index: number) => string | number;
  className?: string;
}

export function DataTable<T>({
  columns,
  data,
  loading = false,
  emptyTitle = 'No records found',
  emptyDescription = 'There are currently no items matching the query criteria.',
  emptyAction,
  totalItems,
  page = 1,
  pageSize = 10,
  onPageChange,
  onRowClick,
  keyExtractor,
  className = '',
}: DataTableProps<T>) {
  if (loading) {
    return <LoadingState />;
  }

  if (!data || data.length === 0) {
    return (
      <EmptyState
        title={emptyTitle}
        description={emptyDescription}
        action={emptyAction}
      />
    );
  }

  const totalPages =
    typeof totalItems === 'number' ? Math.ceil(totalItems / pageSize) : 1;

  return (
    <div className={`space-y-4 ${className}`}>
      <div className="overflow-x-auto rounded-lg border border-border/60 bg-card">
        <table className="w-full text-left text-sm">
          <thead className="bg-muted/40 border-b border-border/60 text-xs uppercase tracking-wider text-muted-foreground font-semibold">
            <tr>
              {columns.map((col) => (
                <th
                  key={col.key}
                  className={`px-4 py-3 ${col.headerClassName || ''}`}
                >
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-border/40">
            {data.map((row, idx) => {
              const rowKey = keyExtractor
                ? keyExtractor(row, idx)
                : (row as any).id || idx;

              return (
                <tr
                  key={rowKey}
                  onClick={() => onRowClick && onRowClick(row)}
                  className={`transition-colors hover:bg-muted/30 ${
                    onRowClick ? 'cursor-pointer' : ''
                  }`}
                >
                  {columns.map((col) => (
                    <td
                      key={col.key}
                      className={`px-4 py-3 text-foreground ${col.className || ''}`}
                    >
                      {col.render
                        ? col.render(row, idx)
                        : (row as any)[col.key] !== undefined
                        ? String((row as any)[col.key])
                        : '-'}
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {typeof totalItems === 'number' && totalPages > 1 && onPageChange && (
        <div className="flex items-center justify-between px-2 pt-2 text-xs text-muted-foreground">
          <span>
            Showing {(page - 1) * pageSize + 1} to{' '}
            {Math.min(page * pageSize, totalItems)} of {totalItems} entries
          </span>
          <Pagination
            currentPage={page}
            totalPages={totalPages}
            totalItems={totalItems}
            pageSize={pageSize}
            onPageChange={onPageChange}
          />
        </div>
      )}
    </div>
  );
}

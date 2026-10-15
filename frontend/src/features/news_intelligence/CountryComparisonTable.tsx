import React, { useState } from 'react';
import { Globe, AlertTriangle, ShieldCheck, CheckCircle2, Search, Filter } from 'lucide-react';
import { CountryComparisonMatrixRow } from '../../core/api/newsHooks';
import { Badge } from '../../components/ui/Badge';
import { cn } from '../../lib/utils';

interface CountryComparisonTableProps {
  rows: CountryComparisonMatrixRow[];
  totalCountriesSearched?: number;
}

export const CountryComparisonTable: React.FC<CountryComparisonTableProps> = ({
  rows,
  totalCountriesSearched = 0,
}) => {
  const [regionFilter, setRegionFilter] = useState<string>('ALL');
  const [searchFilter, setSearchFilter] = useState<string>('');

  if (!rows || rows.length === 0) {
    return null;
  }

  const regions = ['ALL', ...Array.from(new Set(rows.map((r) => r.region).filter(Boolean)))];

  const filteredRows = rows.filter((r) => {
    const matchesRegion = regionFilter === 'ALL' || r.region === regionFilter;
    const matchesQuery =
      !searchFilter ||
      r.country_name.toLowerCase().includes(searchFilter.toLowerCase()) ||
      r.country_code.toLowerCase().includes(searchFilter.toLowerCase()) ||
      r.primary_headline.toLowerCase().includes(searchFilter.toLowerCase());
    return matchesRegion && matchesQuery;
  });

  const reportingCount = rows.filter((r) => r.article_count > 0).length;
  const totalArticles = rows.reduce((acc, r) => acc + r.article_count, 0);

  return (
    <div className="p-5 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#0c101d] shadow-xs space-y-4">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 dark:border-slate-800/80 pb-4">
        <div className="space-y-0.5">
          <div className="flex items-center space-x-2">
            <Globe className="w-4 h-4 text-emerald-500" />
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-800 dark:text-slate-200 font-mono">
              WORLDWIDE COUNTRY COMPARISON MATRIX
            </h3>
            <Badge variant="outline" className="text-[10px] bg-emerald-500/10 text-emerald-600 border-emerald-500/30">
              {reportingCount} of {rows.length} Countries Reporting
            </Badge>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Side-by-side comparative media analysis across national broadcasting editions, source independence, and reporting framing.
          </p>
        </div>

        {/* Region & Text Filter Controls */}
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={searchFilter}
              onChange={(e) => setSearchFilter(e.target.value)}
              placeholder="Filter country or topic..."
              className="pl-8 pr-3 py-1.5 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-1 focus:ring-emerald-500 w-44"
            />
          </div>

          <select
            value={regionFilter}
            onChange={(e) => setRegionFilter(e.target.value)}
            className="px-2.5 py-1.5 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-slate-800 dark:text-slate-200"
          >
            {regions.map((reg) => (
              <option key={reg} value={reg}>
                {reg === 'ALL' ? 'All Regions' : reg}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-slate-100 dark:border-slate-800 text-[10px] font-bold uppercase text-slate-400 tracking-wider">
              <th className="py-2.5 px-3">Country / Territory</th>
              <th className="py-2.5 px-3">Articles & Outlets</th>
              <th className="py-2.5 px-3">Independence</th>
              <th className="py-2.5 px-3">Dominant Framing</th>
              <th className="py-2.5 px-3">Primary National Headline</th>
              <th className="py-2.5 px-3">Observed Gaps / Missing Evidence</th>
              <th className="py-2.5 px-3 text-right">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 font-sans">
            {filteredRows.map((row) => (
              <tr key={row.country_code} className="hover:bg-slate-50/50 dark:hover:bg-slate-900/30 transition-colors">
                {/* Country */}
                <td className="py-3 px-3">
                  <div className="font-semibold text-slate-900 dark:text-slate-100 flex items-center space-x-1.5">
                    <span>{row.country_name}</span>
                    <span className="text-[10px] font-mono text-slate-400">({row.country_code})</span>
                  </div>
                  <div className="text-[10px] text-slate-400">{row.region}</div>
                </td>

                {/* Articles & Outlets */}
                <td className="py-3 px-3">
                  {row.article_count > 0 ? (
                    <div>
                      <span className="font-bold text-slate-800 dark:text-slate-200">
                        {row.article_count}
                      </span>{' '}
                      <span className="text-slate-400">articles</span>
                      <div className="text-[10px] text-slate-500">
                        across {row.source_count} outlet{row.source_count === 1 ? '' : 's'}
                      </div>
                    </div>
                  ) : (
                    <span className="text-slate-400 italic">0 articles indexed</span>
                  )}
                </td>

                {/* Independence */}
                <td className="py-3 px-3">
                  {row.article_count > 0 ? (
                    <div className="space-y-1 w-24">
                      <div className="flex justify-between text-[10px]">
                        <span className="font-mono font-medium">{row.source_independence_score}%</span>
                      </div>
                      <div className="w-full bg-slate-200 dark:bg-slate-700 h-1 rounded-full overflow-hidden">
                        <div
                          className={cn(
                            'h-full rounded-full',
                            row.source_independence_score >= 70
                              ? 'bg-emerald-500'
                              : row.source_independence_score >= 40
                              ? 'bg-amber-500'
                              : 'bg-rose-500'
                          )}
                          style={{ width: `${row.source_independence_score}%` }}
                        />
                      </div>
                    </div>
                  ) : (
                    <span className="text-slate-400 font-mono text-[10px]">—</span>
                  )}
                </td>

                {/* Framing */}
                <td className="py-3 px-3">
                  <Badge
                    variant="outline"
                    className={cn(
                      'text-[10px] font-semibold',
                      row.dominant_framing.includes('CRITICAL')
                        ? 'bg-rose-500/10 text-rose-600 border-rose-500/30'
                        : row.dominant_framing.includes('SUPPORTIVE')
                        ? 'bg-emerald-500/10 text-emerald-600 border-emerald-500/30'
                        : row.dominant_framing.includes('DIPLOMATIC')
                        ? 'bg-sky-500/10 text-sky-600 border-sky-500/30'
                        : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300'
                    )}
                  >
                    {row.dominant_framing}
                  </Badge>
                </td>

                {/* Primary Headline */}
                <td className="py-3 px-3 max-w-xs">
                  <p className="line-clamp-2 text-slate-700 dark:text-slate-300 font-medium">
                    {row.primary_headline}
                  </p>
                  {row.earliest_publication && (
                    <div className="text-[10px] text-slate-400 font-mono mt-0.5">
                      First observed: {row.earliest_publication}
                    </div>
                  )}
                </td>

                {/* Coverage Gaps */}
                <td className="py-3 px-3 max-w-xs">
                  {row.coverage_gaps.length > 0 ? (
                    <div className="space-y-1">
                      {row.coverage_gaps.map((gap, i) => (
                        <div key={i} className="flex items-start space-x-1 text-[10px] text-amber-600 dark:text-amber-400">
                          <AlertTriangle className="w-3 h-3 shrink-0 mt-0.5" />
                          <span>{gap}</span>
                        </div>
                      ))}
                    </div>
                  ) : row.article_count >= 2 ? (
                    <div className="flex items-center space-x-1 text-[10px] text-emerald-600 dark:text-emerald-400">
                      <CheckCircle2 className="w-3 h-3" />
                      <span>Multi-source coverage observed</span>
                    </div>
                  ) : (
                    <span className="text-[10px] text-slate-400 italic">Unassessed / single or zero source</span>
                  )}
                </td>

                {/* Operational Status */}
                <td className="py-3 px-3 text-right">
                  <Badge
                    variant="outline"
                    className={cn(
                      'text-[9px] font-mono font-bold',
                      row.operational_status === 'WORKING_TESTED_REAL'
                        ? 'bg-emerald-500/10 text-emerald-600 border-emerald-500/30'
                        : row.operational_status === 'NO_MATCHING_RESULTS'
                        ? 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border-slate-300 dark:border-slate-700'
                        : row.operational_status === 'NO_SOURCES_CONFIGURED'
                        ? 'bg-amber-500/10 text-amber-600 border-amber-500/30'
                        : row.operational_status === 'UNVERIFIED'
                        ? 'bg-yellow-500/10 text-yellow-600 border-yellow-500/30'
                        : row.operational_status === 'PROVIDER_ERROR' || row.operational_status === 'PROBE_FAILED'
                        ? 'bg-rose-500/10 text-rose-600 border-rose-500/30'
                        : 'bg-slate-100 dark:bg-slate-800 text-slate-500'
                    )}
                  >
                    {row.operational_status}
                  </Badge>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

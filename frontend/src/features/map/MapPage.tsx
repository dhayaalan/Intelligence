import React, { useState, useEffect } from 'react';
import { OsintMapComponent, GeoLocationItem } from './OsintMapComponent';
import { Globe, Search, RefreshCw, Trash2, Crosshair, AlertCircle } from 'lucide-react';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';

export const MapPage: React.FC = () => {
  const [locations, setLocations] = useState<GeoLocationItem[]>([]);
  const [inputTarget, setInputTarget] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Live real geolocation lookup via backend /api/v1/search/geolocate
  const geolocateTarget = async (target: string) => {
    if (!target.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('sential_token') || localStorage.getItem('token') || '';
      const res = await fetch(`/api/v1/search/geolocate?target=${encodeURIComponent(target.trim())}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Could not resolve or geolocate target '${target}'`);
      }

      const data: GeoLocationItem = await res.json();
      setLocations((prev) => {
        // Prevent duplicate IDs
        if (prev.some((loc) => loc.ip === data.ip || (loc.lat === data.lat && loc.lng === data.lng))) {
          return prev;
        }
        return [data, ...prev];
      });
      setInputTarget('');
    } catch (err: any) {
      setError(err.message || 'Geolocation resolution failed');
    } finally {
      setLoading(false);
    }
  };

  // Load real IP/infrastructure entities from the tenant's case database
  const loadEntitiesFromInvestigations = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('sential_token') || localStorage.getItem('token') || '';
      const res = await fetch('/api/v1/entities', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (!res.ok) return;
      const entities = await res.json();
      if (!Array.isArray(entities)) return;

      const ipOrDomainEntities = entities.filter((e: any) =>
        ['ip', 'ipv4', 'domain', 'subdomain'].includes(e.type?.toLowerCase())
      );

      for (const ent of ipOrDomainEntities.slice(0, 5)) {
        await geolocateTarget(ent.value);
      }
    } catch (err: any) {
      setError('Unable to load entities from database');
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    geolocateTarget(inputTarget);
  };

  const clearLocations = () => {
    setLocations([]);
    setError(null);
  };

  return (
    <div className="space-y-4 w-full h-[calc(100vh-8rem)] flex flex-col">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-3 border-b border-zinc-200 dark:border-zinc-800 shrink-0">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-mono text-zinc-500 uppercase tracking-wider">INTELLIGENCE</span>
            <span className="text-zinc-300 dark:text-zinc-700">//</span>
            <span className="text-xs font-mono text-black dark:text-white font-bold">LIVE GEOSPATIAL RADAR</span>
          </div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-zinc-950 dark:text-white flex items-center gap-2 font-sans">
            <Globe className="w-6 h-6 text-zinc-700 dark:text-zinc-300" />
            <span>Geographic Threat Intelligence Mapping</span>
          </h1>
          <p className="text-xs text-zinc-600 dark:text-zinc-400 mt-1">
            Real live spatial distribution of adversary infrastructure, sinkholes, origin IP points, and verified network coordinates.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant="default">{locations.length} Active Pins</Badge>
          {locations.length > 0 && (
            <Button
              variant="outline"
              size="sm"
              onClick={clearLocations}
              className="text-xs text-zinc-500 hover:text-red-600 dark:hover:text-red-400"
            >
              <Trash2 className="w-3.5 h-3.5 mr-1" />
              Clear Radar
            </Button>
          )}
        </div>
      </div>

      {/* Real Live Target Trace Bar */}
      <div className="p-3 bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs shrink-0 font-mono">
        <form onSubmit={handleSearchSubmit} className="flex items-center gap-2 flex-1 max-w-xl">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-zinc-400" />
            <input
              type="text"
              value={inputTarget}
              onChange={(e) => setInputTarget(e.target.value)}
              placeholder="Geolocate live host, domain, or IP (e.g. 8.8.8.8, 1.1.1.1, github.com)..."
              className="w-full pl-9 pr-3 py-1.5 bg-white dark:bg-zinc-950 border border-zinc-300 dark:border-zinc-700 rounded-md text-xs text-zinc-900 dark:text-zinc-100 placeholder:text-zinc-400 focus:outline-none focus:ring-1 focus:ring-zinc-900 dark:focus:ring-zinc-100"
            />
          </div>
          <Button type="submit" variant="default" size="sm" disabled={loading || !inputTarget.trim()}>
            {loading ? (
              <RefreshCw className="w-3.5 h-3.5 animate-spin mr-1" />
            ) : (
              <Crosshair className="w-3.5 h-3.5 mr-1" />
            )}
            Geolocate & Plot
          </Button>
        </form>

        {/* Live Quick Preset Chips */}
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="text-[11px] text-zinc-500">Live Traces:</span>
          {[
            { label: '8.8.8.8 (Google)', val: '8.8.8.8' },
            { label: '1.1.1.1 (Cloudflare)', val: '1.1.1.1' },
            { label: '208.67.222.222 (OpenDNS)', val: '208.67.222.222' },
          ].map((chip) => (
            <button
              key={chip.val}
              type="button"
              onClick={() => geolocateTarget(chip.val)}
              className="px-2 py-1 rounded bg-white hover:bg-zinc-100 dark:bg-zinc-800 dark:hover:bg-zinc-700 text-zinc-700 dark:text-zinc-300 border border-zinc-200 dark:border-zinc-700 text-[11px] transition-colors"
            >
              {chip.label}
            </button>
          ))}
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={loadEntitiesFromInvestigations}
            disabled={loading}
            className="text-[11px] h-7 px-2"
          >
            Import Case IPs
          </Button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-2.5 rounded-lg bg-red-50 border border-red-200 dark:bg-red-950/40 dark:border-red-900 text-red-700 dark:text-red-300 text-xs flex items-center gap-2 shrink-0">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Map Radar Container */}
      <div className="flex-1 min-h-[500px]">
        <OsintMapComponent locations={locations} />
      </div>
    </div>
  );
};

export default MapPage;

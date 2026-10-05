import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { Globe, RotateCcw, Crosshair } from 'lucide-react';

export interface GeoLocationItem {
  id: string;
  name: string;
  type: string;
  ip?: string;
  city?: string;
  country?: string;
  countryCode?: string;
  lat: number;
  lng: number;
  threatLevel?: string;
  source?: string;
  timestamp?: string;
  details?: string;
  imageUrl?: string;
}

interface OsintMapProps {
  locations?: GeoLocationItem[];
  onSelectLocation?: (loc: GeoLocationItem) => void;
}

// Custom Leaflet DivIcon generator for intelligence markers
const createCustomMarker = (loc: GeoLocationItem, isSelected: boolean) => {
  const isCctv = loc.type === 'CCTV_SIGHTING' || loc.type.includes('CCTV') || loc.type.includes('ALPR');
  const isMalicious = loc.threatLevel === 'MALICIOUS' || loc.threatLevel === 'CRITICAL' || loc.threatLevel === 'FLAGGED';
  const isSuspicious = loc.threatLevel === 'HIGH' || loc.threatLevel === 'SUSPICIOUS' || loc.threatLevel === 'SURVEILLANCE';

  const markerColor = isCctv
    ? (isMalicious ? '#ef4444' : '#0284c7')
    : isMalicious
    ? '#dc2626'
    : isSuspicious
    ? '#f59e0b'
    : '#18181b';

  const pulseColor = isCctv
    ? (isMalicious ? 'rgba(239, 68, 68, 0.5)' : 'rgba(2, 132, 199, 0.4)')
    : isMalicious
    ? 'rgba(220, 38, 38, 0.4)'
    : isSuspicious
    ? 'rgba(245, 158, 11, 0.4)'
    : 'rgba(24, 24, 27, 0.3)';

  const html = `
    <div style="position: relative; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; cursor: pointer;">
      ${
        isSelected || isMalicious || isCctv
          ? `<div style="position: absolute; width: 34px; height: 34px; border-radius: 9999px; background: ${pulseColor}; animation: ping 1.8s cubic-bezier(0, 0, 0.2, 1) infinite;"></div>`
          : ''
      }
      <div style="
        position: relative;
        width: ${isSelected ? '20px' : isCctv ? '18px' : '14px'};
        height: ${isSelected ? '20px' : isCctv ? '18px' : '14px'};
        border-radius: ${isCctv ? '4px' : '9999px'};
        background: ${markerColor};
        border: 2px solid #ffffff;
        box-shadow: 0 2px 6px rgba(0,0,0,0.35);
        display: flex;
        align-items: center;
        justify-content: center;
        transition: transform 0.2s ease;
      ">
        ${isCctv ? `<span style="color:#ffffff; font-size:9px; font-weight:900; line-height:1;">📷</span>` : ''}
      </div>
      <div style="
        position: absolute;
        bottom: -18px;
        white-space: nowrap;
        background: ${isCctv ? '#0f172a' : '#ffffff'};
        border: 1px solid ${isCctv ? '#334155' : '#d4d4d8'};
        color: ${isCctv ? '#38bdf8' : '#09090b'};
        font-family: monospace;
        font-size: 9.5px;
        font-weight: 700;
        padding: 1px 6px;
        border-radius: 3px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        pointer-events: none;
      ">
        ${loc.name.length > 18 ? loc.name.substring(0, 16) + '…' : loc.name}
      </div>
    </div>
  `;

  return L.divIcon({
    html,
    className: 'osint-leaflet-marker',
    iconSize: [36, 36],
    iconAnchor: [18, 18],
    popupAnchor: [0, -18],
  });
};

// Map controller for programmatic centering & zoom
const MapController: React.FC<{
  locations: GeoLocationItem[];
  selectedLoc: GeoLocationItem | null;
}> = ({ locations, selectedLoc }) => {
  const map = useMap();

  useEffect(() => {
    if (selectedLoc) {
      map.flyTo([selectedLoc.lat, selectedLoc.lng], Math.max(map.getZoom(), 6), {
        duration: 1.2,
      });
    } else if (locations.length > 0) {
      const bounds = L.latLngBounds(locations.map((loc) => [loc.lat, loc.lng]));
      map.fitBounds(bounds, { padding: [60, 60], maxZoom: 8 });
    }
  }, [map, selectedLoc, locations]);

  return null;
};

export const OsintMapComponent: React.FC<OsintMapProps> = ({
  locations = [],
  onSelectLocation,
}) => {
  const [selectedLoc, setSelectedLoc] = useState<GeoLocationItem | null>(locations[0] || null);
  const [isGreyscale, setIsGreyscale] = useState(false);

  // If no geographic locations exist, show the clean empty state
  if (!locations || locations.length === 0) {
    return (
      <div className="h-full min-h-[380px] rounded-lg border border-dashed border-zinc-300 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950 flex flex-col items-center justify-center p-6 text-center">
        <div className="w-12 h-12 rounded-full bg-zinc-200 dark:bg-zinc-800 flex items-center justify-center text-zinc-500 mb-3">
          <Globe className="w-6 h-6" />
        </div>
        <h4 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100 font-sans">
          No geographic intelligence found for this search.
        </h4>
        <p className="text-xs text-zinc-500 max-w-sm mt-1 font-mono">
          Query targets (e.g. non-routable hostnames or unmapped emails) did not resolve to physical IP geolocations or GPS coordinates.
        </p>
      </div>
    );
  }

  const center: [number, number] = [
    locations[0]?.lat || 48.8566,
    locations[0]?.lng || 2.3522,
  ];

  return (
    <div className="flex flex-col h-full rounded-lg border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-[#121215] overflow-hidden shadow-sm">
      {/* Map Controls Header */}
      <div className="flex flex-wrap items-center justify-between p-3 border-b border-zinc-200 dark:border-zinc-800 bg-zinc-50/80 dark:bg-zinc-900/50 text-xs font-mono gap-2">
        <div className="flex items-center gap-2">
          <Globe className="w-4 h-4 text-zinc-700 dark:text-zinc-300" />
          <span className="font-bold text-zinc-950 dark:text-zinc-100">OPENSTREETMAP GEOSPATIAL RADAR</span>
          <Badge variant="default">{locations.length} Endpoints</Badge>
          <span className="text-[10px] text-zinc-600 dark:text-zinc-400 border border-zinc-200 dark:border-zinc-700 px-1.5 py-0.5 rounded bg-white dark:bg-zinc-800">
            OpenStreetMap (No API Key Required)
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsGreyscale(!isGreyscale)}
            className={`px-2 py-1 rounded border text-[11px] font-mono transition-colors ${
              isGreyscale
                ? 'bg-black text-white border-black dark:bg-white dark:text-black dark:border-white'
                : 'bg-white text-zinc-700 border-zinc-200 hover:border-zinc-400 dark:bg-zinc-800 dark:text-zinc-200 dark:border-zinc-700'
            }`}
          >
            {isGreyscale ? 'Tactical Monochrome: ON' : 'Tactical Monochrome: OFF'}
          </button>

          <Button
            variant="secondary"
            size="sm"
            className="h-7 px-2 text-[11px]"
            onClick={() => setSelectedLoc(null)}
          >
            <RotateCcw className="w-3 h-3 mr-1" />
            Fit All Bounds
          </Button>
        </div>
      </div>

      {/* Leaflet Map Canvas */}
      <div className={`relative flex-1 min-h-[440px] w-full bg-zinc-100 ${isGreyscale ? '[&_.leaflet-tile]:filter [&_.leaflet-tile]:grayscale [&_.leaflet-tile]:contrast-125' : ''}`}>
        <MapContainer
          center={center}
          zoom={4}
          scrollWheelZoom={true}
          style={{ width: '100%', height: '100%', minHeight: '440px', zIndex: 1 }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            maxZoom={19}
          />

          <MapController locations={locations} selectedLoc={selectedLoc} />

          {locations.map((loc) => {
            const isSelected = selectedLoc?.id === loc.id;
            return (
              <Marker
                key={loc.id}
                position={[loc.lat, loc.lng]}
                icon={createCustomMarker(loc, isSelected)}
                eventHandlers={{
                  click: () => {
                    setSelectedLoc(loc);
                    onSelectLocation?.(loc);
                  },
                }}
              >
                <Popup className="osint-leaflet-popup">
                  <div className="p-1 space-y-1.5 font-mono text-xs max-w-xs">
                    <div className="flex items-center justify-between gap-2 border-b border-zinc-200 pb-1">
                      <strong className="text-zinc-950 font-bold">{loc.name}</strong>
                      <span
                        className={`text-[9px] px-1.5 py-0.2 rounded font-bold ${
                          loc.threatLevel === 'MALICIOUS'
                            ? 'bg-red-100 text-red-700'
                            : loc.threatLevel === 'SUSPICIOUS'
                            ? 'bg-amber-100 text-amber-800'
                            : 'bg-zinc-100 text-zinc-800'
                        }`}
                      >
                        {loc.threatLevel || 'RESOLVED'}
                      </span>
                    </div>
                    {loc.imageUrl && (
                      <div className="pt-1">
                        <img
                          src={loc.imageUrl}
                          alt={loc.name}
                          className="w-full h-24 object-cover rounded border border-zinc-200"
                        />
                      </div>
                    )}
                    <div className="text-[11px] text-zinc-600 space-y-0.5">
                      <p>Type: <strong className="text-zinc-900">{loc.type}</strong></p>
                      {loc.ip && <p>IP: <strong className="text-zinc-900">{loc.ip}</strong></p>}
                      <p>Location: <strong className="text-zinc-900">{loc.city}, {loc.country}</strong></p>
                      {loc.timestamp && <p>Detected: <strong className="text-emerald-700">{loc.timestamp}</strong></p>}
                      {loc.details && <p>Telemetry: <strong className="text-zinc-800">{loc.details}</strong></p>}
                      <p className="text-zinc-500">GPS: {loc.lat.toFixed(4)}, {loc.lng.toFixed(4)}</p>
                    </div>
                  </div>
                </Popup>
              </Marker>
            );
          })}
        </MapContainer>

        {/* Selected Location Overlay Card */}
        {selectedLoc && (
          <div className="absolute bottom-4 left-4 z-[1000] p-3.5 rounded-lg border border-zinc-200 bg-white/95 dark:bg-[#121215]/95 backdrop-blur-md shadow-xl text-xs space-y-2 font-mono max-w-sm">
            <div className="flex items-center justify-between gap-3">
              <span className="font-bold text-zinc-950 dark:text-zinc-100 flex items-center gap-1.5">
                <Crosshair className="w-3.5 h-3.5 text-zinc-900 dark:text-zinc-200" />
                {selectedLoc.name}
              </span>
              <Badge variant={selectedLoc.threatLevel === 'MALICIOUS' ? 'destructive' : 'warning'}>
                {selectedLoc.threatLevel || 'RESOLVED'}
              </Badge>
            </div>
            {selectedLoc.imageUrl && (
              <div className="rounded overflow-hidden border border-zinc-300 dark:border-zinc-700 max-h-28">
                <img
                  src={selectedLoc.imageUrl}
                  alt={selectedLoc.name}
                  className="w-full h-24 object-cover"
                />
              </div>
            )}
            <div className="text-[11px] text-zinc-600 dark:text-zinc-400 space-y-1">
              <p>Type: <strong className="text-zinc-900 dark:text-zinc-100">{selectedLoc.type}</strong></p>
              {selectedLoc.ip && <p>IP Host: <strong className="text-zinc-900 dark:text-zinc-100">{selectedLoc.ip}</strong></p>}
              <p>Geographic Origin: <strong className="text-zinc-900 dark:text-zinc-100">{selectedLoc.city}, {selectedLoc.country}</strong></p>
              {selectedLoc.timestamp && <p>Sighting Time: <strong className="text-emerald-600 dark:text-emerald-400">{selectedLoc.timestamp}</strong></p>}
              {selectedLoc.details && <p>Telemetry: <strong className="text-zinc-900 dark:text-zinc-100">{selectedLoc.details}</strong></p>}
              <p>Coordinates: <span className="text-zinc-700 dark:text-zinc-300 font-bold">{selectedLoc.lat.toFixed(4)}° N, {selectedLoc.lng.toFixed(4)}° E</span></p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default OsintMapComponent;

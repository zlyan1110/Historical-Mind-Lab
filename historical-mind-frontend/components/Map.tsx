'use client';

import { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { GeoPoint } from '@/types/simulation';

interface LocationHistory {
  location: GeoPoint;
  turn: number;
  timestamp: string;
  stress_level: number;
  action?: string;
  thought?: string;
}

interface MapProps {
  currentLocation?: GeoPoint;
  locationHistory?: LocationHistory[];
  className?: string;
}

export default function Map({ currentLocation, locationHistory = [], className = '' }: MapProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const markers = useRef<mapboxgl.Marker[]>([]);
  const [mapLoaded, setMapLoaded] = useState(false);

  // Initialize map
  useEffect(() => {
    if (!mapContainer.current) return;
    if (map.current) return; // Initialize only once

    mapboxgl.accessToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN || 'pk.eyJ1IjoiZXhhbXBsZSIsImEiOiJjbGV4YW1wbGUifQ.example';

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/streets-v12',
      center: [112.2051, 30.3509], // Center on Jiangling (江陵)
      zoom: 5,
    });

    // Add navigation controls
    map.current.addControl(new mapboxgl.NavigationControl(), 'top-right');

    map.current.on('load', () => {
      setMapLoaded(true);
    });

    // Cleanup
    return () => {
      markers.current.forEach(m => m.remove());
      map.current?.remove();
    };
  }, []);

  // Update trajectory and markers when history changes
  useEffect(() => {
    if (!map.current || !mapLoaded) return;

    // Clear existing markers
    markers.current.forEach(m => m.remove());
    markers.current = [];

    // Remove existing path layer and source
    if (map.current.getLayer('route')) {
      map.current.removeLayer('route');
    }
    if (map.current.getSource('route')) {
      map.current.removeSource('route');
    }

    // If we have location history, draw the path
    if (locationHistory.length > 0) {
      // Create coordinates array for the path
      const coordinates = locationHistory.map(loc => [loc.location.lon, loc.location.lat]);

      // Add the route as a line
      map.current.addSource('route', {
        type: 'geojson',
        data: {
          type: 'Feature',
          properties: {},
          geometry: {
            type: 'LineString',
            coordinates: coordinates,
          },
        },
      });

      map.current.addLayer({
        id: 'route',
        type: 'line',
        source: 'route',
        layout: {
          'line-join': 'round',
          'line-cap': 'round',
        },
        paint: {
          'line-color': '#3b82f6', // Blue color for the path
          'line-width': 4,
          'line-opacity': 0.8,
        },
      });

      // Add markers for each location in history
      locationHistory.forEach((loc, index) => {
        const isFirst = index === 0;
        const isLast = index === locationHistory.length - 1;
        const isCurrent = isLast && currentLocation?.place_name === loc.location.place_name;

        // Color based on stress level and position
        let color = '#3b82f6'; // Default blue
        if (isCurrent) {
          color = '#ef4444'; // Red for current location
        } else if (isFirst) {
          color = '#f59e0b'; // Orange for start
        } else if (loc.stress_level >= 80) {
          color = '#dc2626'; // Dark red for high stress
        } else if (loc.stress_level >= 50) {
          color = '#f97316'; // Orange for medium stress
        } else {
          color = '#22c55e'; // Green for low stress
        }

        // Create marker size based on importance
        const scale = isCurrent ? 1.2 : isFirst ? 1.0 : 0.7;

        // Create popup content
        const popupContent = `
          <div class="p-2">
            <h3 class="font-bold text-sm mb-1">${loc.location.place_name}</h3>
            <p class="text-xs text-gray-600">回合 ${loc.turn} | ${new Date(loc.timestamp).toLocaleString('zh-CN')}</p>
            <p class="text-xs mt-1">
              <span class="font-semibold">压力:</span>
              <span class="font-bold ${
                loc.stress_level >= 80 ? 'text-red-600' :
                loc.stress_level >= 50 ? 'text-yellow-600' :
                'text-green-600'
              }">${loc.stress_level}/100</span>
            </p>
            ${loc.thought ? `<p class="text-xs mt-1"><span class="font-semibold">思考:</span> ${loc.thought}</p>` : ''}
            ${loc.action ? `<p class="text-xs mt-1"><span class="font-semibold">行动:</span> ${loc.action}</p>` : ''}
            ${isFirst ? '<p class="text-xs mt-1 text-orange-600 font-semibold">🏁 起点</p>' : ''}
            ${isCurrent ? '<p class="text-xs mt-1 text-red-600 font-semibold">📍 当前位置</p>' : ''}
          </div>
        `;

        const popup = new mapboxgl.Popup({ offset: 25 }).setHTML(popupContent);

        const marker = new mapboxgl.Marker({
          color: color,
          scale: scale,
        })
          .setLngLat([loc.location.lon, loc.location.lat])
          .setPopup(popup)
          .addTo(map.current!);

        markers.current.push(marker);
      });

      // Fit map to show all markers
      if (coordinates.length > 1) {
        const bounds = coordinates.reduce((bounds, coord) => {
          return bounds.extend(coord as [number, number]);
        }, new mapboxgl.LngLatBounds(coordinates[0] as [number, number], coordinates[0] as [number, number]));

        map.current.fitBounds(bounds, {
          padding: 50,
          maxZoom: 8,
          duration: 1000,
        });
      } else if (coordinates.length === 1) {
        // If only one location, center on it
        map.current.flyTo({
          center: coordinates[0] as [number, number],
          zoom: 8,
          duration: 1000,
        });
      }
    } else if (currentLocation) {
      // No history yet, just show current location
      const color = '#ef4444'; // Red
      const popupContent = `
        <div class="p-2">
          <h3 class="font-bold text-sm">${currentLocation.place_name}</h3>
          <p class="text-xs text-gray-600">${currentLocation.lat.toFixed(4)}, ${currentLocation.lon.toFixed(4)}</p>
          <p class="text-xs mt-1 text-red-600 font-semibold">📍 当前位置</p>
        </div>
      `;

      const marker = new mapboxgl.Marker({ color: color })
        .setLngLat([currentLocation.lon, currentLocation.lat])
        .setPopup(new mapboxgl.Popup({ offset: 25 }).setHTML(popupContent))
        .addTo(map.current);

      markers.current.push(marker);

      map.current.flyTo({
        center: [currentLocation.lon, currentLocation.lat],
        zoom: 8,
        duration: 2000,
      });
    }
  }, [locationHistory, currentLocation, mapLoaded]);

  return (
    <div className="relative w-full h-full">
      <div ref={mapContainer} className={`w-full h-full ${className}`} />
      {!mapLoaded && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading map...</p>
          </div>
        </div>
      )}

      {/* Legend */}
      {locationHistory.length > 0 && (
        <div className="absolute bottom-4 left-4 bg-white px-4 py-3 rounded-lg shadow-lg text-xs">
          <p className="font-bold mb-2">图例</p>
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-orange-500"></div>
              <span>起点</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
              <span>当前位置</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
              <span>低压力 (&lt;50)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-orange-500"></div>
              <span>中压力 (50-79)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-red-600"></div>
              <span>高压力 (≥80)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-8 h-1 bg-blue-500"></div>
              <span>移动路径</span>
            </div>
          </div>
        </div>
      )}

      {/* Current location info */}
      {currentLocation && (
        <div className="absolute top-4 left-4 bg-white px-4 py-2 rounded-lg shadow-lg">
          <p className="text-sm font-semibold text-gray-700">📍 {currentLocation.place_name}</p>
          <p className="text-xs text-gray-500">
            {currentLocation.lat.toFixed(4)}, {currentLocation.lon.toFixed(4)}
          </p>
          {locationHistory.length > 0 && (
            <p className="text-xs text-blue-600 mt-1 font-semibold">
              已访问 {locationHistory.length} 个地点
            </p>
          )}
        </div>
      )}
    </div>
  );
}

'use client';

import { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { GeoPoint } from '@/types/simulation';

interface MapProps {
  currentLocation?: GeoPoint;
  className?: string;
}

export default function Map({ currentLocation, className = '' }: MapProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const marker = useRef<mapboxgl.Marker | null>(null);
  const [mapLoaded, setMapLoaded] = useState(false);

  // Initialize map
  useEffect(() => {
    if (!mapContainer.current) return;
    if (map.current) return; // Initialize only once

    // You need to set your Mapbox access token
    // For development, you can use a public token
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
      marker.current?.remove();
      map.current?.remove();
    };
  }, []);

  // Update marker when location changes
  useEffect(() => {
    if (!map.current || !mapLoaded || !currentLocation) return;

    // Remove old marker
    if (marker.current) {
      marker.current.remove();
    }

    // Create new marker
    marker.current = new mapboxgl.Marker({ color: '#FF0000' })
      .setLngLat([currentLocation.lon, currentLocation.lat])
      .setPopup(
        new mapboxgl.Popup({ offset: 25 }).setHTML(
          `<h3 class="font-bold">${currentLocation.place_name}</h3><p>Lat: ${currentLocation.lat.toFixed(4)}, Lon: ${currentLocation.lon.toFixed(4)}</p>`
        )
      )
      .addTo(map.current);

    // Fly to new location
    map.current.flyTo({
      center: [currentLocation.lon, currentLocation.lat],
      zoom: 8,
      duration: 2000,
    });
  }, [currentLocation, mapLoaded]);

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
      {currentLocation && (
        <div className="absolute top-4 left-4 bg-white px-4 py-2 rounded-lg shadow-lg">
          <p className="text-sm font-semibold text-gray-700">📍 {currentLocation.place_name}</p>
          <p className="text-xs text-gray-500">
            {currentLocation.lat.toFixed(4)}, {currentLocation.lon.toFixed(4)}
          </p>
        </div>
      )}
    </div>
  );
}

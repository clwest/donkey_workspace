import { useEffect, useState } from 'react';
import apiFetch from '@/utils/apiClient';

export function parseOverlayResults(data) {
  return data?.results || [];
}

export async function fetchGlossaryOverlay(location) {
  const data = await apiFetch('/terms/glossary_overlay/', { params: { location } });
  return parseOverlayResults(data);
}

export default function useGlossaryOverlay(location) {
  const [overlays, setOverlays] = useState([]);
  const [paused, setPaused] = useState(false);

  const load = async () => {
    if (!location) return;
    try {
      const data = await fetchGlossaryOverlay(location);
      setOverlays(data);
      setPaused(false);
    } catch (err) {
      console.error('overlay fetch', err);
      if (err.status === 429) setPaused(true);
    }
  };

  useEffect(() => {
    load();
  }, [location]);

  return { overlays, paused, refresh: load };
}

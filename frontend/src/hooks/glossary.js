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

  useEffect(() => {
    if (!location) return;
    fetchGlossaryOverlay(location)
      .then(setOverlays)
      .catch((err) => console.error('overlay fetch', err));
  }, [location]);

  return overlays;
}

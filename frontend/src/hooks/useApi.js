import { useEffect, useState } from 'react';
import apiFetch from '@/utils/apiClient';

export default function useApi(url) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [backoff, setBackoff] = useState(0);

  useEffect(() => {
    let active = true;
    const load = async () => {
      try {
        const res = await apiFetch(url);
        if (!active) return;
        setData(res);
        setError(null);
        setBackoff(0);
      } catch (err) {
        if (!active) return;
        setError(err);
        if (err.status === 429) {
          const wait = err.retryAfter || 30;
          const next = Math.min(wait * (backoff + 1), 60);
          setBackoff(next);
          setTimeout(load, next * 1000);
        }
      }
    };
    load();
    return () => {
      active = false;
    };
  }, [url]);

  return { data, error };
}

import { useEffect, useState } from 'react';
import apiFetch from '@/utils/apiClient';

export default function useApi(url) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let active = true;
    apiFetch(url)
      .then((res) => {
        if (active) setData(res);
      })
      .catch((err) => {
        console.error('useApi error', err);
        if (active) setError(err);
      });
    return () => {
      active = false;
    };
  }, [url]);

  return { data, error };
}

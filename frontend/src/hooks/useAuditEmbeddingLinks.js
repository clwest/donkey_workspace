import { useEffect, useState } from 'react';
import apiFetch from '@/utils/apiClient';

export default function useAuditEmbeddingLinks() {
  const [rows, setRows] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let active = true;
    apiFetch('/dev/embedding-audit/')
      .then((res) => {
        if (active) setRows(res.context_audit || []);
      })
      .catch((err) => {
        if (active) setError(err);
      });
    return () => {
      active = false;
    };
  }, []);

  return { rows, error };
}

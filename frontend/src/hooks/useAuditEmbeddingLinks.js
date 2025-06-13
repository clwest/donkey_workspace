import { useEffect, useState } from 'react';
import apiFetch from '@/utils/apiClient';

export default function useAuditEmbeddingLinks() {
  const [rows, setRows] = useState(null);
  const [error, setError] = useState(null);

  const load = () => {
    return apiFetch('/dev/embedding-audit/')
      .then((res) => {
        setRows(res.context_audit || []);
      })
      .catch((err) => {
        setError(err);
      });
  };

  useEffect(() => {
    load();
  }, []);

  return { rows, error, reload: load };
}

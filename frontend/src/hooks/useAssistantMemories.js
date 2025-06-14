import { useState, useMemo, useEffect } from 'react';
import useSWR from 'swr';
import debounce from 'lodash/debounce';
import apiFetch from '@/utils/apiClient';

const fetcher = (url) => apiFetch(url);

export default function useAssistantMemories(slug, opts = {}) {
  const { limit: initialLimit = 50, offset: initialOffset = 0 } = opts;
  const [params, setParams] = useState({ limit: initialLimit, offset: initialOffset });

  const query = useMemo(() => {
    return `limit=${params.limit}&offset=${params.offset}`;
  }, [params]);

  const key = slug ? `/assistants/${slug}/memories/?${query}` : null;
  const { data, error, mutate, isValidating } = useSWR(key, fetcher, {
    dedupingInterval: 3000,
    revalidateOnFocus: false,
  });

  // Debounced manual refresh
  const refresh = useMemo(() => debounce(() => mutate(), 3000, { leading: true }), [mutate]);

  const memories = data?.results || data || [];
  const totalCount = data?.total_count ?? memories.length;

  const nextPage = () => setParams(p => ({ ...p, offset: p.offset + p.limit }));
  const prevPage = () => setParams(p => ({ ...p, offset: Math.max(0, p.offset - p.limit) }));

  useEffect(() => {
    setParams({ limit: initialLimit, offset: initialOffset });
  }, [slug, initialLimit, initialOffset]);

  return {
    memories,
    totalCount,
    loading: !data && !error,
    error,
    isValidating,
    refresh,
    limit: params.limit,
    offset: params.offset,
    nextPage,
    prevPage,
    hasMore: totalCount > params.offset + memories.length,
  };
}

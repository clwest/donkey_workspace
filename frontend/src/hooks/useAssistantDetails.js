import { useMemo } from "react";
import useSWR from "swr";
import useAssistantMemories from "./useAssistantMemories";
import apiFetch from "@/utils/apiClient";

const fetcher = (url) => apiFetch(url);

export default function useAssistantDetails(slug, opts = {}) {
  const { pauseOnError = true, limit = 50, offset = 0 } = opts;

  const {
    memories,
    totalCount,
    refresh: refreshMemories,
    isValidating: memoriesValidating,
    error: memoriesError,
  } = useAssistantMemories(slug, { limit, offset });

  const swrConfig = useMemo(
    () => ({
      dedupingInterval: 3000,
      revalidateOnFocus: false,
      shouldRetryOnError: (err) => {
        if (err?.status === 429) return !pauseOnError;
        if (err?.status >= 500) return false;
        return true;
      },
    }),
    [pauseOnError],
  );

  const {
    data: reflections,
    error: reflectionsError,
    mutate: refreshReflections,
  } = useSWR(
    slug ? `/assistants/${slug}/recent-reflections/` : null,
    fetcher,
    swrConfig,
  );

  const {
    data: trustProfile,
    error: profileError,
    mutate: refreshProfile,
  } = useSWR(slug ? `/assistants/${slug}/trust_profile/` : null, fetcher, swrConfig);

  const { data: diagnostics, mutate: refreshDiagnostics } = useSWR(
    slug ? `/assistants/${slug}/diagnostic_report/` : null,
    fetcher,
    swrConfig,
  );

  const paused =
    memoriesError?.status === 429 ||
    reflectionsError?.status === 429 ||
    profileError?.status >= 500;

  const refreshAll = () => {
    refreshMemories();
    refreshReflections();
    refreshProfile();
    refreshDiagnostics();
  };

  return {
    memories,
    totalCount,
    reflections: reflections || [],
    trustProfile,
    diagnostics,
    loading:
      memoriesValidating && !memories?.length &&
      !memoriesError &&
      !reflections &&
      !trustProfile &&
      !diagnostics,
    paused,
    refreshAll,
  };
}


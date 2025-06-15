import useSWR from "swr";
import apiFetch from "@/utils/apiClient";

const fetcher = (url) => apiFetch(url);

export default function useAssistantCardData(slug, { enabled = false } = {}) {
  const { data: profile } = useSWR(
    slug ? `/assistants/${slug}/trust_profile/` : null,
    fetcher,
    { dedupingInterval: 3000 },
  );

  const diagKey =
    slug && enabled ? `/assistants/${slug}/diagnostic_report/` : null;
  const { data: diagnostic } = useSWR(diagKey, fetcher, {
    dedupingInterval: 3000,
  });

  const memKey = slug && enabled ? `/assistants/${slug}/memories/` : null;
  const { data: memData, error: memError } = useSWR(memKey, fetcher, {
    dedupingInterval: 3000,
  });

  let memoryStatus = null;
  if (memData) memoryStatus = "hydrated";
  if (memError) {
    memoryStatus = memError.status === 429 ? "paused" : "error";
  }

  return {
    profile,
    diagnostic,
    memories: memData?.results || memData,
    memoryStatus,
  };
}

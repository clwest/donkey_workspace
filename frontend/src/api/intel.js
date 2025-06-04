import apiFetch from "../utils/apiClient";

export const fetchChunkStats = (params) =>
  apiFetch(`/intel/chunk-stats/`, { params });

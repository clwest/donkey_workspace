import apiFetch from "../utils/apiClient";

export const searchDocumentChunks = (query, assistantId) =>
  apiFetch("/embeddings/search/", {
    method: "POST",
    body: {
      text: query,
      target: "documentchunk",
      assistant_id: assistantId,
      top_k: 3,
    },
  });

export const storeMemoryFromChat = (content, tags = []) =>
  apiFetch("/memory/entries/", {
    method: "POST",
    body: { event: content, tags },
  });

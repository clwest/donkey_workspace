import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import apiFetch from "@/utils/apiClient";
import IdentityGlyphPreview from "@/components/assistant/IdentityGlyphPreview";

export default function AssistantIdentityPage() {
  const { id } = useParams();
  const [anchor, setAnchor] = useState(null);

  useEffect(() => {
    apiFetch(`/assistants/${id}/identity/`)
      .then(setAnchor)
      .catch((err) => {
        console.error('Failed to fetch identity', err);
        setAnchor(null);
      });
  }, [id]);

  if (!anchor) return <div>Loading...</div>;

  return (
    <div className="container my-4">
      <h1 className="mb-3">Identity Anchor</h1>
      <IdentityGlyphPreview vector={anchor.codex_vector} />
      <div className="mt-2">Memory Origin: {anchor.memory_origin}</div>
    </div>
  );
}

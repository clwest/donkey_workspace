import { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";

export default function AssistantReplayDiffPage() {
  const { slug, uuid } = useParams();
  const [data, setData] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    apiFetch(`/assistants/${slug}/replays/${uuid}/diff/`)
      .then((res) => setData(res))
      .catch(() => setData(null));
  }, [slug, uuid]);

  const accept = async () => {
    await apiFetch(`/replays/${uuid}/accept/`, { method: "POST" });
    navigate(`/assistants/${slug}/replays`);
  };

  const reject = async () => {
    await apiFetch(`/replays/${uuid}/reject/`, { method: "POST" });
    navigate(`/assistants/${slug}/replays`);
  };

  if (!data) return <div className="container my-5">Loading...</div>;

  return (
    <div className="container my-5">
      <h2 className="mb-4">Replay Diff</h2>
      <div className="row">
        <div className="col-6">
          <h5>Original</h5>
          <pre className="border p-2" style={{ whiteSpace: "pre-wrap" }}>{data.original}</pre>
        </div>
        <div className="col-6">
          <h5>Replayed</h5>
          <pre className="border p-2" style={{ whiteSpace: "pre-wrap" }}>{data.replayed}</pre>
        </div>
      </div>
      <div className="my-3" dangerouslySetInnerHTML={{ __html: data.diff_html }} />
      <p>
        <strong>Glossary changes:</strong>{" "}
        {data.glossary_terms_changed.join(", ") || "None"}
      </p>
      <p>
        <strong>Anchor Overlap:</strong> {data.anchor_overlap.toFixed(2)}
        {" | "}
        <strong>Change Score:</strong> {data.change_score.toFixed(2)}
      </p>
      <button onClick={accept} className="btn btn-success me-2">
        Accept
      </button>
      <button onClick={reject} className="btn btn-danger me-2">
        Reject
      </button>
      <Link to={`/assistants/${slug}/replays`} className="btn btn-secondary">
        Back
      </Link>
    </div>
  );
}

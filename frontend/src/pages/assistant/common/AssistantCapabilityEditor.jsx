import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { toast } from "react-toastify";
import apiFetch from "../../../utils/apiClient";

export default function AssistantCapabilityEditor() {
  const { slug } = useParams();
  const [capabilities, setCapabilities] = useState({
    can_train_glossary: true,
    can_run_reflection: true,
    can_delegate_tasks: true,
    can_ingest_docs: true,
    can_embed: true,
    can_self_fork: false,
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const data = await apiFetch(`/assistants/${slug}/`);
        setCapabilities((prev) => ({ ...prev, ...(data.capabilities || {}) }));
      } catch (err) {
        toast.error("Failed to load capabilities");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [slug]);

  const handleToggle = (key) => {
    setCapabilities((caps) => ({ ...caps, [key]: !caps[key] }));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const body = { capabilities };
      const data = await apiFetch(`/assistants/${slug}/`, {
        method: "PATCH",
        body,
      });
      setCapabilities(data.capabilities || {});
      toast.success("Capabilities updated");
    } catch (err) {
      toast.error("Failed to save capabilities");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="container my-5">
      <h1 className="mb-4">Assistant Capabilities</h1>
      <div className="mb-3">
        <Link to={`/assistants/${slug}`} className="btn btn-secondary">
          ← Back to Assistant
        </Link>
      </div>
      <div className="mb-4">
        {[
          ["can_train_glossary", "Train Glossary"],
          ["can_run_reflection", "Run Reflections"],
          ["can_delegate_tasks", "Delegate Tasks"],
          ["can_ingest_docs", "Ingest Documents"],
          ["can_embed", "Embed"],
          ["can_self_fork", "Self Fork"],
        ].map(([key, label]) => (
          <div className="form-check form-switch mb-2" key={key}>
            <input
              className="form-check-input"
              type="checkbox"
              id={key}
              checked={!!capabilities[key]}
              onChange={() => handleToggle(key)}
            />
            <label className="form-check-label" htmlFor={key}>
              {label}
            </label>
          </div>
        ))}
      </div>
      <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
        {saving ? "Saving..." : "Save"}
      </button>
      <h5 className="mt-4">Current JSON</h5>
      <pre>{JSON.stringify(capabilities, null, 2)}</pre>
    </div>
  );
}

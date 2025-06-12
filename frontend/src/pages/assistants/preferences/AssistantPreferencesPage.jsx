import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import apiFetch from "@/utils/apiClient";
import useAuthGuard from "@/hooks/useAuthGuard";

export default function AssistantPreferencesPage() {
  useAuthGuard();
  const { slug } = useParams();
  const [prefs, setPrefs] = useState(null);
  const [saving, setSaving] = useState(false);
  const [tone, setTone] = useState("friendly");
  const [planning, setPlanning] = useState("short_term");
  const [tagInput, setTagInput] = useState("");
  const [tags, setTags] = useState([]);
  const [selfNarration, setSelfNarration] = useState(false);

  useEffect(() => {
    apiFetch(`/assistants/${slug}/preferences/`).then((res) => {
      setPrefs(res);
      setTone(res.tone);
      setPlanning(res.planning_mode);
      setTags(res.custom_tags || []);
      setSelfNarration(res.self_narration_enabled || false);
    });
  }, [slug]);

  const save = async () => {
    setSaving(true);
    try {
      const body = { tone, planning_mode: planning, custom_tags: tags, self_narration_enabled: selfNarration };
      const res = await apiFetch(`/assistants/${slug}/preferences/`, {
        method: "PATCH",
        body,
      });
      setPrefs(res);
      setSelfNarration(res.self_narration_enabled || false);
    } finally {
      setSaving(false);
    }
  };

  if (!prefs) return <div className="container my-5">Loading...</div>;

  const addTag = () => {
    if (!tagInput.trim()) return;
    if (!tags.includes(tagInput.trim())) setTags([...tags, tagInput.trim()]);
    setTagInput("");
  };

  return (
    <div className="container my-5" id="preferences-page">
      <h1 className="mb-4">Assistant Preferences</h1>
      <p className="text-muted">Linked User: {prefs.username}</p>
      <div className="mb-3" style={{ maxWidth: 400 }}>
        <label className="form-label">Tone</label>
        <select
          className="form-select"
          value={tone}
          onChange={(e) => setTone(e.target.value)}
        >
          <option value="friendly">Friendly</option>
          <option value="formal">Formal</option>
          <option value="playful">Playful</option>
        </select>
      </div>
      <div className="mb-3" style={{ maxWidth: 400 }}>
        <label className="form-label">Planning Mode</label>
        <select
          className="form-select"
          value={planning}
          onChange={(e) => setPlanning(e.target.value)}
        >
          <option value="short_term">Short Term</option>
          <option value="long_term">Long Term</option>
        </select>
      </div>
      <div className="mb-3" style={{ maxWidth: 400 }}>
        <label className="form-label">Favorite Tags</label>
        <div className="d-flex mb-2">
          <input
            className="form-control"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
          />
          <button className="btn btn-secondary ms-2" onClick={addTag}>
            Add
          </button>
        </div>
        {tags.length > 0 && (
          <div className="d-flex flex-wrap gap-1">
            {tags.map((t) => (
              <span key={t} className="badge bg-primary">
                {t}
              </span>
            ))}
          </div>
        )}
      </div>
      <div className="form-check mb-3">
        <input
          className="form-check-input"
          type="checkbox"
          id="selfNarrationToggle"
          checked={selfNarration}
          onChange={(e) => setSelfNarration(e.target.checked)}
        />
        <label className="form-check-label" htmlFor="selfNarrationToggle">
          Enable Self-Narration
        </label>
      </div>
      <button className="btn btn-primary" disabled={saving} onClick={save}>
        {saving ? "Saving..." : "Save Preferences"}
      </button>
    </div>
  );
}

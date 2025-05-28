// frontend/pages/assistant/EditAssistantPage.jsx

import { useEffect, useState } from "react";
import { useNavigate, useLocation, useParams } from "react-router-dom";
import { toast } from "react-toastify";
import PromptIdeaGenerator from "../../../components/prompts/PromptIdeaGenerator";

const mythDefaults = {
  memory: {
    tone: "reflective",
    tag: "memory",
    personality: "Reflects on past events and contextual cues.",
  },
  codex: {
    tone: "precise",
    tag: "codex",
    personality:
      "Embodies symbolic law, codified behavior, and structured ritual logic.",
  },
  ritual: {
    tone: "observant",
    tag: "ritual",
    personality:
      "Observes, records, and reacts to symbolic rituals and emergent patterns.",
  },
};

const mythSummaries = {
  memory: { emoji: "🧠", desc: "Memory Seeker" },
  codex: { emoji: "📜", desc: "Codex Explorer" },
  ritual: { emoji: "🌀", desc: "Ritual Witness" },
};

export default function EditAssistantPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { slug } = useParams();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [specialty, setSpecialty] = useState("");
  const [avatar, setAvatar] = useState("");
  const [systemPromptId, setSystemPromptId] = useState("");
  const [prompts, setPrompts] = useState([]);
  const [personality, setPersonality] = useState("");
  const [tone, setTone] = useState("");
  const [preferredModel, setPreferredModel] = useState("gpt-4o");
  const [saving, setSaving] = useState(false);
  const [mythpath, setMythpath] = useState(
    location.state?.mythpath || "custom"
  );
  const lockedPath = Boolean(location.state?.mythpath);

  useEffect(() => {
    async function fetchPrompts() {
      try {
        const res = await fetch("/api/prompts/?type=system&show_all=true");
        const data = await res.json();
        setPrompts(data);
      } catch (err) {
        console.error("Failed to load prompts", err);
        toast.error("❌ Failed to load prompts.");
      }
    }
    fetchPrompts();

    async function fetchAssistant() {
      try {
        const res = await fetch(`/api/assistants/${slug}/`);
        const data = await res.json();
        if (res.ok) {
          setName(data.name || "");
          setDescription(data.description || "");
          setSpecialty(data.specialty || "");
          setAvatar(data.avatar || "");
          setSystemPromptId(data.system_prompt?.id || "");
          setPersonality(data.personality || "");
          setTone(data.tone || "");
          setPreferredModel(data.preferred_model || "gpt-4o");
        }
      } catch (err) {
        console.error("Failed to load assistant", err);
      }
    }
    if (slug) fetchAssistant();
  }, []);

  useEffect(() => {
    if (mythDefaults[mythpath]) {
      setTone(mythDefaults[mythpath].tone);
      setSpecialty(mythDefaults[mythpath].tag);
      if (mythDefaults[mythpath].personality) {
        setPersonality(mythDefaults[mythpath].personality);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mythpath]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const res = await fetch(`/api/assistants/${slug}/`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name,
          description,
          specialty,
          avatar,
          system_prompt: systemPromptId,
          personality,
          tone,
          preferred_model: preferredModel,
        }),
      });
      const data = await res.json();
      if (res.ok) {
        toast.success("✅ Assistant updated!");
        navigate(`/assistants/${data.slug}`);
      } else {
        toast.error("❌ Failed to update assistant.");
      }
    } catch (err) {
      console.error("Error updating assistant:", err);
      toast.error("❌ Server error.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="container my-5">
      <h1 className="mb-4">🧠 Edit Assistant</h1>
      <div className="mb-3">
        <label className="form-label">Mythpath</label>
        <select
          className="form-select"
          value={mythpath}
          onChange={(e) => setMythpath(e.target.value)}
          disabled={lockedPath}
        >
          <option value="memory">Memory Seeker</option>
          <option value="codex">Codex Explorer</option>
          <option value="ritual">Ritual Witness</option>
          <option value="custom">Custom</option>
        </select>
        {mythpath !== "custom" && (
          <div className="form-text">
            {mythSummaries[mythpath].emoji} {mythSummaries[mythpath].desc}
          </div>
        )}
      </div>
      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <label className="form-label">Name</label>
          <input className="form-control" value={name} onChange={(e) => setName(e.target.value)} required />
        </div>

        <div className="mb-3">
          <label className="form-label">Description</label>
          <textarea className="form-control" value={description} onChange={(e) => setDescription(e.target.value)} rows={3} />
        </div>

        <div className="mb-3">
          <label className="form-label">Specialty</label>
          <input className="form-control" value={specialty} onChange={(e) => setSpecialty(e.target.value)} />
        </div>

        <div className="mb-3">
          <label className="form-label">Avatar URL</label>
          <input className="form-control" value={avatar} onChange={(e) => setAvatar(e.target.value)} />
        </div>
        <PromptIdeaGenerator onGenerate={(prompt) => setPersonality(prompt)} />
        <div className="mb-3">
          <label className="form-label">System Prompt</label>
          <select
            className="form-select"
            value={systemPromptId}
            onChange={(e) => setSystemPromptId(e.target.value)}
          >    
            <option value="">Select a prompt</option>
            {prompts.map((p) => (
              <option key={p.id} value={p.id}>{p.title}</option>
            ))}
          </select>
        </div>

        <div className="mb-3">
          <label className="form-label">Personality</label>
          <textarea
            className="form-control"
            rows={3}
            value={personality}
            onChange={(e) => setPersonality(e.target.value)}
          />
        </div>

        <div className="mb-3">
          <label className="form-label">Tone</label>
          <input className="form-control" value={tone} onChange={(e) => setTone(e.target.value)} />
        </div>

        <div className="mb-3">
          <label className="form-label">Preferred Model</label>
          <select className="form-select" value={preferredModel} onChange={(e) => setPreferredModel(e.target.value)}>
            <option value="gpt-4o">GPT-4o</option>
            <option value="claude-3-sonnet">Claude 3 Sonnet</option>
            <option value="mistral-7b">Mistral 7B</option>
          </select>
        </div>

        <button className="btn btn-success" type="submit" disabled={saving}>
          {saving ? "Saving..." : "💾 Save Assistant"}
        </button>
      </form>
    </div>
  );
}

// frontend/pages/assistants/CreateNewAssistantPage.jsx

import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { toast } from "react-toastify";
import PromptIdeaGenerator from "../../../components/prompts/PromptIdeaGenerator";
import apiFetch from "@/utils/apiClient";

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

export default function CreateNewAssistantPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [specialty, setSpecialty] = useState("");
  const [avatar, setAvatar] = useState("");
  const [avatarStyle, setAvatarStyle] = useState(
    location.state?.avatar_style || "robot"
  );
  const [toneProfile, setToneProfile] = useState(
    location.state?.tone_profile || "friendly"
  );
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
        const data = await apiFetch("/prompts/?type=system&show_all=true");
        setPrompts(data);
      } catch (err) {
        console.error("Failed to load prompts", err);
        toast.error("❌ Failed to load prompts.");
      }
    }
    fetchPrompts();
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
      const res = await apiFetch("/assistants/", {
        method: "POST",
        body: {
          name,
          description,
          specialty,
          avatar,
          avatar_style: avatarStyle,
          tone_profile: toneProfile,
          system_prompt: systemPromptId,
          personality,
          tone,
          preferred_model: preferredModel,
          archetype_path: mythpath !== "custom" ? mythpath : null,
        },
      });
      const data = res;
      if (data) {
        toast.success("✅ Assistant created!");
        navigate(`/assistants/${data.slug}/intro`);
      } else {
        toast.error("❌ Failed to create assistant.");
      }
    } catch (err) {
      console.error("Error creating assistant:", err);
      toast.error("❌ Server error.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="container my-5">
      <h1 className="mb-4">🧠 Create New Assistant</h1>
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

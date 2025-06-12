// frontend/pages/assistants/CreateNewAssistantPage.jsx

import { useEffect, useState } from "react";
import { useNavigate, useLocation, Link } from "react-router-dom";
import { toast } from "react-toastify";
import PromptIdeaGenerator from "../../../components/prompts/PromptIdeaGenerator";
import apiFetch from "@/utils/apiClient";
import { previewAssistantFromDemo } from "../../../api/assistants";
import AssistantPreviewBox from "../../../components/assistant/AssistantPreviewBox";
import useDemoSession from "../../../hooks/useDemoSession";
import { clearCachedUser } from "../../../hooks/useAuthGuard";

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
  const { demoSessionId } = useDemoSession();
  const params = new URLSearchParams(location.search);
  const cloneFrom = params.get("clone_from");
  const prefill = params.get("prefill");
  const fromOnboarding = location.state?.fromOnboarding;
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [specialty, setSpecialty] = useState("");
  const [avatar, setAvatar] = useState("");
  const [avatarStyle, setAvatarStyle] = useState(
    location.state?.avatar_style || "robot",
  );
  const [toneProfile, setToneProfile] = useState(
    location.state?.tone_profile || "friendly",
  );
  const [systemPromptId, setSystemPromptId] = useState("");
  const [systemPromptText, setSystemPromptText] = useState("");
  const [boostSummary, setBoostSummary] = useState("");
  const [originTraits, setOriginTraits] = useState([]);
  const [retainPrompt, setRetainPrompt] = useState(true);
  const [prefillTranscript, setPrefillTranscript] = useState([]);
  const [demoSlug, setDemoSlug] = useState(cloneFrom);
  const [prompts, setPrompts] = useState([]);
  const [personality, setPersonality] = useState("");
  const [tone, setTone] = useState("");
  const [loadingDemo, setLoadingDemo] = useState(false);
  const [preferredModel, setPreferredModel] = useState("gpt-4o");
  const [saving, setSaving] = useState(false);
  const [mythpath, setMythpath] = useState(
    location.state?.mythpath || "custom",
  );
  const lockedPath = Boolean(location.state?.mythpath);

  useEffect(() => {
    if (!cloneFrom) return;
    apiFetch("/assistants/demos/").then((list) => {
      const demo = (list || []).find((d) => d.demo_slug === cloneFrom);
      if (demo) {
        setName(demo.name);
        setTone(demo.tone || "");
        setAvatar(demo.avatar || "");
        if (demo.primary_badge) {
          setSpecialty(demo.primary_badge);
        }
        if (demo.avatar_style) {
          setAvatarStyle(demo.avatar_style);
        }
        if (demo.tone_profile) {
          setToneProfile(demo.tone_profile);
        }
        previewAssistantFromDemo(cloneFrom, []).then((resp) => {
          setSystemPromptText(resp.suggested_system_prompt || "");
          setBoostSummary(resp.boost_summary || "");
          setOriginTraits(resp.origin_traits || []);
          setRetainPrompt(!!resp.suggested_system_prompt);
        });
      }
    });
  }, [cloneFrom]);

  useEffect(() => {
    if (prefill !== "demo") return;
    const stored = localStorage.getItem("demo_prefill");
    if (!stored) return;
    const data = JSON.parse(stored);
    setLoadingDemo(true);
    setDemoSlug(data.assistant.demo_slug);
    setName(data.assistant.name || "");
    setDescription(data.assistant.description || "");
    setTone(data.assistant.tone || "");
    setAvatar(data.assistant.avatar || "");
    if (data.assistant.flair) setSpecialty(data.assistant.flair);
    if (data.assistant.avatar_style)
      setAvatarStyle(data.assistant.avatar_style);
    if (data.assistant.tone_profile)
      setToneProfile(data.assistant.tone_profile);
    setSystemPromptText(data.suggested_system_prompt || "");
    setPrefillTranscript(data.recent_messages || []);
    previewAssistantFromDemo(
      data.assistant.demo_slug,
      data.recent_messages,
    ).then((resp) => {
      setSystemPromptText(resp.suggested_system_prompt || "");
      setBoostSummary(resp.boost_summary || "");
      setOriginTraits(resp.origin_traits || []);
      setRetainPrompt(!!resp.suggested_system_prompt);
      setLoadingDemo(false);
    });
  }, [prefill]);

  useEffect(() => {
    if (cloneFrom || prefill === "demo") return;
    const saved = localStorage.getItem("assistant_draft");
    if (saved) {
      const d = JSON.parse(saved);
      setName(d.name || "");
      setDescription(d.description || "");
      setPersonality(d.personality || "");
      setTone(d.tone || "");
    } else if (fromOnboarding) {
      apiFetch("/assistants/default_template/")
        .then((t) => {
          if (!t) return;
          setName(t.name || "");
          setDescription(t.description || "");
          setPersonality(t.personality || "");
          setTone(t.tone || "");
        })
        .catch((err) => {
          console.error("Failed to load default template", err);
        });
    }
  }, []);

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

  useEffect(() => {
    if (prefill === "demo" || cloneFrom) return;
    const data = {
      name,
      description,
      personality,
      tone,
    };
    localStorage.setItem("assistant_draft", JSON.stringify(data));
  }, [name, description, personality, tone, cloneFrom, prefill]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      let res;
      if (prefill === "demo") {
        res = await apiFetch("/assistants/from_demo/", {
          method: "POST",
          body: {
            demo_slug: demoSlug,
            transcript: prefillTranscript,
            demo_session_id: demoSessionId,
            retain_starter_prompt: retainPrompt,
          },
        });
      } else {
        res = await apiFetch("/assistants/", {
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
      }
      const data = res;
      if (data) {
        if (prefill === "demo") {
          toast.success(
            "✅ New Assistant Created — Prompt boosted from your demo session",
          );
        } else {
          toast.success("✅ Assistant created!");
        }
        clearCachedUser();
        localStorage.removeItem("assistant_draft");
        const firstPrompt = prefillTranscript[0]?.content || "";
        navigate(`/assistants/${data.slug}/intro`, {
          state: { showConfetti: true, starter: firstPrompt },
        });
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
      {prefill === "demo" && (
        <Link to="/assistants-demos" className="d-block mb-2">
          &larr; Back to Demos
        </Link>
      )}
      <h1 className="mb-4">
        {prefill === "demo"
          ? "Personalize your clone"
          : "🧠 Create New Assistant"}
      </h1>
      {fromOnboarding && (
        <div className="alert alert-info" role="alert">
          You’re almost there — let’s bring your assistant to life.
        </div>
      )}
      <div className="row">
        <div className="col-md-8">
          <form onSubmit={handleSubmit}>
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
            <div className="mb-3">
              <label className="form-label">Name</label>
              <input
                className="form-control"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>

            <div className="mb-3">
              <label className="form-label">Description</label>
              <textarea
                className="form-control"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={3}
              />
            </div>

            <div className="mb-3">
              <label className="form-label">Specialty</label>
              <input
                className="form-control"
                value={specialty}
                onChange={(e) => setSpecialty(e.target.value)}
              />
            </div>

            <div className="mb-3">
              <label className="form-label">Avatar URL</label>
              <input
                className="form-control"
                value={avatar}
                onChange={(e) => setAvatar(e.target.value)}
              />
            </div>
            <PromptIdeaGenerator
              onGenerate={(prompt) => setPersonality(prompt.content)}
            />
            <div className="mb-3">
              <label className="form-label">System Prompt</label>
              <select
                className="form-select"
                value={systemPromptId}
                onChange={(e) => setSystemPromptId(e.target.value)}
              >
                <option value="">Select a prompt</option>
                {prompts.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.title}
                  </option>
                ))}
              </select>
            </div>
            {prefill === "demo" && (
              <details className="mb-3">
                <summary>🔍 Boosted from Demo</summary>
                <div className="mt-2">
                  {boostSummary && <p className="mb-2">{boostSummary}</p>}
                  <label className="form-label">Boosted Prompt</label>
                  <textarea
                    className="form-control"
                    rows={4}
                    value={systemPromptText}
                    readOnly
                  />
                  <div className="form-check mt-1">
                    <input
                      className="form-check-input"
                      type="checkbox"
                      checked={retainPrompt}
                      onChange={(e) => setRetainPrompt(e.target.checked)}
                      id="retainPrompt"
                    />
                    <label className="form-check-label" htmlFor="retainPrompt">
                      Retain this as system prompt
                    </label>
                  </div>
                  {originTraits.length > 0 && (
                    <div className="mt-2">
                      <strong>Traits Inherited:</strong> {originTraits.join(", ")}
                    </div>
                  )}
                </div>
              </details>
            )}

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
              <input
                className="form-control"
                value={tone}
                onChange={(e) => setTone(e.target.value)}
              />
            </div>

            <div className="mb-3">
              <label className="form-label">Preferred Model</label>
              <select
                className="form-select"
                value={preferredModel}
                onChange={(e) => setPreferredModel(e.target.value)}
              >
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
        <div className="col-md-4">
          {loadingDemo ? (
            <div className="placeholder-glow">
              <div
                className="placeholder col-12 mb-2"
                style={{ height: "8rem" }}
              />
            </div>
          ) : (
            <AssistantPreviewBox
              name={name}
              tone={toneProfile || tone}
              personality={personality}
              avatarStyle={avatarStyle}
            />
          )}
        </div>
      </div>
    </div>
  );
}

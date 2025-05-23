import { useEffect, useState } from "react";
import CommonModal from "../../CommonModal";
import apiFetch from "../../../utils/apiClient";

export default function IdentityCardEditor({ assistantId, show, onClose }) {
  const [card, setCard] = useState(null);
  const [name, setName] = useState("");
  const [tone, setTone] = useState("Guardian");
  const [traits, setTraits] = useState("");

  useEffect(() => {
    if (!show || !assistantId) return;
    apiFetch(`/assistants/${assistantId}/identity-card/`).then((res) => {
      setCard(res);
      setName(res.name_override || res.assistant_name || "");
      setTone(res.role_tone || "Guardian");
      setTraits((res.archetype_traits || []).join(", "));
    });
  }, [assistantId, show]);

  const save = async () => {
    try {
      await apiFetch(`/assistants/${assistantId}/identity-card/`, {
        method: "PUT",
        body: {
          name_override: name,
          role_tone: tone,
          archetype_traits: traits.split(/,\s*/).filter(Boolean),
        },
      });
      onClose(true);
    } catch (err) {
      console.error("Failed to save identity card", err);
      onClose(false);
    }
  };

  return (
    <CommonModal
      show={show}
      onClose={() => onClose(false)}
      title="Edit Identity Card"
      footer={
        <button className="btn btn-primary" onClick={save} disabled={!card}>
          Save
        </button>
      }
    >
      {card ? (
        <div>
          <div className="mb-2">
            <label className="form-label">Assistant Name</label>
            <input
              className="form-control"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>
          <div className="mb-2">
            <label className="form-label">Role Tone</label>
            <select
              className="form-select"
              value={tone}
              onChange={(e) => setTone(e.target.value)}
            >
              <option>Guardian</option>
              <option>Oracle</option>
              <option>Trickster</option>
              <option>Scholar</option>
            </select>
          </div>
          <div className="mb-2">
            <label className="form-label">Archetype Traits</label>
            <input
              className="form-control"
              value={traits}
              onChange={(e) => setTraits(e.target.value)}
              placeholder="comma separated"
            />
          </div>
          <div className="mb-2">
            <label className="form-label">Codex Focus</label>
            <input className="form-control" value={card.codex_focus || ""} readOnly />
          </div>
        </div>
      ) : (
        <div>Loading...</div>
      )}
    </CommonModal>
  );
}

import { useEffect, useState } from "react";
import PropTypes from "prop-types";
import { toast } from "react-toastify";
import Modal from "../CommonModal";
import AvatarSelector from "../onboarding/AvatarSelector";
import BadgeSelector from "./BadgeSelector";
import AssistantCard from "./AssistantCard";
import apiFetch from "@/utils/apiClient";

const TONES = ["cheerful", "friendly", "formal", "mysterious", "nerdy", "zen"];

export default function AssistantPersonalizationPrompt({
  assistant,
  show,
  onClose,
  onSaved,
}) {
  const [name, setName] = useState(assistant.name || "");
  const [tone, setTone] = useState(
    assistant.tone_profile || assistant.tone || "",
  );
  const [avatar, setAvatar] = useState(assistant.avatar_style || "robot");
  const [badge, setBadge] = useState(assistant.primary_badge || "");
  const suggestions = assistant.personalization_prompt?.suggested_names || [];
  const available = assistant.available_badges || [];

  useEffect(() => {
    setName(assistant.name || "");
    setTone(assistant.tone_profile || assistant.tone || "");
    setAvatar(assistant.avatar_style || "robot");
    setBadge(assistant.primary_badge || "");
  }, [assistant]);

  const handleSave = async () => {
    try {
      await apiFetch(`/assistants/${assistant.slug}/`, {
        method: "PATCH",
        body: {
          name,
          tone_profile: tone,
          avatar_style: avatar,
          primary_badge: badge || null,
        },
      });
      toast.info("\ud83e\udde0 Welcome memory saved!");
      onSaved && onSaved();
      onClose();
    } catch (err) {
      console.error("Failed to save", err);
    }
  };

  const preview = {
    ...assistant,
    name,
    tone_profile: tone,
    avatar_style: avatar,
    primary_badge: badge,
  };

  const footer = (
    <div className="d-flex justify-content-end w-100">
      <button className="btn btn-secondary me-2" onClick={onClose}>
        Cancel
      </button>
      <button className="btn btn-primary" onClick={handleSave}>
        Save
      </button>
    </div>
  );

  return (
    <Modal
      show={show}
      onClose={onClose}
      title="Personalize Assistant"
      footer={footer}
    >
      <div className="mb-3">
        <label className="form-label">Assistant Name</label>
        <input
          className="form-control"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        {suggestions.length > 0 && (
          <div className="mt-2">
            {suggestions.map((s) => (
              <button
                key={s}
                className="btn btn-sm btn-outline-secondary me-2"
                onClick={() => setName(s)}
              >
                {s}
              </button>
            ))}
          </div>
        )}
      </div>
      <div className="mb-3">
        <label className="form-label">Tone</label>
        <select
          className="form-select"
          value={tone}
          onChange={(e) => setTone(e.target.value)}
        >
          {TONES.map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>
      </div>
      <div className="mb-3">
        <label className="form-label">Avatar</label>
        <AvatarSelector value={avatar} onChange={setAvatar} />
      </div>
      <div className="mb-3">
        <label className="form-label">Primary Badge</label>
        <BadgeSelector
          available={available}
          selected={badge ? [badge] : []}
          onChange={(list) => setBadge(list[0] || "")}
          primary={badge}
          onPrimaryChange={setBadge}
        />
      </div>
      <AssistantCard assistant={preview} />
    </Modal>
  );
}

AssistantPersonalizationPrompt.propTypes = {
  assistant: PropTypes.object.isRequired,
  show: PropTypes.bool,
  onClose: PropTypes.func.isRequired,
  onSaved: PropTypes.func,
};

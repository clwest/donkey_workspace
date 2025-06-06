import { OverlayTrigger, Tooltip } from "react-bootstrap";

export const BADGE_INFO = {
  glossary_apprentice: {
    label: "Glossary Apprentice",
    icon: "📚",
    tip: "📚 Acquired 10 glossary terms",
  },
  semantic_master: {
    label: "Semantic Synthesizer",
    icon: "🏅",
    tip: "🏅 Semantic Synthesizer — Reinforced 50 glossary terms",
  },
  reflection_ready: {
    label: "Reflection Adept",
    icon: "🧠",
    tip: "🧠 Completed 5 reflections",
  },
  delegation_ready: {
    label: "Delegation Ready",
    icon: "🤝",
    tip: "🤝 Badge collection complete",
  },
};

export const BADGE_ORDER = [
  "delegation_ready",
  "semantic_master",
  "glossary_apprentice",
  "reflection_ready",
];

export default function AssistantBadgeIcon({ badges = [], primaryBadge }) {
  const badge =
    primaryBadge ||
    badges.sort(
      (a, b) => BADGE_ORDER.indexOf(a) - BADGE_ORDER.indexOf(b)
    )[0];
  const info = BADGE_INFO[badge];
  if (!info) return null;
  return (
    <OverlayTrigger placement="top" overlay={<Tooltip>{info.tip}</Tooltip>}>
      <span className="ms-1" role="img" aria-label={info.label}>
        {info.icon}
      </span>
    </OverlayTrigger>
  );
}

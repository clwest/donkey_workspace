import PropTypes from "prop-types";

const AVATARS = [
  { value: "owl", label: "Owl", emoji: "🦚" },
  { value: "fox", label: "Fox", emoji: "🦊" },
  { value: "robot", label: "Robot", emoji: "🤖" },
  { value: "wizard", label: "Wizard", emoji: "🧙‍♂️" },
];

export default function AvatarSelector({ value, onChange }) {
  return (
    <div className="d-flex flex-wrap gap-3">
      {AVATARS.map((a) => (
        <div
          key={a.value}
          className={`p-2 border rounded text-center cursor-pointer ${
            value === a.value ? "bg-primary text-white" : ""
          }`}
          onClick={() => onChange(a.value)}
          style={{ width: "80px" }}
        >
          <div style={{ fontSize: "2rem" }}>{a.emoji}</div>
          <div>{a.label}</div>
        </div>
      ))}
    </div>
  );
}

AvatarSelector.propTypes = {
  value: PropTypes.string,
  onChange: PropTypes.func.isRequired,
};

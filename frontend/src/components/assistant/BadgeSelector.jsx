import { OverlayTrigger, Tooltip } from "react-bootstrap";

export default function BadgeSelector({
  available = [],
  selected = [],
  onChange,
  primary,
  onPrimaryChange,
}) {
  const toggle = (slug) => {
    if (!onChange) return;
    if (selected.includes(slug)) {
      onChange(selected.filter((b) => b !== slug));
    } else {
      onChange([...selected, slug]);
    }
  };
  return (
    <div className="mb-3">
      <label className="form-label">Skill Badges</label>
      <div className="d-flex flex-wrap">
        {available.map((b) => (
          <OverlayTrigger
            key={b.slug}
            placement="top"
            overlay={<Tooltip>{b.description}</Tooltip>}
          >
            <span
              onClick={() => toggle(b.slug)}
              className={`badge me-2 mb-2 ${
                selected.includes(b.slug) ? "bg-success" : "bg-secondary"
              }`}
              style={{ cursor: onChange ? "pointer" : "default" }}
              role="img"
              aria-label={b.label}
            >
              {b.emoji} {b.label}
            </span>
          </OverlayTrigger>
        ))}
      </div>
      {selected.length > 0 && onPrimaryChange && (
        <div className="mt-2">
          <label className="form-label">Primary Badge</label>
          <select
            className="form-select"
            value={primary || ""}
            onChange={(e) => onPrimaryChange(e.target.value)}
          >
            <option value="">(none)</option>
            {selected.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>
      )}
    </div>
  );
}


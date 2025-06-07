import { OverlayTrigger, Tooltip } from 'react-bootstrap';
import { Link } from 'react-router-dom';

export default function GlossaryOverlayTooltip({ label, tooltip, slug }) {
  if (!tooltip) return <>{label}</>;
  const overlay = (
    <Tooltip>
      <div>{tooltip}</div>
      {slug && (
        <div className="mt-1">
          <Link to={`/glossary/${slug}/`}>More Info</Link>
        </div>
      )}
    </Tooltip>
  );
  return (
    <OverlayTrigger overlay={overlay} placement="top">
      <span className="glossary-overlay" style={{ borderBottom: '1px dotted' }}>
        {label}
      </span>
    </OverlayTrigger>
  );
}

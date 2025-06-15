import { OverlayTrigger, Tooltip } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { useEffect, useRef } from 'react';
import apiFetch from '@/utils/apiClient';

export default function GlossaryOverlayTooltip({ label, tooltip, slug }) {
  const fetchedRef = useRef({});
  useEffect(() => {
    if (!slug || fetchedRef.current[slug]) return;
    fetchedRef.current[slug] = true;
    apiFetch(`/glossary/${slug}/overlay/`).catch(() => {});
  }, [slug]);
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

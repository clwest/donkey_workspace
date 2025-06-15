import useGlossaryOverlay from '@/hooks/glossary';
import GlossaryOverlayTooltip from './GlossaryOverlayTooltip';

export default function ReflectionReviewPanel() {
  const { overlays, paused } = useGlossaryOverlay('reflection');
  return (
    <div className="p-3 border rounded">
      <h5>Reflection Review</h5>
      {paused && (
        <div className="text-warning small">Paused due to rate limit</div>
      )}
      <ul>
        {overlays.map((o) => (
          <li key={o.slug}>
            <GlossaryOverlayTooltip {...o} />
          </li>
        ))}
      </ul>
    </div>
  );
}

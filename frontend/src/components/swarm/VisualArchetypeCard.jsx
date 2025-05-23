import { useEffect, useState } from "react";
import { fetchVisualArchetypeCard } from "../../api/agents";

export default function VisualArchetypeCard({ assistantId }) {
  const [card, setCard] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!assistantId) return;
    fetchVisualArchetypeCard(assistantId)
      .then(setCard)
      .catch(() => setCard(null))
      .finally(() => setLoading(false));
  }, [assistantId]);

  if (loading) return <div>Loading archetype...</div>;
  if (!card) return null;

  return (
    <div className="card my-3">
      <div className="card-body">
        <h5 className="card-title">{card.name}</h5>
        <p className="mb-1">Role: {card.role}</p>
        <p className="mb-1">Ritual State: {card.ritual_state}</p>
        <p className="mb-1">Alignment: {card.archetypal_alignment}</p>
        <pre className="small text-muted mb-0">
          {JSON.stringify(card.belief_vector || {}, null, 2)}
        </pre>
      </div>
    </div>
  );
}

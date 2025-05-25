import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";

export default function PersonalityDeckBuilder() {
  const { id } = useParams();
  const [deck, setDeck] = useState(null);

  useEffect(() => {
    apiFetch(`/assistants/${id}/personality-deck/`)
      .then(setDeck)
      .catch((err) => console.error("Failed to load deck", err));
  }, [id]);

  return (
    <div className="container my-4">
      <h3>Personality Deck</h3>
      <pre>{JSON.stringify(deck, null, 2)}</pre>
    </div>
  );
}

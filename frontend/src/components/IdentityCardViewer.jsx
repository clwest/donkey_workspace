import { useEffect, useState } from "react";
import apiFetch from "../utils/apiClient";

export default function IdentityCardViewer() {
  const [cards, setCards] = useState([]);

  useEffect(() => {
    apiFetch("/identity-cards/").then(setCards);
  }, []);

  return (
    <div className="mb-3">
      <h5>Mythic Identity Cards</h5>
      <ul>
        {cards.map((c) => (
          <li key={c.id}>
            {c.assistant} — {c.identity_signature}
          </li>
        ))}
      </ul>
    </div>
  );
}

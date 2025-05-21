import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function InheritanceGraph() {
  const [lines, setLines] = useState([]);

  useEffect(() => {
    async function load() {
      try {
        const data = await apiFetch("/agents/lore-inheritance/");
        setLines(data || []);
      } catch (err) {
        console.error("Failed to load inheritance lines", err);
      }
    }
    load();
  }, []);

  if (lines.length === 0) return <div>No inheritance data.</div>;

  return (
    <ul className="list-group">
      {lines.map((l) => (
        <li key={l.id} className="list-group-item">
          {l.source_title} &rarr; {l.descendant_title}
        </li>
      ))}
    </ul>
  );
}

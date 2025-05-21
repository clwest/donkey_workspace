import { useState } from "react";

export default function DebateArena({ debates = [] }) {
  const [selected, setSelected] = useState(null);

  return (
    <div className="p-3 border rounded bg-light">
      <h5>Debate Arena</h5>
      <ul className="list-group mb-2">
        {debates.map((d) => (
          <li
            key={d.id}
            className="list-group-item"
            onClick={() => setSelected(d)}
            role="button"
          >
            {d.topic}
          </li>
        ))}
      </ul>
      {selected && (
        <div className="mt-2">
          <h6>{selected.topic}</h6>
          <pre className="small bg-white p-2 rounded">
            {JSON.stringify(selected.perspectives, null, 2)}
          </pre>
          {selected.outcome_summary && <p>{selected.outcome_summary}</p>}
        </div>
      )}
    </div>
  );
}

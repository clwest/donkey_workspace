// frontend/components/agents/AssistantList.jsx
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

export default function AssistantList() {
  const [assistants, setAssistants] = useState([]);

  useEffect(() => {
    fetch("http://localhost:8000/api/assistants/")
      .then((res) => res.json())
      .then(setAssistants)
      .catch((err) => console.error("Failed to fetch assistants:", err));
  }, []);

  // Group by parent
  const parentMap = {};
  assistants.forEach((a) => {
    if (!a.parent_assistant) {
      parentMap[a.id] = { parent: a, children: [] };
    }
  });

  assistants.forEach((a) => {
    if (a.parent_assistant && parentMap[a.parent_assistant]) {
      parentMap[a.parent_assistant].children.push(a);
    }
  });

  return (
    <div className="container mt-5">
      <h2>🧠 Available Assistants</h2>
      <ul className="list-group">
        {Object.values(parentMap).map(({ parent, children }) => (
          <li key={parent.id} className="list-group-item">
            <Link to={`/assistants/${parent.slug}`}>
              <strong>{parent.name}</strong>
            </Link>
            <p className="text-muted mb-1">{parent.description}</p>

            {children.length > 0 && (
              <ul className="ps-3">
                {children.map((child) => (
                  <li key={child.id}>
                    <Link to={`/assistants/${child.slug}`}>
                      {child.name}
                    </Link>
                    <span className="text-muted ms-1">({child.specialty})</span>
                  </li>
                ))}
              </ul>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
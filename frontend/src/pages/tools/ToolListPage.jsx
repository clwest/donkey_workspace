import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchTools } from "../../api/tools";

export default function ToolListPage() {
  const [tools, setTools] = useState([]);

  useEffect(() => {
    fetchTools().then(setTools).catch(() => setTools([]));
  }, []);

  return (
    <div className="container mt-3">
      <h3>Tools</h3>
      <ul className="list-group">
        {tools.map((t) => (
          <li key={t.id} className="list-group-item">
            <Link to={`/tools/${t.id}`}>{t.name}</Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

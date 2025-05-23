import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function HyperstructureBuilder() {
  const [structures, setStructures] = useState([]);

  useEffect(() => {
    apiFetch("/hyperstructures/")
      .then((res) => setStructures(res.results || res))
      .catch(() => setStructures([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Myth Hyperstructures</h5>
      <ul className="list-group">
        {structures.map((s) => (
          <li key={s.id} className="list-group-item">
            {s.structure_name}
          </li>
        ))}
        {structures.length === 0 && (
          <li className="list-group-item text-muted">No hyperstructures.</li>
        )}
      </ul>
    </div>
  );
}

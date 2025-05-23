import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function TrainingGroundSimulator() {
  const [grounds, setGrounds] = useState([]);

  useEffect(() => {
    apiFetch("/training-grounds/")
      .then((data) => setGrounds(data.results || data))
      .catch(() => setGrounds([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Narrative Training Grounds</h5>
      <ul className="list-group">
        {grounds.map((g) => (
          <li key={g.id} className="list-group-item">
            {g.training_title}
          </li>
        ))}
        {grounds.length === 0 && (
          <li className="list-group-item text-muted">No training grounds.</li>
        )}
      </ul>
    </div>
  );
}

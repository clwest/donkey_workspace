import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function SceneControlPanel() {
  const [scenes, setScenes] = useState([]);

  useEffect(() => {
    apiFetch("/simulation/scene-control/")
      .then((res) => setScenes(res.results || res))
      .catch(() => setScenes([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Scene Control</h5>
      <ul className="list-group">
        {scenes.map((s) => (
          <li key={s.id} className="list-group-item">
            {s.scene_title}
          </li>
        ))}
        {scenes.length === 0 && (
          <li className="list-group-item text-muted">No scenes active.</li>
        )}
      </ul>
    </div>
  );
}

import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function LegacyVaultViewer() {
  const [vaults, setVaults] = useState([]);

  useEffect(() => {
    apiFetch("/legacy-continuity-vaults/")
      .then((data) => setVaults(data.results || data))
      .catch(() => setVaults([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Legacy Continuity Vaults</h5>
      <ul className="list-group">
        {vaults.map((v) => (
          <li key={v.id} className="list-group-item">
            {v.vault_name} – {v.narrative_epoch}
          </li>
        ))}
        {vaults.length === 0 && (
          <li className="list-group-item text-muted">No continuity vaults.</li>
        )}
      </ul>
    </div>
  );
}

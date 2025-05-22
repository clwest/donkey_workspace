import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function LegacyVaultViewer() {
  const [vaults, setVaults] = useState([]);

  useEffect(() => {
    apiFetch("/legacy-vaults/")
      .then((data) => setVaults(data.results || data))
      .catch(() => setVaults([]));
  }, []);

  return (
    <div className="my-3">
      <h5>Legacy Token Vaults</h5>
      <ul className="list-group">
        {vaults.map((v) => (
          <li key={v.id} className="list-group-item">
            <strong>{v.name}</strong> - {v.vault_access_policy}
          </li>
        ))}
        {vaults.length === 0 && (
          <li className="list-group-item text-muted">No vaults available.</li>
        )}
      </ul>
    </div>
  );
}

import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function PurposeMigrationConsole() {
  const [migrations, setMigrations] = useState([]);
  const [fromId, setFromId] = useState("");
  const [toId, setToId] = useState("");
  const [reason, setReason] = useState("");

  const load = () => {
    apiFetch("/agents/purpose-migrations/")
      .then(setMigrations)
      .catch(() => setMigrations([]));
  };

  useEffect(() => {
    load();
  }, []);

  const submit = async () => {
    await apiFetch("/agents/purpose-migrations/", {
      method: "POST",
      body: {
        reassigned_from: fromId,
        reassigned_to: toId,
        migration_reason: reason,
        intent_vector: {},
      },
    });
    setFromId("");
    setToId("");
    setReason("");
    load();
  };

  return (
    <div className="card my-3">
      <div className="card-header">Purpose Migrations</div>
      <div className="card-body">
        <div className="row g-2 mb-3">
          <div className="col">
            <input
              className="form-control"
              placeholder="From Assistant ID"
              value={fromId}
              onChange={(e) => setFromId(e.target.value)}
            />
          </div>
          <div className="col">
            <input
              className="form-control"
              placeholder="To Assistant ID"
              value={toId}
              onChange={(e) => setToId(e.target.value)}
            />
          </div>
          <div className="col-4">
            <input
              className="form-control"
              placeholder="Reason"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
            />
          </div>
          <div className="col-auto">
            <button className="btn btn-primary" onClick={submit} disabled={!fromId || !toId}>
              Migrate
            </button>
          </div>
        </div>
        <ul className="list-group">
          {migrations.map((m) => (
            <li key={m.id} className="list-group-item">
              {m.reassigned_from.name} → {m.reassigned_to.name} : {m.migration_reason}
            </li>
          ))}
          {migrations.length === 0 && (
            <li className="list-group-item text-muted">No migrations recorded.</li>
          )}
        </ul>
      </div>
    </div>
  );
}

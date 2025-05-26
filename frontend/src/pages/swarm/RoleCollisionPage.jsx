import { useEffect, useState } from "react";
import { fetchRoleCollisions } from "../../api/ontology";

export default function RoleCollisionPage() {
  const [collisions, setCollisions] = useState([]);

  useEffect(() => {
    fetchRoleCollisions()
      .then((res) => setCollisions(res || []))
      .catch(() => setCollisions([]));
  }, []);

  return (
    <div className="container my-4">
      <h1 className="mb-3">Swarm Role Collisions</h1>
      {collisions.length === 0 ? (
        <p>No collisions detected.</p>
      ) : (
        <table className="table table-sm">
          <thead>
            <tr>
              <th>Assistant A</th>
              <th>Assistant B</th>
              <th>Type</th>
              <th>Tension</th>
            </tr>
          </thead>
          <tbody>
            {collisions.map((c, idx) => (
              <tr key={idx}>
                <td>{c.assistant_a}</td>
                <td>{c.assistant_b}</td>
                <td>{c.conflict_type}</td>
                <td>{c.tension_score}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

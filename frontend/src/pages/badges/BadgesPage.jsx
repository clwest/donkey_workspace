import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function BadgesPage() {
  const [badges, setBadges] = useState([]);

  useEffect(() => {
    apiFetch("/badges/").then(setBadges);
  }, []);

  return (
    <div className="container my-4">
      <h3>All Skill Badges</h3>
      <table className="table">
        <thead>
          <tr>
            <th>Badge</th>
            <th>Description</th>
            <th>Requirements</th>
          </tr>
        </thead>
        <tbody>
          {badges.map((b) => (
            <tr key={b.slug}>
              <td>
                {b.emoji} {b.label}
              </td>
              <td>{b.description}</td>
              <td>{b.criteria}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function AssistantReflectionGroups() {
  const { slug } = useParams();
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchGroups() {
      try {
        const data = await apiFetch(`/assistants/${slug}/reflections/groups/`);
        setGroups(Array.isArray(data) ? data : []);
      } catch (err) {
        console.error("Failed to load groups", err);
        setGroups([]);
      } finally {
        setLoading(false);
      }
    }
    fetchGroups();
  }, [slug]);

  if (loading) return <div className="container my-5">Loading...</div>;

  return (
    <div className="container my-5">
      <h2 className="mb-4">Reflection Groups</h2>
      {groups.length === 0 ? (
        <p>No reflection groups.</p>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>Group Name</th>
              <th># Reflections</th>
              <th>Summary Preview</th>
              <th>Last Updated</th>
            </tr>
          </thead>
          <tbody>
            {groups.map((g) => (
              <tr key={g.slug}>
                <td>{g.title || g.slug}</td>
                <td>{g.reflection_count}</td>
                <td>{g.summary ? g.summary.slice(0, 60) : ""}</td>
                <td>
                  {g.summary_updated
                    ? new Date(g.summary_updated).toLocaleDateString()
                    : ""}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

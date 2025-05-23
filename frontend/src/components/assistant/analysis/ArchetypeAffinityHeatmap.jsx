import { useEffect, useState } from "react";
import apiFetch from "../../../utils/apiClient";

export default function ArchetypeAffinityHeatmap({ assistantId }) {
  const [weights, setWeights] = useState({});

  useEffect(() => {
    if (!assistantId) return;
    async function load() {
      try {
        const res = await apiFetch(`/assistants/${assistantId}/`);
        setWeights(res.archetype_affinity || {});
      } catch (err) {
        console.error("Failed to load affinity", err);
        setWeights({});
      }
    }
    load();
  }, [assistantId]);

  const archetypes = Object.keys(weights);

  if (archetypes.length === 0) return <div>No archetype data.</div>;

  return (
    <div className="my-3">
      <table className="table table-sm text-center">
        <tbody>
          {archetypes.map((a) => (
            <tr key={a}>
              <th className="text-start">{a}</th>
              <td style={{ background: `rgba(13,110,253,${weights[a]})` }}>
                {weights[a].toFixed(2)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

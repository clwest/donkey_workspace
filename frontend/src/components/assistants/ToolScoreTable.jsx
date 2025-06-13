export default function ToolScoreTable({ scores = [] }) {
  if (!scores.length) return <div>No tool data.</div>;
  return (
    <table className="table table-sm">
      <thead>
        <tr>
          <th>Tool</th>
          <th>Uses</th>
          <th style={{ width: "40%" }}>Confidence</th>
          <th>Tags</th>
        </tr>
      </thead>
      <tbody>
        {scores.map((s) => (
          <tr key={s.tool.id}>
            <td>{s.tool.name}</td>
            <td>{s.usage_count}</td>
            <td>
              <div className="progress">
                <div
                  className="progress-bar"
                  style={{ width: `${Math.round(s.confidence * 100)}%` }}
                />
              </div>
            </td>
            <td>{s.tags.join(", ")}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

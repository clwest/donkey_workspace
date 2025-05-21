import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";
import TagFilterBar from "../../../components/mcp_core/TagFilterBar";
import ThreadDiagnosticsPanel from "../../../components/mcp_core/ThreadDiagnosticsPanel";

export default function ThreadsOverviewPage() {
  const [threads, setThreads] = useState([]);
  const [filteredTags, setFilteredTags] = useState([]);
  const [statusFilter, setStatusFilter] = useState("");

  useEffect(() => {
    const fetchThreads = async () => {
      const data = await apiFetch("/mcp/threads/overview/");
      setThreads(data || []);
    };
    fetchThreads();
  }, []);

  const filtered = filteredTags.length
    ? threads.filter((t) =>
        t.tags.some((tag) => filteredTags.includes(tag.slug))
      )
    : threads;
  const statusFiltered = statusFilter
    ? filtered.filter((t) => t.completion_status === statusFilter)
    : filtered;

  return (
    <div className="container my-5">
      <h2 className="mb-4">🧵 Thread Continuity Overview</h2>

      <TagFilterBar tags={extractUniqueTags(threads)} onFilter={setFilteredTags} />
      <div className="mb-3">
        <select
          className="form-select w-auto d-inline"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="">All Statuses</option>
          <option value="in_progress">In Progress</option>
          <option value="completed">Completed</option>
          <option value="stalled">Stalled</option>
          <option value="draft">Draft</option>
        </select>
      </div>

      {statusFiltered.length === 0 ? (
        <p className="text-muted mt-4">No threads match current filters.</p>
      ) : (
        <table className="table table-sm align-middle">
          <thead>
            <tr>
              <th>Thread</th>
              <th>Reflections</th>
              <th>Progress</th>
              <th>Last Updated</th>
              <th>Gaps</th>
            </tr>
          </thead>
          <tbody>
            {statusFiltered
              .sort(
                (a, b) => new Date(b.last_updated) - new Date(a.last_updated)
              )
              .map((thread) => (
                <tr key={thread.id}>
                  <td>
                    <Link to={`/threads/${thread.id}`}>{thread.title}</Link>
                    <div className="text-muted small">
                      {thread.summary?.slice(0, 80)}
                    </div>
                    <ThreadDiagnosticsPanel thread={thread} />
                  </td>
                  <td>{thread.reflection_count}</td>
                  <td>{thread.progress_percent ?? 0}%</td>
                  <td>
                    {thread.last_updated
                      ? new Date(thread.last_updated).toLocaleString()
                      : ""}
                  </td>
                  <td>
                    {thread.gaps_detected && thread.gaps_detected.length > 0
                      ? thread.gaps_detected.join(", ")
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

function extractUniqueTags(threads) {
  const tagMap = {};
  threads.forEach((thread) => {
    (thread.tags || []).forEach((tag) => {
      tagMap[tag.slug] = tag;
    });
  });
  return Object.values(tagMap);
}
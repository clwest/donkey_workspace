import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";
import TagFilterBar from "../../../components/mcp_core/TagFilterBar";
import ThreadCard from "../../../components/mcp_core/ThreadCard";

export default function ThreadsOverviewPage() {
  const [threads, setThreads] = useState([]);
  const [filteredTags, setFilteredTags] = useState([]);

  useEffect(() => {
    const fetchThreads = async () => {
      const data = await apiFetch("/mcp/threads/");
      setThreads(data || []);
    };
    fetchThreads();
  }, []);

  const filtered = filteredTags.length
    ? threads.filter((t) =>
        t.tags.some((tag) => filteredTags.includes(tag.slug))
      )
    : threads;

  return (
    <div className="container my-5">
      <h2 className="mb-4">🧵 Narrative Threads</h2>

      <TagFilterBar tags={extractUniqueTags(threads)} onFilter={setFilteredTags} />

      {filtered.length === 0 ? (
        <p className="text-muted mt-4">No threads match current filters.</p>
      ) : (
        <div className="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-3">
          {filtered.map((thread) => (
            <div key={thread.id} className="col">
              <ThreadCard thread={thread} />
            </div>
          ))}
        </div>
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
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import TagBadge from "../TagBadge";

dayjs.extend(relativeTime);

export default function MemoryCard({ memory, action }) {
  const summaryRaw =
    memory.content_preview || memory.summary || memory.event || memory.content || "";
  const isEmpty = !summaryRaw.trim() || summaryRaw.trim().toLowerCase() === "no meaningful content.";
  const summary = !isEmpty
    ? summaryRaw.slice(0, 150) + (summaryRaw.length > 150 ? "…" : "")
    : "No meaningful content";

  const readSecs = Math.round((memory.token_count || 0) / 4);
  const created = dayjs(memory.created_at);
  const isRecent = dayjs().diff(created, "minute") < 10;
  const isWeak = (memory.token_count || 0) < 5 && (memory.importance || 0) <= 2;
  const tooltip = `${created.format("YYYY-MM-DD HH:mm:ss")} (${created.fromNow()})`;
  const reflected =
    memory.type === "reflection" ||
    (memory.tags || []).some((t) => t.name.toLowerCase().includes("reflection"));

  return (
    <div className={`card mb-2 ${isRecent ? "recent-memory" : ""} ${isWeak ? "opacity-50" : ""}`}>
      <div className="card-body p-2 d-flex justify-content-between">
        <div>
          <div className="memory-summary mb-1 small">
            📄 {reflected && <span title="Used in reflection" className="me-1">🪞</span>}
            {isEmpty ? <span className="text-muted">{summary}</span> : summary}
          </div>
          <div className="memory-meta text-muted small" title={tooltip}>
            🧠 {memory.token_count || 0} tokens · ~{readSecs}s • {created.fromNow()}
          </div>
          {memory.triggered_by && (
            <div className="memory-origin text-muted small">{memory.triggered_by}</div>
          )}
          {(memory.session_id || memory.anchor_slug) && (
            <div className="memory-trace small">
              <a
                href={memory.session_id ? `/sessions/${memory.session_id}` : `/anchors/${memory.anchor_slug}`}
                target="_blank"
                rel="noreferrer"
              >
                Origin
              </a>
            </div>
          )}
          {memory.tags && memory.tags.length > 0 && (
            <div className="mt-1 text-truncate" style={{ maxWidth: 220 }}>
              {memory.tags.slice(0, 3).map((t) => (
                <TagBadge key={t.id || t.slug} tag={t} />
              ))}
            </div>
          )}
        </div>
        {action && <div className="ms-2">{action}</div>}
      </div>
    </div>
  );
}

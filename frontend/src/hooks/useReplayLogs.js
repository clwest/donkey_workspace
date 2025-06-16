import { useEffect, useState } from "react";
import { fetchReplayLogs } from "../api/assistants";

export default function useReplayLogs(slug) {
  const [logs, setLogs] = useState([]);
  useEffect(() => {
    if (!slug) return;
    fetchReplayLogs(slug)
      .then((res) => setLogs(res.results || res))
      .catch(() => setLogs([]));
  }, [slug]);
  return logs;
}

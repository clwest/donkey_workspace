import { useEffect, useState } from "react";
import { fetchDriftAudit } from "../api/assistants";

export default function useDriftSnapshots(id) {
  const [data, setData] = useState([]);
  useEffect(() => {
    if (!id) return;
    fetchDriftAudit(id)
      .then((res) => setData(res.snapshots || res))
      .catch(() => setData([]));
  }, [id]);
  return data;
}

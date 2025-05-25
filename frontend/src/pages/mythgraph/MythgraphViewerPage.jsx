import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { fetchMythgraph } from "../../api/mythgraph";
import MythgraphGraph from "../../components/mythgraph/MythgraphGraph";

export default function MythgraphViewerPage() {
  const { id } = useParams();
  const [data, setData] = useState(null);

  useEffect(() => {
    fetchMythgraph(id).then(setData).catch((e) => console.error(e));
  }, [id]);

  return (
    <div className="container my-4">
      <h1 className="mb-3">Mythgraph Viewer</h1>
      {data ? <MythgraphGraph data={data} /> : <p>Loading...</p>}
    </div>
  );
}

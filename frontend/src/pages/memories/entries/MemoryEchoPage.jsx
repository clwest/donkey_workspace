import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import apiFetch from '../../../utils/apiClient';

export default function MemoryEchoPage() {
  const { id } = useParams();
  const [effects, setEffects] = useState([]);

  useEffect(() => {
    async function fetchData() {
      const data = await apiFetch(`/memory-echo-effects?memory=${id}`);
      setEffects(data);
    }
    fetchData();
  }, [id]);

  return (
    <div className="container my-4">
      <h1>Memory Echo Preview</h1>
      <pre>{JSON.stringify(effects, null, 2)}</pre>
    </div>
  );
}

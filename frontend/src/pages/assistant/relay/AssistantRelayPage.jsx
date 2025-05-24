import { useParams } from 'react-router-dom';
import AssistantRelayPanel from '@/components/assistant/AssistantRelayPanel';

export default function AssistantRelayPage() {
  const { id } = useParams();
  return (
    <div className="container my-4">
      <h1 className="mb-3">Relay Console</h1>
      <AssistantRelayPanel slug={id} />
    </div>
  );
}

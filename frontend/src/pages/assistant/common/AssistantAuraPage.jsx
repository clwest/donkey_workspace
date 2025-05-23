import { useParams } from 'react-router-dom';
import { useEffect, useState } from 'react';
import apiFetch from '../../../utils/apiClient';
import ReflectiveUIAnimationLayer from '../../../components/animation/ReflectiveUIAnimationLayer';

export default function AssistantAuraPage() {
  const { id } = useParams();
  const [assistant, setAssistant] = useState(null);

  useEffect(() => {
    apiFetch(`/assistants/${id}`).then(setAssistant).catch(() => {});
  }, [id]);

  if (!assistant) return <div className="container my-4">Loading...</div>;

  return (
    <div className="container my-4">
      <h1>{assistant.name} Aura</h1>
      <ReflectiveUIAnimationLayer codexTone="neutral" memoryEntropy={0.5} ritualPerformance={0.5} traitBlend={0.5}>
        <p>This is where aura adjustments would appear.</p>
      </ReflectiveUIAnimationLayer>
    </div>
  );
}

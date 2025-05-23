import { useState } from 'react';
import ReflectiveUIAnimationLayer from '../../components/animation/ReflectiveUIAnimationLayer';

export default function MotionTestPage() {
  const [tone, setTone] = useState('neutral');
  const [entropy, setEntropy] = useState(0.5);
  const [performance, setPerformance] = useState(0.5);
  const [blend, setBlend] = useState(0.5);

  return (
    <div className="container my-4">
      <h1>Symbolic Motion Test</h1>
      <div className="mb-3">
        <label className="form-label">Codex Tone</label>
        <input className="form-control" value={tone} onChange={e => setTone(e.target.value)} />
      </div>
      <ReflectiveUIAnimationLayer
        codexTone={tone}
        memoryEntropy={entropy}
        ritualPerformance={performance}
        traitBlend={blend}
      >
        <div className="p-5 border">Preview Motion</div>
      </ReflectiveUIAnimationLayer>
    </div>
  );
}

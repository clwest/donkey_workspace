export function symbolicMotionEngine({ codexTone = 'neutral', memoryEntropy = 0.5, ritualPerformance = 0.5, traitBlend = 0.5 }) {
  const intensity = (memoryEntropy + ritualPerformance + traitBlend) / 3;
  let transitionStyle = intensity > 0.7 ? 'dramatic' : intensity > 0.4 ? 'fluid' : 'subtle';
  let overlayState = codexTone === 'ominous' ? 'dark' : 'light';
  let symbolicModifier = intensity > 0.8 ? 'vibration' : intensity < 0.3 ? 'drift' : 'gravity';
  return { transitionStyle, overlayState, symbolicModifier };
}

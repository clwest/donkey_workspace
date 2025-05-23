import { symbolicMotionEngine } from '../../utils/symbolicMotionEngine';

export default function ReflectiveUIAnimationLayer({ codexTone, memoryEntropy, ritualPerformance, traitBlend, children }) {
  const { transitionStyle, overlayState, symbolicModifier } = symbolicMotionEngine({ codexTone, memoryEntropy, ritualPerformance, traitBlend });
  const className = `motion-${transitionStyle} overlay-${overlayState} mod-${symbolicModifier}`;
  return <div className={className}>{children}</div>;
}

import useOnboardingTracker from "@/hooks/useOnboardingTracker";

export default function OnboardingProgressBar() {
  const { percent } = useOnboardingTracker();
  return (
    <div className="progress mb-3">
      <div className="progress-bar" style={{ width: `${percent || 0}%` }} />
    </div>
  );
}

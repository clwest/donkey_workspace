import MythOnboardingWorld from "../../components/mythos/MythOnboardingWorld";
import OnboardingProgressPanel from "../../components/onboarding/OnboardingProgressPanel";
import useOnboardingGuard from "../../onboarding/useOnboardingGuard";

export default function MythOnboardingWorldPage() {
  useOnboardingGuard("world");
  return (
    <div className="container my-4">
      <OnboardingProgressPanel />
      <MythOnboardingWorld />
    </div>
  );
}

import ArchetypeSelectionChamber from "../../components/mythos/ArchetypeSelectionChamber";
import OnboardingProgressPanel from "../../components/onboarding/OnboardingProgressPanel";
import useOnboardingGuard from "../../onboarding/useOnboardingGuard";

export default function ArchetypeSelectionChamberPage() {
  useOnboardingGuard("archetype");

  return (
    <div className="container my-4">
      <OnboardingProgressPanel />
      <ArchetypeSelectionChamber />
    </div>
  );
}

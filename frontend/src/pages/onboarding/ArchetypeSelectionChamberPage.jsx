import ArchetypeSelectionChamber from "../../components/mythos/ArchetypeSelectionChamber";
import OnboardingProgressPanel from "../../components/onboarding/OnboardingProgressPanel";
import OnboardingProgressBar from "../../components/onboarding/OnboardingProgressBar";
import GuideChatPanel from "../../components/onboarding/GuideChatPanel";
import useOnboardingGuard from "../../onboarding/useOnboardingGuard";

export default function ArchetypeSelectionChamberPage() {
  const { progress } = useOnboardingGuard("archetype");
  if (!progress) return <div className="container my-5">Loading...</div>;

  return (
    <div className="container my-4">
      <GuideChatPanel />
      <OnboardingProgressBar />
      <OnboardingProgressPanel />
      <ArchetypeSelectionChamber />
    </div>
  );
}

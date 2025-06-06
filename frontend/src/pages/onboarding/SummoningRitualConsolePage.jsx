import SummoningRitualConsole from "../../components/mythos/SummoningRitualConsole";
import OnboardingProgressPanel from "../../components/onboarding/OnboardingProgressPanel";
import OnboardingProgressBar from "../../components/onboarding/OnboardingProgressBar";
import useOnboardingGuard from "../../onboarding/useOnboardingGuard";

export default function SummoningRitualConsolePage() {
  useOnboardingGuard("summon");

  return (
    <div className="container my-4">
      <OnboardingProgressBar />
      <OnboardingProgressPanel />
      <SummoningRitualConsole />
    </div>
  );
}

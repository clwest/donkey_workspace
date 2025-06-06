import SummoningRitualConsole from "../../components/mythos/SummoningRitualConsole";
import OnboardingProgressPanel from "../../components/onboarding/OnboardingProgressPanel";
import useOnboardingGuard from "../../onboarding/useOnboardingGuard";

export default function SummoningRitualConsolePage() {
  useOnboardingGuard("summon");

  return (
    <div className="container my-4">
      <OnboardingProgressPanel />
      <SummoningRitualConsole />
    </div>
  );
}

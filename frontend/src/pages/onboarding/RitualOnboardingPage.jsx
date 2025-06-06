import CinematicUILayer from "../../components/cinematic/CinematicUILayer";
import OnboardingProgressPanel from "../../components/onboarding/OnboardingProgressPanel";
import OnboardingProgressBar from "../../components/onboarding/OnboardingProgressBar";
import useOnboardingGuard from "../../onboarding/useOnboardingGuard";

export default function RitualOnboardingPage() {
  useOnboardingGuard("ritual");

  return (
    <CinematicUILayer title="Ritual Onboarding">
      <OnboardingProgressBar />
      <OnboardingProgressPanel />
      <p>Begin your mythic journey.</p>
    </CinematicUILayer>
  );
}

import CinematicUILayer from "../../components/cinematic/CinematicUILayer";
import OnboardingProgressPanel from "../../components/onboarding/OnboardingProgressPanel";
import OnboardingProgressBar from "../../components/onboarding/OnboardingProgressBar";
import GuideChatPanel from "../../components/onboarding/GuideChatPanel";
import useOnboardingGuard from "../../onboarding/useOnboardingGuard";

export default function RitualOnboardingPage() {
  const { progress } = useOnboardingGuard("ritual");
  if (!progress) return <div className="container my-5">Loading...</div>;

  return (
    <CinematicUILayer title="Ritual Onboarding">
      <GuideChatPanel />
      <OnboardingProgressBar />
      <OnboardingProgressPanel />
      <p>Begin your mythic journey.</p>
    </CinematicUILayer>
  );
}

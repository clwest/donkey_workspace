import UserMythpathInitializer from "../../components/mythos/UserMythpathInitializer";
import OnboardingProgressPanel from "../../components/onboarding/OnboardingProgressPanel";
import OnboardingProgressBar from "../../components/onboarding/OnboardingProgressBar";
import useOnboardingGuard from "../../onboarding/useOnboardingGuard";

export default function UserMythpathInitializerPage() {
  const { progress } = useOnboardingGuard("mythpath");
  if (!progress) return <div className="container my-5">Loading...</div>;

  return (
    <div className="container my-4">
      <OnboardingProgressBar />
      <OnboardingProgressPanel />
      <UserMythpathInitializer />
    </div>
  );
}

import UserMythpathInitializer from "../../components/mythos/UserMythpathInitializer";
import OnboardingProgressPanel from "../../components/onboarding/OnboardingProgressPanel";
import OnboardingProgressBar from "../../components/onboarding/OnboardingProgressBar";
import useOnboardingGuard from "../../onboarding/useOnboardingGuard";

export default function UserMythpathInitializerPage() {
  useOnboardingGuard("mythpath");

  return (
    <div className="container my-4">
      <OnboardingProgressBar />
      <OnboardingProgressPanel />
      <UserMythpathInitializer />
    </div>
  );
}

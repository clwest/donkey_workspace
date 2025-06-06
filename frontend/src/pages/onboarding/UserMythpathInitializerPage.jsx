import UserMythpathInitializer from "../../components/mythos/UserMythpathInitializer";
import OnboardingProgressPanel from "../../components/onboarding/OnboardingProgressPanel";
import useOnboardingGuard from "../../onboarding/useOnboardingGuard";

export default function UserMythpathInitializerPage() {
  useOnboardingGuard("mythpath");

  return (
    <div className="container my-4">
      <OnboardingProgressPanel />
      <UserMythpathInitializer />
    </div>
  );
}

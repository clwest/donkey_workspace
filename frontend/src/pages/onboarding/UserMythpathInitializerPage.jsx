import UserMythpathInitializer from "../../components/mythos/UserMythpathInitializer";
import OnboardingProgressPanel from "../../components/onboarding/OnboardingProgressPanel";
import OnboardingProgressBar from "../../components/onboarding/OnboardingProgressBar";
import GuideChatPanel from "../../components/onboarding/GuideChatPanel";
import useOnboardingGuard from "../../onboarding/useOnboardingGuard";
import useOnboardingTracker from "@/hooks/useOnboardingTracker";

export default function UserMythpathInitializerPage() {
  const { progress } = useOnboardingGuard("mythpath");
  useOnboardingTracker();
  if (!progress) return <div className="container my-5">Loading...</div>;

  return (
    <div className="container my-4">
      <GuideChatPanel />
      <OnboardingProgressBar />
      <OnboardingProgressPanel />
      <UserMythpathInitializer />
    </div>
  );
}

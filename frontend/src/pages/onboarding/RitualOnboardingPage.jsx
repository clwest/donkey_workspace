import CinematicUILayer from "../../components/cinematic/CinematicUILayer";
import OnboardingProgressPanel from "../../components/onboarding/OnboardingProgressPanel";
import OnboardingProgressBar from "../../components/onboarding/OnboardingProgressBar";
import GuideChatPanel from "../../components/onboarding/GuideChatPanel";
import useOnboardingGuard from "../../onboarding/useOnboardingGuard";
import useOnboardingTracker from "@/hooks/useOnboardingTracker";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";

export default function RitualOnboardingPage() {
  const navigate = useNavigate();
  const { progress } = useOnboardingGuard("ritual");
  const { completeStep } = useOnboardingTracker();
  if (!progress) return <div className="container my-5">Loading...</div>;

  const finish = async () => {
    await completeStep("ritual");
    toast.success("\ud83c\udf89 Onboarding Complete!");
    navigate("/assistants/launch", { replace: true });
  };

  return (
    <CinematicUILayer title="Ritual Onboarding">
      <GuideChatPanel />
      <OnboardingProgressBar />
      <OnboardingProgressPanel />
      <p>Begin your mythic journey.</p>
      <button className="btn btn-success mt-3" onClick={finish}>
        Finish
      </button>
    </CinematicUILayer>
  );
}

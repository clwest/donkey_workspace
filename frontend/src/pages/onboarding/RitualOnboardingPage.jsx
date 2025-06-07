import CinematicUILayer from "../../components/cinematic/CinematicUILayer";
import OnboardingProgressPanel from "../../components/onboarding/OnboardingProgressPanel";
import OnboardingProgressBar from "../../components/onboarding/OnboardingProgressBar";
import GuideChatPanel from "../../components/onboarding/GuideChatPanel";
import OnboardingHelpButton from "../../components/onboarding/OnboardingHelpButton";
import useOnboardingGuard from "../../onboarding/useOnboardingGuard";
import useOnboardingTracker from "@/hooks/useOnboardingTracker";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";

export default function RitualOnboardingPage() {
  const navigate = useNavigate();
  const { progress } = useOnboardingGuard("ritual");
  const { completeStep } = useOnboardingTracker();
  const [showAnim, setShowAnim] = useState(false);
  if (!progress) return <div className="container my-5">Loading...</div>;

  const finish = async () => {
    const res = await completeStep("ritual");
    toast.success("Your assistant has awakened. Let's begin.");
    setShowAnim(true);
    if (localStorage.getItem("playSfx") === "true") {
      try {
        new Audio("/static/success.mp3").play();
      } catch (e) {}
    }
    const slug = res.slug || res.redirect?.split("/").filter(Boolean).pop();
    setTimeout(() => {
      if (slug) {
        navigate(`/assistants/${slug}/`, { replace: true });
      } else {
        navigate("/assistants/launch", { replace: true });
      }
    }, 3500);
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
      {showAnim && (
        <div className="ritual-animation">
          <div className="ritual-avatar" />
          <h2 className="ritual-welcome">Welcome</h2>
        </div>
      )}
      <OnboardingHelpButton />
    </CinematicUILayer>
  );
}

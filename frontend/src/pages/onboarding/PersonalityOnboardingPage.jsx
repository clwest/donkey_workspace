import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import OnboardingProgressPanel from "../../components/onboarding/OnboardingProgressPanel";
import useOnboardingGuard from "../../onboarding/useOnboardingGuard";
import useUserInfo from "@/hooks/useUserInfo";
import TonePreview from "../../components/onboarding/TonePreview";
import AvatarSelector from "../../components/onboarding/AvatarSelector";
import GuideChatPanel from "../../components/onboarding/GuideChatPanel";

const TONES = ["cheerful", "formal", "nerdy", "zen", "friendly", "mysterious"];

export default function PersonalityOnboardingPage() {
  const { progress } = useOnboardingGuard("personality");
  const navigate = useNavigate();
  const location = useLocation();
  const userInfo = useUserInfo();
  const [tone, setTone] = useState(location.state?.tone_profile || "friendly");
  const [avatar, setAvatar] = useState(location.state?.avatar_style || "robot");

  useEffect(() => {
    if (!userInfo) return;
    if (userInfo.onboarding_complete && userInfo.has_assistants) {
      navigate("/home", { replace: true });
      return;
    }
    if (userInfo.avatar_style || userInfo.tone_profile) {
      setTone(userInfo.tone_profile || "friendly");
      setAvatar(userInfo.avatar_style || "robot");
      if (userInfo.avatar_style && userInfo.tone_profile) {
        navigate("/assistants/create", {
          replace: true,
          state: { tone_profile: userInfo.tone_profile, avatar_style: userInfo.avatar_style },
        });
      }
    }
  }, [userInfo, navigate]);

  if (!progress) return <div className="container my-5">Loading...</div>;

  const handleNext = () => {
    navigate("/assistants/create", {
      state: { tone, avatar_style: avatar, tone_profile: tone },
    });
  };

  return (
    <div className="container my-4">
      <GuideChatPanel />
      <OnboardingProgressPanel />
      <h2>Choose Personality</h2>
      <div className="mb-3">
        <label className="form-label">Tone</label>
        <div className="d-flex flex-wrap gap-2 mb-2">
          {TONES.map((t) => (
            <button
              key={t}
              className={`btn btn-sm ${tone === t ? "btn-primary" : "btn-outline-secondary"}`}
              onClick={() => setTone(t)}
            >
              {t}
            </button>
          ))}
        </div>
        <TonePreview tone={tone} />
      </div>
      <div className="mb-4">
        <label className="form-label">Avatar</label>
        <AvatarSelector value={avatar} onChange={setAvatar} />
      </div>
      <button className="btn btn-success" onClick={handleNext}>
        Save &amp; Continue
      </button>
    </div>
  );
}

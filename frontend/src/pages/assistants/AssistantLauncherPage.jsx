import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import AssistantDemoPage from "../assistant/common/AssistantDemoPage";
import HintBubble from "../../components/HintBubble";
import useAssistantHints from "../../hooks/useAssistantHints";
import useOnboardingTracker from "../../hooks/useOnboardingTracker";
import useUserInfo from "../../hooks/useUserInfo";
import useAuthGuard from "../../hooks/useAuthGuard";
import OnboardingProgressBar from "../../components/onboarding/OnboardingProgressBar";
import AssistantSetupSummary from "../../components/assistant/AssistantSetupSummary";

export default function AssistantLauncherPage() {
  useAuthGuard();
  const navigate = useNavigate();
  const userInfo = useUserInfo();
  const { progress } = useOnboardingTracker();
  const { hints, dismissHint } = useAssistantHints("launcher");
  const [primary, setPrimary] = useState(null);

  useEffect(() => {
    if (userInfo?.assistant_count > 0) {
      fetch("/api/assistants/primary/")
        .then((res) => res.json())
        .then(setPrimary)
        .catch(() => {});
    }
  }, [userInfo]);

  const glossaryDone =
    progress?.find((p) => p.step === "glossary")?.status === "completed";

  return (
    <div className="container my-4 position-relative">
      <OnboardingProgressBar />
      {hints.find((h) => h.id === "launcher_intro" && !h.dismissed) && (
        <HintBubble
          label={hints.find((h) => h.id === "launcher_intro").label}
          content={hints.find((h) => h.id === "launcher_intro").content}
          onDismiss={() => dismissHint("launcher_intro")}
          position={{ top: 60, right: 20 }}
        />
      )}
      <h1 className="mb-3">Choose your AI guide…</h1>
      {glossaryDone && primary && (
        <div className="mb-4">
          <AssistantSetupSummary assistant={primary} />
        </div>
      )}
      {primary && (
        <button
          className="btn btn-success me-2 mb-3"
          onClick={() => navigate(`/assistants/${primary.slug}`)}
        >
          Continue with {primary.name}
        </button>
      )}
      <button
        id="new-assistant-btn"
        className={`btn btn-primary mb-4 ${
          hints.find((h) => h.id === "launcher_choose_path" && !h.dismissed)
            ? "pulse"
            : ""
        }`}
        onClick={() => navigate("/assistants/create")}
      >
        Create New Assistant
      </button>
      {hints.find((h) => h.id === "launcher_choose_path" && !h.dismissed) && (
        <HintBubble
          label={hints.find((h) => h.id === "launcher_choose_path").label}
          content={hints.find((h) => h.id === "launcher_choose_path").content}
          highlightSelector="#new-assistant-btn"
          onDismiss={() => dismissHint("launcher_choose_path")}
        />
      )}
      <AssistantDemoPage />
    </div>
  );
}

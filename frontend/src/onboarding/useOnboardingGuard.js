import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import useOnboardingTracker from "@/hooks/useOnboardingTracker";
import useUserInfo from "@/hooks/useUserInfo";

export const STEP_ROUTES = {
  mythpath: "/onboarding",
  world: "/onboarding/world",
  glossary: "/onboarding/glossary",
  archetype: "/onboarding/archetype",
  summon: "/onboarding/summon",
  personality: "/onboarding/personality",
  wizard: "/onboarding/wizard",
  ritual: "/onboarding/ritual",
};

export default function useOnboardingGuard(step) {
  const navigate = useNavigate();
  const { progress, nextStep, completeStep } = useOnboardingTracker();
  const userInfo = useUserInfo();

  useEffect(() => {
    completeStep(step);
  }, [completeStep, step]);

  useEffect(() => {
    if (!progress || !userInfo) return;
    if (userInfo.has_assistants) {
      if (userInfo.onboarding_complete) {
        navigate("/home", { replace: true });
        return;
      }
      const stepSlug = userInfo.pending_onboarding_step || nextStep;
      if (stepSlug && stepSlug !== step) {
        navigate(STEP_ROUTES[stepSlug], { replace: true });
        return;
      }
    }
    const firstIncomplete = progress.find((p) => p.status !== "completed");
    if (!firstIncomplete) {
      navigate("/assistants/create", { replace: true });
      return;
    }
    if (firstIncomplete.step !== step) {
      navigate(STEP_ROUTES[firstIncomplete.step], { replace: true });
    }
  }, [progress, userInfo, nextStep, navigate, step]);

  return { progress };
}

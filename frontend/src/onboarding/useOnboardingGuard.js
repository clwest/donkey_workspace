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
  const { progress, completeStep, onboardingComplete } = useOnboardingTracker();
  const userInfo = useUserInfo();

  useEffect(() => {
    if (!localStorage.getItem("access")) {
      navigate(`/login?next=${STEP_ROUTES[step]}`, { replace: true });
      return;
    }
  }, [navigate, step]);

  useEffect(() => {
    if (!localStorage.getItem("access")) return;
    const status = progress?.find((p) => p.step === step)?.status;
    if (status !== "completed") {
      completeStep(step);
    }
  }, [completeStep, step, progress]);

  useEffect(() => {
    if (!progress || !userInfo) return;

    if (progress.every((p) => p.status === "pending") && step !== "mythpath") {
      navigate("/onboarding", { replace: true });
      return;
    }

    if (userInfo.onboarding_complete || onboardingComplete) {
      navigate("/assistants/create", { replace: true });
    }
  }, [progress, userInfo, onboardingComplete, navigate, step]);

  return { progress };
}

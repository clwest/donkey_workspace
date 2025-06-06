import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import useOnboardingTracker from "@/hooks/useOnboardingTracker";

export const STEP_ROUTES = {
  mythpath: "/onboarding",
  world: "/onboarding/world",
  archetype: "/onboarding/archetype",
  summon: "/onboarding/summon",
  wizard: "/onboarding/wizard",
  ritual: "/onboarding/ritual",
};

export default function useOnboardingGuard(step) {
  const navigate = useNavigate();
  const { progress, completeStep } = useOnboardingTracker();

  useEffect(() => {
    completeStep(step);
  }, [completeStep, step]);

  useEffect(() => {
    if (!progress) return;
    const firstIncomplete = progress.find((p) => p.status !== "completed");
    if (!firstIncomplete) {
      navigate("/assistants/create", { replace: true });
      return;
    }
    if (firstIncomplete.step !== step) {
      navigate(STEP_ROUTES[firstIncomplete.step], { replace: true });
    }
  }, [progress, navigate, step]);

  return { progress };
}

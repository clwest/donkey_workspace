import { useEffect, useState, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import apiFetch from "@/utils/apiClient";

export default function useOnboardingTracker(theme = "fantasy") {
  const navigate = useNavigate();
  const [status, setStatus] = useState(null);
  const completedRef = useRef(
    JSON.parse(localStorage.getItem("onboardingCompleted") || "{}")
  );
  const [complete, setComplete] = useState(
    localStorage.getItem("onboarding_complete") === "true"
  );

  const refreshStatus = useCallback(async () => {
    if (!localStorage.getItem("access")) return;
    try {
      const res = await apiFetch(`/onboarding/status/?theme=${theme}`);
      setStatus(res);
      if (res.onboarding_complete || res.next_step === null) {
        setComplete(true);
        localStorage.setItem("onboarding_complete", "true");
      }
      const steps = {};
      res.progress?.forEach((p) => {
        if (p.status === "completed") steps[p.step] = true;
      });
      completedRef.current = steps;
      localStorage.setItem("onboardingCompleted", JSON.stringify(steps));
      return res;
    } catch (err) {
      console.error("onboarding status error", err);
    }
  }, [theme]);

  const completeStep = useCallback(
    async (step) => {
      if (!localStorage.getItem("access")) return;
      if (localStorage.getItem("onboarding_complete") === "true") {
        setComplete(true);
        return { onboarding_complete: true };
      }
      if (completedRef.current[step]) return status;
      try {
        const res = await apiFetch("/onboarding/complete/", {
          method: "POST",
          body: { step },
        });
        setStatus(res);
        completedRef.current[step] = true;
        localStorage.setItem(
          "onboardingCompleted",
          JSON.stringify(completedRef.current)
        );
        if (res.onboarding_complete || res.next_step === null) {
          setComplete(true);
          localStorage.setItem("onboarding_complete", "true");
          try {
            const info = await apiFetch("/user/");
            navigate(
              info.assistant_count > 0 ? "/home" : "/assistants/create",
              { replace: true }
            );
          } catch {}
        }
        return res;
      } catch (err) {
        console.error("complete step error", err);
      }
    },
    [status]
  );

  useEffect(() => {
    if (localStorage.getItem("access")) {
      refreshStatus();
    }
  }, [refreshStatus]);

  useEffect(() => {
    if (process.env.NODE_ENV === "development" && status) {
      // eslint-disable-next-line no-console
      console.log("[onboarding] status", status);
    }
  }, [status]);

  return {
    progress: status?.progress,
    nextStep: status?.next_step,
    percent: status?.percent,
    showIntro: status?.show_intro,
    aliases: status?.aliases,
    onboardingComplete: complete,
    refreshStatus,
    completeStep,
  };
}

import { useEffect, useState } from "react";
import apiFetch from "@/utils/apiClient";

export default function useOnboardingTracker() {
  const [status, setStatus] = useState(null);

  const refreshStatus = async () => {
    try {
      const res = await apiFetch("/onboarding/status/");
      setStatus(res);
      return res;
    } catch (err) {
      console.error("onboarding status error", err);
    }
  };

  const completeStep = async (step) => {
    try {
      const res = await apiFetch("/onboarding/complete/", {
        method: "POST",
        body: { step },
      });
      setStatus(res);
      return res;
    } catch (err) {
      console.error("complete step error", err);
    }
  };

  useEffect(() => {
    refreshStatus();
  }, []);

  return {
    progress: status?.progress,
    nextStep: status?.next_step,
    percent: status?.percent,
    showIntro: status?.show_intro,
    refreshStatus,
    completeStep,
  };
}

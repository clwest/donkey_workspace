import { useEffect, useState } from "react";
import apiFetch from "@/utils/apiClient";

export default function useOnboardingTracker() {
  const [progress, setProgress] = useState(null);

  const refreshStatus = async () => {
    try {
      const res = await apiFetch("/onboarding/status/");
      setProgress(res.progress);
      return res.progress;
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
      setProgress(res.progress);
      return res.progress;
    } catch (err) {
      console.error("complete step error", err);
    }
  };

  useEffect(() => {
    refreshStatus();
  }, []);

  return { progress, refreshStatus, completeStep };
}

import { useEffect, useState } from "react";
import apiFetch from "@/utils/apiClient";

export default function useOnboardingIntro() {
  const [intro, setIntro] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchIntro = async () => {
    try {
      const data = await apiFetch("/onboarding/intro/");
      setIntro(data);
    } catch (err) {
      console.error("intro fetch", err);
    } finally {
      setLoading(false);
    }
  };

  const dismissIntro = async () => {
    try {
      await apiFetch("/onboarding/intro/", { method: "POST" });
    } catch (err) {
      console.error("dismiss intro", err);
    }
    setIntro((i) => (i ? { ...i, show_intro: false } : i));
  };

  useEffect(() => {
    fetchIntro();
  }, []);

  return { intro, loading, dismissIntro, refreshIntro: fetchIntro };
}

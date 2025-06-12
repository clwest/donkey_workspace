import { useEffect, useState } from "react";
import apiFetch from "@/utils/apiClient";

export default function useOnboardingStatus() {
  const [loading, setLoading] = useState(true);
  const [primarySlug, setPrimarySlug] = useState(null);
  const [onboardingComplete, setOnboardingComplete] = useState(false);

  useEffect(() => {
    let active = true;
    apiFetch('/debug/assistant_routing/', { allowUnauthenticated: true })
      .then((res) => {
        if (!active) return;
        setPrimarySlug(res.primary_slug || null);
        setOnboardingComplete(!!res.onboarding_complete);
      })
      .catch(() => {})
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  return { loading, primarySlug, onboardingComplete };
}

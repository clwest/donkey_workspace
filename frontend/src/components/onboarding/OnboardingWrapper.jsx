import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import useOnboardingStatus from "@/hooks/useOnboardingStatus";

export default function OnboardingWrapper({ children }) {
  const { loading, onboardingComplete, primarySlug } = useOnboardingStatus();
  const navigate = useNavigate();

  useEffect(() => {
    if (!loading && onboardingComplete) {
      navigate(`/assistants/${primarySlug}`, { replace: true });
    }
  }, [loading, onboardingComplete, primarySlug, navigate]);

  if (loading) return <div className="text-center mt-5">Loading...</div>;
  return children;
}

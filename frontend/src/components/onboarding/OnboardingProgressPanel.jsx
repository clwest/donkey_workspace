import useOnboardingTracker from "@/hooks/useOnboardingTracker";
import { useMemo } from "react";

const STEP_ROUTES = [
  "mythpath",
  "world",
  "glossary",
  "archetype",
  "summon",
  "wizard",
  "ritual",
];

export default function OnboardingProgressPanel() {
  const { progress } = useOnboardingTracker();

  const firstIncomplete = useMemo(() => {
    if (!progress) return null;
    return progress.find((p) => p.status !== "completed");
  }, [progress]);

  return (
    <ul className="list-unstyled mb-3">
      {STEP_ROUTES.map((step, idx) => {
        const entry = progress?.find((p) => p.step === step);
        const status = entry?.status || "pending";
        let icon = "⬜";
        if (status === "completed") icon = "✅";
        else if (firstIncomplete && firstIncomplete.step === step) icon = "🔄";
        const label = step.charAt(0).toUpperCase() + step.slice(1);
        return (
          <li key={step}>
            {icon} Step {idx + 1}: {label}
          </li>
        );
      })}
    </ul>
  );
}

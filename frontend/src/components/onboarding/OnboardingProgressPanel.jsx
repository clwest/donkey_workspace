import useOnboardingTracker from "@/hooks/useOnboardingTracker";
import { useMemo } from "react";
import { ONBOARDING_WORLD } from "../../onboarding/metadata";
import useOnboardingTheme from "../../onboarding/useOnboardingTheme";

const STEP_ORDER = ONBOARDING_WORLD.nodes.map((n) => n.slug);

export default function OnboardingProgressPanel() {
  const { progress } = useOnboardingTracker();
  const { theme } = useOnboardingTheme();

  const firstIncomplete = useMemo(() => {
    if (!progress) return null;
    return progress.find((p) => p.status !== "completed");
  }, [progress]);

  return (
    <ul className="list-unstyled mb-3">
      {STEP_ORDER.map((step, idx) => {
        const entry = progress?.find((p) => p.step === step);
        const status = entry?.status || "pending";
        let icon = "⬜";
        if (status === "completed") icon = "✅";
        else if (firstIncomplete && firstIncomplete.step === step) icon = "🔄";
        const node = ONBOARDING_WORLD.nodes.find((n) => n.slug === step);
        const label =
          theme === "fantasy"
            ? node.title
            : node.ui_label || node.title;
        return (
          <li key={step}>
            {icon} Step {idx + 1}: {label}
          </li>
        );
      })}
    </ul>
  );
}

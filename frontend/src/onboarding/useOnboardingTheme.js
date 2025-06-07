import { useState } from "react";

export default function useOnboardingTheme() {
  const [theme, setTheme] = useState(
    localStorage.getItem("onboardingTheme") || "fantasy"
  );

  const toggle = (next) => {
    const val = next || (theme === "fantasy" ? "practical" : "fantasy");
    setTheme(val);
    localStorage.setItem("onboardingTheme", val);
  };

  return { theme, toggle };
}

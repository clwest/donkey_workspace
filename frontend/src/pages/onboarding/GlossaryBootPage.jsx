import { useEffect, useState } from "react";
import apiFetch from "@/utils/apiClient";
import useOnboardingGuard from "../../onboarding/useOnboardingGuard";
import useOnboardingTracker from "@/hooks/useOnboardingTracker";
import GlossaryAnchorCard from "../../components/onboarding/GlossaryAnchorCard";
import TeachAnchorModal from "../../components/onboarding/TeachAnchorModal";

export default function GlossaryBootPage() {
  const { progress, completeStep } = useOnboardingGuard("glossary");
  const { nextStep } = useOnboardingTracker();
  const [anchors, setAnchors] = useState([]);
  const [taught, setTaught] = useState(false);

  useEffect(() => {
    if (!progress) return;
    apiFetch("/onboarding/glossary_boot/")
      .then((res) => setAnchors(res.results))
      .catch((err) => console.error("glossary boot", err));
  }, [progress]);

  const teach = async (anchor) => {
    try {
      await apiFetch("/onboarding/teach_anchor/", {
        method: "POST",
        body: { anchor_slug: anchor.slug },
      });
      localStorage.setItem("boot_anchor_slug", anchor.slug);
      setTaught(true);
      completeStep("glossary");
    } catch (err) {
      console.error("teach anchor", err);
    }
  };

  if (!progress) {
    return <div className="container my-5">Loading...</div>;
  }

  return (
    <div className="container my-4">
      <h2>Glossary Preview</h2>
      {localStorage.getItem("boot_anchor_slug") && nextStep !== "glossary" && (
        <div className="alert alert-success">
          You taught: {localStorage.getItem("boot_anchor_slug")}
        </div>
      )}
      <div className="d-flex flex-wrap gap-3">
        {anchors.map((a) => (
          <GlossaryAnchorCard key={a.slug} anchor={a} onTeach={teach} />
        ))}
      </div>
      <TeachAnchorModal show={taught} onClose={() => setTaught(false)} />
    </div>
  );
}

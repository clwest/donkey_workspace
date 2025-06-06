import { useEffect, useState } from "react";
import apiFetch from "@/utils/apiClient";
import useOnboardingGuard from "../../onboarding/useOnboardingGuard";
import GlossaryAnchorCard from "../../components/onboarding/GlossaryAnchorCard";
import TeachAnchorModal from "../../components/onboarding/TeachAnchorModal";

export default function GlossaryBootPage() {
  const { completeStep } = useOnboardingGuard("glossary");
  const [anchors, setAnchors] = useState([]);
  const [taught, setTaught] = useState(false);

  useEffect(() => {
    apiFetch("/onboarding/glossary_boot/")
      .then((res) => setAnchors(res.results))
      .catch((err) => console.error("glossary boot", err));
  }, []);

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

  return (
    <div className="container my-4">
      <h2>Glossary Preview</h2>
      <div className="d-flex flex-wrap gap-3">
        {anchors.map((a) => (
          <GlossaryAnchorCard key={a.slug} anchor={a} onTeach={teach} />
        ))}
      </div>
      <TeachAnchorModal show={taught} onClose={() => setTaught(false)} />
    </div>
  );
}

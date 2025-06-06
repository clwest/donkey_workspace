import { Modal, Button } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import useOnboardingIntro from "@/hooks/useOnboardingIntro";
import useOnboardingTracker from "@/hooks/useOnboardingTracker";
import { STEP_ROUTES } from "../../onboarding/useOnboardingGuard";

export default function OnboardingIntroModal() {
  const { intro, dismissIntro } = useOnboardingIntro();
  const { nextStep, showIntro, refreshStatus } = useOnboardingTracker();
  const navigate = useNavigate();

  if (!intro) return null;
  const show = nextStep === "world" && showIntro;

  const start = () => {
    dismissIntro();
    navigate(STEP_ROUTES.mythpath);
    refreshStatus();
  };

  const skip = () => {
    dismissIntro();
    refreshStatus();
  };

  return (
    <Modal show={show} onHide={skip} centered>
      <Modal.Header closeButton>
        <Modal.Title>{intro.title}</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <p>{intro.welcome}</p>
        <ul className="list-unstyled">
          {intro.steps.map((s) => (
            <li key={s.slug} className="mb-1">
              <span className="me-2">{s.emoji}</span>
              <strong>{s.name}</strong> &mdash; {s.goal}
            </li>
          ))}
        </ul>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={skip}>
          Skip Tour
        </Button>
        <Button variant="primary" onClick={start}>
          Let&apos;s begin!
        </Button>
      </Modal.Footer>
    </Modal>
  );
}

import React, { useState, useEffect } from "react";
import Joyride, { STATUS, EVENTS } from "react-joyride";
import { useNavigate, useLocation } from "react-router-dom";
import PropTypes from "prop-types";

export default function Tour({ steps, onFinish }) {
  const [run, setRun] = useState(false);
  const [stepIndex, setStepIndex] = useState(0);
  const navigate = useNavigate();
  const location = useLocation();

  const waitForTarget = (selector, attempts = 0) => {
    if (!selector) return setRun(true);
    const targetElement = document.querySelector(selector);
    if (targetElement) {
      setRun(true);
    } else if (attempts < 20) {
      setTimeout(() => waitForTarget(selector, attempts + 1), 200);
    }
  };

  const handleCallback = (data) => {
    const { status, type, index } = data;

    if (type === EVENTS.STEP_AFTER) {
      const next = index + 1;
      setRun(false);
      setStepIndex(next);
      return;
    }

    if ([STATUS.FINISHED, STATUS.SKIPPED].includes(status)) {
      setRun(false);
      onFinish && onFinish();
    }
  };

  useEffect(() => {
    setStepIndex(0);
    const first = steps[0];
    if (first) {
      if (first.path && first.path !== location.pathname) {
        navigate(first.path);
      }
      waitForTarget(first.target);
    }
  }, [steps]);

  useEffect(() => {
    const step = steps[stepIndex];
    if (!step) return;
    if (step.path && step.path !== location.pathname) {
      navigate(step.path);
    }
    waitForTarget(step.target);
  }, [stepIndex, location.pathname]);

  return (
    <Joyride
      steps={steps}
      run={run}
      continuous
      showProgress
      showSkipButton
      callback={handleCallback}
      styles={{ options: { zIndex: 10000 } }}
    />
  );
}

Tour.propTypes = {
  steps: PropTypes.array.isRequired,
  onFinish: PropTypes.func,
};

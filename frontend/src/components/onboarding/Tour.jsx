import React, { useState, useEffect } from "react";
import Joyride, { STATUS } from "react-joyride";
import { useNavigate, useLocation } from "react-router-dom";
import PropTypes from "prop-types";

export default function Tour({ steps, onFinish }) {
  const [run, setRun] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();

  const handleCallback = (data) => {
    const { status, index } = data;
    const step = steps[index];
    if (step && step.path && step.path !== location.pathname) {
      navigate(step.path);
    }
    if ([STATUS.FINISHED, STATUS.SKIPPED].includes(status)) {
      setRun(false);
      onFinish && onFinish();
    }
  };

  useEffect(() => {
    setRun(true);
  }, [steps]);

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

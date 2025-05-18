// components/common/LoadingSpinner.jsx
import React from "react";

const LoadingSpinner = ({ message = "Loading...", size = "md", className = "" }) => {
  const sizeClass = {
    sm: "spinner-border-sm",
    md: "",
    lg: "spinner-border-lg",
  }[size];

  return (
    <div className={`d-flex flex-column align-items-center justify-content-center ${className}`}>
      <div className={`spinner-border text-primary ${sizeClass}`} role="status" />
      {message && <div className="mt-2 text-muted">{message}</div>}
    </div>
  );
};

export default LoadingSpinner;
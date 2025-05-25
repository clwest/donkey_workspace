import React, { useEffect } from "react";
import { useLocation } from "react-router-dom";
import ComingSoon from "../components/common/ComingSoon";
import { SHOW_INACTIVE_ROUTES } from "../config/ui";

export default function PageNotFound() {
  const location = useLocation();
  useEffect(() => {
    console.warn("404 route visit:", location.pathname);
  }, [location]);
  if (SHOW_INACTIVE_ROUTES) {
    return <ComingSoon title={`Page not found: ${location.pathname}`} />;
  }
  return <div className="container my-5">Route not found.</div>;
}

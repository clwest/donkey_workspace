import React, { useEffect } from "react";
import { useLocation } from "react-router-dom";
import ComingSoon from "../components/ComingSoon";

export default function PageNotFound() {
  const location = useLocation();
  useEffect(() => {
    console.warn("404 route visit:", location.pathname);
  }, [location]);
  return <ComingSoon title={`Page not found: ${location.pathname}`} />;
}

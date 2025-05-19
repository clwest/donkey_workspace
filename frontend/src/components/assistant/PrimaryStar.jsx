import React from "react";

export default function PrimaryStar({ isPrimary }) {
  if (!isPrimary) return null;
  return (
    <span className="ms-1 text-warning" title="Primary Assistant" style={{fontSize: "0.9em"}}>
      ⭐
    </span>
  );
}

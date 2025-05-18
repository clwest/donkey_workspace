import { useState } from "react";

export default function AutoModeToggle({ enabled, onToggle }) {
  return (
    <div className="d-flex align-items-center gap-2 mt-3">
      <span>🌀 Auto-Mode:</span>
      <button
        className={`btn btn-sm ${enabled ? "btn-success" : "btn-outline-secondary"}`}
        onClick={() => onToggle(!enabled)}
      >
        {enabled ? "Enabled" : "Disabled"}
      </button>
    </div>
  );
}
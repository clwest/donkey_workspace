import React from "react";

export default function CinematicUILayer({ title, children }) {
  return (
    <div className="cinematic-layer position-relative">
      <div className="cinematic-overlay position-absolute top-0 start-0 w-100 h-100 text-center d-flex align-items-center justify-content-center" style={{ pointerEvents: 'none' }}>
        <h2 className="text-light">{title}</h2>
      </div>
      <div className="cinematic-content">{children}</div>
    </div>
  );
}

import React from "react";

function ComingSoon({ title }) {
  return (
    <div className="text-center p-5">
      <h2>🚧 {title || "Page Not Ready Yet"}</h2>
      <p>This feature is part of the evolving MythOS UI and will be activated soon.</p>
    </div>
  );
}

export default ComingSoon;

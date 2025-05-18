// components/common/TagBadge.jsx

import React from "react";

export default function TagBadge({ tag }) {
    return (
      <span
        className="badge rounded-pill me-1 mb-1"
        style={{
          backgroundColor: tag.color || "#17a2b8",
          color: "#fff",
          fontSize: "0.75rem",
        }}
      >
        #{tag.name}
      </span>
    );
  }

import React from "react";

export default function IngestSessionLogConsole({ log }) {
  if (!log || log.length === 0) return null;
  return (
    <div
      className="mt-3 p-2 bg-dark text-light"
      style={{ fontFamily: "monospace", maxHeight: "200px", overflowY: "auto" }}
    >
      {log.map((line, idx) => (
        <div key={idx}>{line}</div>
      ))}
    </div>
  );
}

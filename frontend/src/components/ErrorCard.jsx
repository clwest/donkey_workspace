import React from "react";

export default function ErrorCard({ message }) {
  if (!message) return null;
  return (
    <div className="container py-4">
      <div className="alert alert-danger" role="alert">
        {message}
      </div>
    </div>
  );
}

import React, { useEffect, useState } from "react";
import { Card } from "react-bootstrap";

export default function MetaphorMapViewer({ memoryId }) {
  const [metaphors, setMetaphors] = useState([]);

  useEffect(() => {
    async function fetchMap() {
      try {
        const res = await fetch(`/api/memory/${memoryId}/metaphors/`);
        if (res.ok) {
          const data = await res.json();
          setMetaphors(data.metaphor_tags || []);
        }
      } catch (err) {
        console.error("Failed to load metaphor map", err);
      }
    }
    if (memoryId) fetchMap();
  }, [memoryId]);

  return (
    <Card className="my-3">
      <Card.Header>Metaphor Map</Card.Header>
      <Card.Body>
        {metaphors.length === 0 ? (
          <div className="text-muted">No metaphors found.</div>
        ) : (
          <ul>
            {metaphors.map((m) => (
              <li key={m}>{m}</li>
            ))}
          </ul>
        )}
      </Card.Body>
    </Card>
  );
}

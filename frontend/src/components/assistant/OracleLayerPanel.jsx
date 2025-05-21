import React, { useEffect, useState } from "react";
import { Card, Button } from "react-bootstrap";

export default function OracleLayerPanel({ assistantSlug }) {
  const [layers, setLayers] = useState([]);

  useEffect(() => {
    async function loadLayers() {
      try {
        const res = await fetch(`/api/assistants/${assistantSlug}/oracle-layers/`);
        if (res.ok) {
          const data = await res.json();
          setLayers(data.results || []);
        }
      } catch (err) {
        console.error("Failed to load oracle layers", err);
      }
    }
    if (assistantSlug) loadLayers();
  }, [assistantSlug]);

  const generateLayer = async () => {
    try {
      await fetch(`/api/assistants/${assistantSlug}/oracle-layers/`, {
        method: "POST",
      });
      await new Promise((r) => setTimeout(r, 300));
      const res = await fetch(`/api/assistants/${assistantSlug}/oracle-layers/`);
      if (res.ok) {
        const data = await res.json();
        setLayers(data.results || []);
      }
    } catch (err) {
      console.error("Failed to generate oracle layer", err);
    }
  };

  return (
    <Card className="my-3">
      <Card.Header>
        Oracle Layers
        <Button
          variant="outline-secondary"
          size="sm"
          className="float-end"
          onClick={generateLayer}
        >
          Generate
        </Button>
      </Card.Header>
      <Card.Body>
        {layers.length === 0 ? (
          <div className="text-muted">No oracle insights.</div>
        ) : (
          <ul>
            {layers.map((l) => (
              <li key={l.id}>{l.summary_insight}</li>
            ))}
          </ul>
        )}
      </Card.Body>
    </Card>
  );
}

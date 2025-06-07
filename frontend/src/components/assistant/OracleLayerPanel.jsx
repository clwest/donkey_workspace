import React, { useEffect, useState } from "react";
import { Card, Button } from "react-bootstrap";
import apiFetch from "@/utils/apiClient";

export default function OracleLayerPanel({ assistantSlug }) {
  const [layers, setLayers] = useState([]);

  useEffect(() => {
    async function loadLayers() {
      try {
        const data = await apiFetch(`/assistants/${assistantSlug}/oracle-layers/`);
        setLayers(data.results || []);
      } catch (err) {
        console.error("Failed to load oracle layers", err);
      }
    }
    if (assistantSlug) loadLayers();
  }, [assistantSlug]);

  const generateLayer = async () => {
    try {
      await apiFetch(`/assistants/${assistantSlug}/oracle-layers/`, {
        method: "POST",
      });
      await new Promise((r) => setTimeout(r, 300));
      const data = await apiFetch(`/assistants/${assistantSlug}/oracle-layers/`);
      setLayers(data.results || []);
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

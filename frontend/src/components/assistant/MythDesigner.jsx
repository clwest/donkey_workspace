import React, { useEffect, useState } from "react";
import { Card, Button, Form } from "react-bootstrap";
import apiFetch from "@/utils/apiClient";

export default function MythDesigner() {
  const [entries, setEntries] = useState([]);
  const [selected, setSelected] = useState("");
  const [epithets, setEpithets] = useState("");
  const [traits, setTraits] = useState("");
  const [tone, setTone] = useState("mystic");
  const [result, setResult] = useState(null);

  useEffect(() => {
    async function loadLore() {
      try {
        const data = await apiFetch(`/lore/`);
        setEntries(data.results || []);
      } catch (err) {
        console.error("Failed to load lore entries", err);
      }
    }
    loadLore();
  }, []);

  const createAssistant = async () => {
    try {
      const res = await apiFetch(`/assistants/design-from-myth/`, {
        method: "POST",
        body: {
          lore_id: selected,
          epithets: epithets.split(/\s*,\s*/),
          traits: traits.split(/\s*,\s*/),
          tone,
        },
      });
      if (res) {
        const data = res;
        setResult(data);
      }
    } catch (err) {
      console.error("Failed to design assistant", err);
    }
  };

  return (
    <Card className="my-3 p-3">
      <h5>Myth Designer</h5>
      <Form.Select
        className="mb-2"
        value={selected}
        onChange={(e) => setSelected(e.target.value)}
      >
        <option value="">Select Lore Entry</option>
        {entries.map((e) => (
          <option key={e.id} value={e.id}>
            {e.title}
          </option>
        ))}
      </Form.Select>
      <Form.Control
        className="mb-2"
        placeholder="Epithets comma separated"
        value={epithets}
        onChange={(e) => setEpithets(e.target.value)}
      />
      <Form.Control
        className="mb-2"
        placeholder="Traits comma separated"
        value={traits}
        onChange={(e) => setTraits(e.target.value)}
      />
      <Form.Control
        className="mb-2"
        placeholder="Tone"
        value={tone}
        onChange={(e) => setTone(e.target.value)}
      />
      <Button onClick={createAssistant} disabled={!selected}>
        Spawn Assistant
      </Button>
      {result && (
        <div className="mt-3 alert alert-success">
          Spawned {result.name} ({result.slug})
        </div>
      )}
    </Card>
  );
}


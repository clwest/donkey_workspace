import { useState } from "react";

export default function WorkflowDesigner({ onSave }) {
  const [name, setName] = useState("");
  const [steps, setSteps] = useState("[]");

  const handleSave = () => {
    if (onSave) onSave({ name, steps: JSON.parse(steps) });
  };

  return (
    <div className="p-2 border rounded">
      <h5>Workflow Designer</h5>
      <input
        className="form-control mb-2"
        placeholder="Name"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />
      <textarea
        className="form-control mb-2"
        rows="4"
        placeholder='Steps JSON e.g. [{"assistant_id":1}]'
        value={steps}
        onChange={(e) => setSteps(e.target.value)}
      />
      <button className="btn btn-primary" onClick={handleSave}>
        Save
      </button>
    </div>
  );
}

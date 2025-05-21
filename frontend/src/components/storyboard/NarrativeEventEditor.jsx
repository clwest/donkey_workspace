import { useState } from "react";

export default function NarrativeEventEditor({ onSave }) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [scene, setScene] = useState("");
  const [location, setLocation] = useState("");

  const handleSubmit = () => {
    if (onSave) {
      onSave({ title, description, scene, location_context: location });
      setTitle("");
      setDescription("");
      setScene("");
      setLocation("");
    }
  };

  return (
    <div className="card mb-3">
      <div className="card-body">
        <input
          type="text"
          className="form-control mb-2"
          placeholder="Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <textarea
          className="form-control mb-2"
          rows="3"
          placeholder="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        <input
          type="text"
          className="form-control mb-2"
          placeholder="Scene tags (e.g. castle)"
          value={scene}
          onChange={(e) => setScene(e.target.value)}
        />
        <textarea
          className="form-control mb-2"
          rows="2"
          placeholder="Location description"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
        />
        <button className="btn btn-primary" onClick={handleSubmit}>
          Save Event
        </button>
      </div>
    </div>
  );
}

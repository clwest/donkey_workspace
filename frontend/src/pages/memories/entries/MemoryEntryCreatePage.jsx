import { useState } from "react";
import MemoryRecordingButton from "../../../components/memory/MemoryRecordingButton"; // update path if needed

export default function MemoryEntryCreatePage() {
  const [event, setEvent] = useState("");
  const [memoryId, setMemoryId] = useState(null);

  async function handleSaveMemory() {
    const res = await fetch("http://localhost:8000/api/memory/save/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ event }),
    });
    const data = await res.json();
    setMemoryId(data.memory_id);
    alert("Memory saved! Now you can record audio.");
  }

  async function handleSaveAudio(blob) {
    if (!memoryId) {
      alert("Please save the memory first!");
      return;
    }

    const formData = new FormData();
    formData.append("voice_clip", blob);
    formData.append("memory_id", memoryId);

    try {
      const res = await fetch("http://localhost:8000/api/memory/upload-voice/", {
        method: "POST",
        body: formData,
      });
      if (res.ok) {
        alert("Audio uploaded successfully!");
      } else {
        alert("Audio upload failed.");
      }
    } catch (err) {
      console.error("Error uploading audio:", err);
    }
  }

  return (
    <div className="container my-5">
      <h1 className="mb-4">🧠 Create Memory Entry</h1>

      <textarea
        className="form-control mb-3"
        rows="5"
        placeholder="Write your memory event here..."
        value={event}
        onChange={(e) => setEvent(e.target.value)}
      />

      <button className="btn btn-primary mb-4" onClick={handleSaveMemory}>
        💾 Save Memory
      </button>

      {memoryId && (
        <>
          <p className="text-muted">Memory saved! Now you can record audio:</p>
          <MemoryRecordingButton onSave={handleSaveAudio} />
        </>
      )}
    </div>
  );
}
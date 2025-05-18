import { useState, useRef } from "react";

export default function MemoryRecordingButton({ onSave }) {
  const [recording, setRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [audioBlob, setAudioBlob] = useState(null);

  const chunks = useRef([]);

  async function startRecording() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const recorder = new MediaRecorder(stream);

    recorder.ondataavailable = (e) => {
      chunks.current.push(e.data);
    };

    recorder.onstop = () => {
      const blob = new Blob(chunks.current, { type: "audio/webm" });
      setAudioBlob(blob);
      chunks.current = [];

      if (onSave) {
        onSave(blob);
      }
    };

    recorder.start();
    setMediaRecorder(recorder);
    setRecording(true);
  }

  async function uploadVoiceClip(blob, memoryId) {
    const formData = new FormData();
    formData.append("voice_clip", blob);
    formData.append("memory_id", memoryId);
  
    const res = await fetch("http://localhost:8000/api/memory/upload-voice/", {
      method: "POST",
      body: formData,
    });
  
    if (res.ok) {
      console.log("✅ Voice clip uploaded!");
    } else {
      console.error("❌ Upload failed.");
    }
  }

  function stopRecording() {
    if (mediaRecorder) {
      mediaRecorder.stop();
      setRecording(false);
    }
  }

  return (
    <div className="my-4 d-flex gap-2">
      {recording ? (
        <button onClick={stopRecording} className="btn btn-danger">
          ⏹️ Stop Recording
        </button>
      ) : (
        <button onClick={startRecording} className="btn btn-primary">
          🎙️ Start Recording
        </button>
      )}
      {audioBlob && (
        <audio controls src={URL.createObjectURL(audioBlob)} className="mt-2" />
      )}
    </div>
  );
}
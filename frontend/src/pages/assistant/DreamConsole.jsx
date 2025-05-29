import { useState } from "react";
import { useParams } from "react-router-dom";
import { initiateDream } from "../../api/assistants";

export default function DreamConsole() {
  const { id } = useParams();
  const [text, setText] = useState("");
  const [status, setStatus] = useState("");

  const enterDream = async () => {
    try {
      await initiateDream(id, { dream: text });
      setStatus("Dream initiated");
    } catch (err) {
      console.error(err);
      setStatus("Failed");
    }
  };

  return (
    <div className="container my-5">
      <h1>Dream Console</h1>
      <textarea
        className="form-control mb-2"
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <button className="btn btn-primary" onClick={enterDream}>
        Enter Dream
      </button>
      {status && <div className="mt-3">{status}</div>}
    </div>
  );
}

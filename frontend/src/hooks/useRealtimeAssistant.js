import { useState, useRef, useEffect } from "react";

export default function useRealtimeAssistant(model = "gpt-4o") {
  const [output, setOutput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const wsRef = useRef(null);

  const start = (messages) => {
    const token = localStorage.getItem("access");
    const ws = new WebSocket("wss://api.openai.com/v1/realtime");
    wsRef.current = ws;
    setOutput("");
    setStreaming(true);
    ws.onopen = () => {
      ws.send(
        JSON.stringify({ type: "start", data: { model, messages } })
      );
    };
    ws.onmessage = (evt) => {
      const data = JSON.parse(evt.data);
      if (data.type === "token") {
        setOutput((prev) => prev + data.data);
      }
    };
    ws.onclose = () => {
      setStreaming(false);
    };
  };

  const interrupt = () => {
    if (wsRef.current) {
      wsRef.current.send(JSON.stringify({ type: "interrupt" }));
      wsRef.current.close();
    }
  };

  const edit = (messages) => {
    if (wsRef.current) {
      wsRef.current.send(JSON.stringify({ type: "edit", data: { messages } }));
    }
  };

  useEffect(() => {
    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  return { output, streaming, start, interrupt, edit };
}

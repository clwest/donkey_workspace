export default function AdaptiveLoopManager({ assistantId, onTrigger }) {
  const handleTrigger = () => {
    fetch(
      `http://localhost:8000/api/learning-loops/trigger/${assistantId}/`,
      { method: "POST" }
    )
      .then((res) => res.json())
      .then((data) => onTrigger && onTrigger(data))
      .catch((e) => console.error("trigger", e));
  };

  return (
    <div className="p-2 border rounded">
      <h5>Adaptive Loop</h5>
      <button className="btn btn-secondary" onClick={handleTrigger}>
        Trigger Now
      </button>
    </div>
  );
}

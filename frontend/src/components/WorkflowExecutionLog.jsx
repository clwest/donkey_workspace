export default function WorkflowExecutionLog({ log }) {
  if (!log) return null;
  return (
    <div className="p-2 border rounded mt-2">
      <h6>Execution Log</h6>
      <pre className="small bg-light p-2">{log}</pre>
    </div>
  );
}

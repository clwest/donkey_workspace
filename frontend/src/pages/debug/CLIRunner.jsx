import { useState, useEffect } from "react";
import apiFetch from "../../utils/apiClient";

export default function CLIRunner() {
  const [commands, setCommands] = useState([]);
  const [command, setCommand] = useState("run_rag_tests");
  const [flags, setFlags] = useState("");
  const [output, setOutput] = useState("");
  const [running, setRunning] = useState(false);

  useEffect(() => {
    apiFetch("/dev/cli/list/").then((res) => {
      const groups = res.results || {};
      const flat = [];
      Object.entries(groups).forEach(([app, cmds]) => {
        cmds.forEach((c) => flat.push({ ...c, app }));
      });
      setCommands(flat);
      if (flat.length) setCommand(flat[0].name);
    });
  }, []);

  const run = async () => {
    setRunning(true);
    setOutput("");
    try {
      const res = await apiFetch("/dev/cli/run/", {
        method: "POST",
        body: { command, flags },
      });
      const id = res.log_id;
      let done = false;
      while (!done) {
        const log = await apiFetch(`/dev/command-logs/${id}/`);
        setOutput(log.output);
        done = log.status !== "running";
        if (!done) await new Promise((r) => setTimeout(r, 1000));
      }
    } catch {
      setOutput("Error running command");
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="container my-4">
      <h3>CLI Runner</h3>
      <div className="d-flex mb-2 gap-2">
        <select
          className="form-select w-auto"
          value={command}
          onChange={(e) => setCommand(e.target.value)}
        >
          {commands.map((c) => (
            <option key={c.name} value={c.name}>
              {c.name}
            </option>
          ))}
        </select>
        <input
          type="text"
          className="form-control w-auto"
          placeholder="--flags"
          value={flags}
          onChange={(e) => setFlags(e.target.value)}
        />
        <button className="btn btn-primary" onClick={run} disabled={running}>
          {running ? "Running..." : "Run"}
        </button>
      </div>
      <pre className="bg-dark text-light p-3" style={{ minHeight: "200px" }}>
        {output}
      </pre>
    </div>
  );
}

import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";

export default function CLIRunnerPage() {
  const [commands, setCommands] = useState([]);
  const [command, setCommand] = useState("");
  const [flags, setFlags] = useState("");
  const [assistant, setAssistant] = useState("");
  const [output, setOutput] = useState("");
  const [running, setRunning] = useState(false);
  const [filter, setFilter] = useState("");

  useEffect(() => {
    apiFetch("/dev/cli/commands/")
      .then((res) => {
        setCommands(res.results || []);
        if (res.results?.length) setCommand(res.results[0].name);
      })
      .catch(() => setCommands([]));
  }, []);

  const run = async () => {
    setRunning(true);
    setOutput("");
    try {
      const res = await apiFetch("/dev/cli/run/", {
        method: "POST",
        body: { command, flags, assistant },
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

  const filtered = commands.filter((c) =>
    filter ? c.app.startsWith(filter) : true
  );

  const apps = Array.from(new Set(commands.map((c) => c.app.split(".")[0])));

  return (
    <div className="container my-4">
      <h3 className="mb-3">CLI Runner</h3>
      <div className="d-flex mb-2 gap-2 align-items-center">
        <select
          className="form-select w-auto"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        >
          <option value="">All Apps</option>
          {apps.map((a) => (
            <option key={a} value={a}>
              {a}
            </option>
          ))}
        </select>
        <select
          className="form-select w-auto"
          value={command}
          onChange={(e) => setCommand(e.target.value)}
        >
          {filtered.map((c) => (
            <option key={c.name} value={c.name}>
              {c.name}
            </option>
          ))}
        </select>
        <input
          type="text"
          className="form-control w-auto"
          placeholder="Assistant (optional)"
          value={assistant}
          onChange={(e) => setAssistant(e.target.value)}
        />
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

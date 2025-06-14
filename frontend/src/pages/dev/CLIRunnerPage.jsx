import { useEffect, useState } from "react";
import apiFetch from "../../utils/apiClient";
import { toast } from "react-toastify";

export default function CLIRunnerPage() {
  const [commands, setCommands] = useState([]);
  const [command, setCommand] = useState("");
  const [flags, setFlags] = useState("");
  const [assistant, setAssistant] = useState("");
  const [assistants, setAssistants] = useState([]);
  const [isAdmin, setIsAdmin] = useState(false);
  const [output, setOutput] = useState("");
  const [running, setRunning] = useState(false);
  const [filter, setFilter] = useState("");

  useEffect(() => {
    async function loadData() {
      try {
        const cmdRes = await apiFetch("/dev/cli/list/");
        const groups = cmdRes.results || {};
        const flat = [];
        Object.entries(groups).forEach(([app, cmds]) => {
          cmds.forEach((c) => flat.push({ ...c, app }));
        });
        setCommands(flat);
        if (flat.length) setCommand(flat[0].name);
      } catch {
        setCommands([]);
      }
      try {
        const aRes = await apiFetch("/assistants/?limit=100");
        setAssistants(aRes.results || aRes);
      } catch {
        setAssistants([]);
      }
      try {
        const user = await apiFetch("/auth/user/", { allowUnauthenticated: true });
        setIsAdmin(user.is_staff || user.is_superuser);
      } catch {
        setIsAdmin(false);
      }
    }
    loadData();
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
    } catch (err) {
      if (err.status === 403) {
        toast.error("Permission denied");
      }
      setOutput("Error running command");
    } finally {
      setRunning(false);
    }
  };

  const filtered = commands.filter((c) =>
    filter ? c.app.startsWith(filter) : true
  );

  const apps = Array.from(new Set(commands.map((c) => c.app)));

  // if (!isAdmin) {
  //   return <div className="container my-4">Admin access required</div>;
  // }

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
        <select
          className="form-select w-auto"
          value={assistant}
          onChange={(e) => setAssistant(e.target.value)}
        >
          <option value="">No Assistant</option>
          {assistants.map((a) => (
            <option key={a.slug} value={a.slug}>
              {a.name}
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

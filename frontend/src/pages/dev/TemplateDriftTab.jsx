import React, { useEffect, useState } from "react";
import { toast } from "react-toastify";
import apiFetch from "../../utils/apiClient";

export default function TemplateDriftTab() {
  const [templates, setTemplates] = useState([]);
  const [diffs, setDiffs] = useState({});

  const loadTemplates = async () => {
    try {
      const res = await apiFetch("/dev/templates/health/");
      setTemplates(res.templates || []);
    } catch (err) {
      console.error("Failed to load templates", err);
    }
  };

  const reloadFromDisk = async () => {
    try {
      await apiFetch("/dev/templates/reload/", { method: "POST" });
      toast.success("Templates reloaded");
      loadTemplates();
    } catch (err) {
      console.error("Reload failed", err);
      toast.error("Reload failed");
    }
  };

  const viewDiff = async (path) => {
    try {
      const encoded = encodeURIComponent(path);
      const res = await apiFetch(`/dev/templates/${encoded}/diff/`);
      setDiffs((d) => ({ ...d, [path]: res.diff }));
    } catch (err) {
      console.error("Diff fetch failed", err);
    }
  };

  useEffect(() => {
    loadTemplates();
  }, []);

  return (
    <div className="p-3" style={{ overflowY: "auto" }}>
      <div className="mb-2">
        <button className="btn btn-outline-secondary me-2" onClick={loadTemplates}>
          Refresh
        </button>
        <button className="btn btn-outline-primary" onClick={reloadFromDisk}>
          Reload from disk
        </button>
      </div>
      <table className="table table-sm table-bordered">
        <thead className="table-light">
          <tr>
            <th>Template</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {templates.map((t) => (
            <React.Fragment key={t.template_path}>
              <tr>
                <td>
                  <code>{t.template_path}</code>
                  {t.hash_diff && (
                    <span className="badge bg-warning text-dark ms-2">⚠️ Drift</span>
                  )}
                </td>
                <td>
                  {t.git_tracked && (
                    <button
                      className="btn btn-sm btn-outline-primary"
                      onClick={() => viewDiff(t.template_path)}
                    >
                      View diff
                    </button>
                  )}
                </td>
              </tr>
              {diffs[t.template_path] && (
                <tr>
                  <td colSpan="2">
                    <pre style={{ whiteSpace: "pre-wrap" }}>{diffs[t.template_path] || "No diff"}</pre>
                  </td>
                </tr>
              )}
            </React.Fragment>
          ))}
        </tbody>
      </table>
    </div>
  );
}

import { useEffect, useState } from "react";
import { fetchBootProfile, runSelfTest } from "../../api/assistants";
import { toast } from "react-toastify";

export default function AssistantBootPanel({ assistant, onTestComplete }) {
  const slug = assistant?.slug;
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);

  useEffect(() => {
    if (!slug) return;
    setLoading(true);
    fetchBootProfile(slug)
      .then(setProfile)
      .catch(() => {
        toast.error("Failed to load boot profile");
        setProfile(null);
      })
      .finally(() => setLoading(false));
  }, [slug]);

  const handleTest = async () => {
    if (!slug) return;
    setTesting(true);
    try {
      const res = await runSelfTest(slug);
      setTestResult(res);
      onTestComplete && onTestComplete({ ...res, timestamp: new Date().toISOString() });
      toast[res.passed ? "success" : "error"](
        res.passed ? "Self-test passed" : "Self-test failed",
      );
    } catch (err) {
      toast.error("Self-test failed");
    } finally {
      setTesting(false);
    }
  };

  if (loading) return <div>Loading boot profile...</div>;
  if (!profile)
    return <div className="text-muted">Boot profile unavailable.</div>;

  return (
    <div>
      <h6 className="mt-2">🧬 Boot Profile Overview</h6>
      <ul className="list-unstyled small mb-3">
        <li>Prompt: “{profile.system_prompt.title}”</li>
        <li>Tone: {assistant.tone || "default"}</li>
        <li>Model: {assistant.preferred_model || assistant.preferred_llm}</li>
        <li>Context ID: {assistant.memory_context_id}</li>
        <li>
          Glossary Anchors: {profile.glossary_anchors.active}/{profile.glossary_anchors.total}
        </li>
        <li>Linked Projects: {profile.projects_total}</li>
      </ul>
      <h6>🧪 Self-Test</h6>
      {testResult && (
        <p className="small">
          {testResult.passed ? "✅ Passed" : "❌ Failed"}
          {testResult.issues && testResult.issues.length > 0 && (
            <> - {testResult.issues.join(", ")}</>
          )}
        </p>
      )}
      <button className="btn btn-sm btn-primary" onClick={handleTest} disabled={testing}>
        {testing ? "Running..." : "Run Self-Test"}
      </button>
    </div>
  );
}

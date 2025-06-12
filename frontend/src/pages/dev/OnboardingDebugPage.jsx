import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import apiFetch from "@/utils/apiClient";
import useUserInfo from "@/hooks/useUserInfo";

export default function OnboardingDebugPage() {
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState(null);
  const userInfo = useUserInfo();

  useEffect(() => {
    apiFetch("/debug/assistant_routing/", { allowUnauthenticated: true })
      .then((data) => setStatus(data))
      .finally(() => setLoading(false));
  }, []);

  const reset = async () => {
    await apiFetch("/debug/reset_onboarding/", { method: "POST" });
    window.location.reload();
  };

  if (loading) return <div className="container py-5">Loading...</div>;

  return (
    <div className="container my-5">
      <div className="d-flex justify-content-between mb-3">
        <h2>Onboarding Debug</h2>
        <Link to="/dev-dashboard" className="btn btn-outline-secondary">
          ← Back to Dev Dashboard
        </Link>
      </div>
      <table className="table table-bordered w-auto">
        <tbody>
          <tr>
            <th>User ID</th>
            <td>{userInfo?.id || "-"}</td>
          </tr>
          <tr>
            <th>Onboarding Complete</th>
            <td>{String(status?.onboarding_complete)}</td>
          </tr>
          <tr>
            <th>Primary Slug</th>
            <td>{status?.primary_slug || "-"}</td>
          </tr>
        </tbody>
      </table>
      <button className="btn btn-danger" onClick={reset}>
        Reset Onboarding
      </button>
    </div>
  );
}

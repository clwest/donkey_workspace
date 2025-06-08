import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import apiFetch from "../../../utils/apiClient";
import DemoComparisonCard from "../../../components/assistant/DemoComparisonCard";

export default function DemoComparisonPage() {
  const [assistants, setAssistants] = useState([]);

  const fetchSet = () => {
    apiFetch("/assistants/demo_comparison/")
      .then((data) => setAssistants(Array.isArray(data) ? data : []))
      .catch(() => setAssistants([]));
  };

  useEffect(() => {
    fetchSet();
  }, []);

  return (
    <div className="container py-5">
      <h1 className="mb-4">🆚 Compare Demo Assistants</h1>
      <div className="row">
        {assistants.map((a) => (
          <div key={a.demo_slug} className="col-md-4 mb-3">
            <DemoComparisonCard assistant={a} />
          </div>
        ))}
      </div>
      <div className="mt-4">
        <button className="btn btn-outline-secondary me-2" onClick={fetchSet}>
          Try another comparison
        </button>
        <Link className="btn btn-primary" to="/assistants-demos">
          Return to Demo Overview
        </Link>
      </div>
    </div>
  );
}

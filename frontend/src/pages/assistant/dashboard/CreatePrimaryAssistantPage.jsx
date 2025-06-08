import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createPrimaryAssistant } from "../../../api/assistants";
import ComingSoon from "../../../components/common/ComingSoon";
import { SHOW_INACTIVE_ROUTES } from "../../../config/ui";
import { toast } from "react-toastify";


export default function CreatePrimaryAssistantPage() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleCreate = async () => {
    setLoading(true);
    try {
      const res = await createPrimaryAssistant();
      toast.success("Primary assistant created");
      navigate(`/assistants/${res.slug}/dashboard`);
    } catch (err) {
      console.error("Failed to create primary assistant", err);
      if (err.message.includes("404")) {
        toast.error("Primary creation endpoint not found (404)");
      } else {
        toast.error("Failed to create primary assistant");
      }
    } finally {
      setLoading(false);
    }
  };

  if (SHOW_INACTIVE_ROUTES) {
    return <ComingSoon title="Create Primary Assistant" />;
  }

  return (
    <div className="container my-5 text-center">
      <h3 className="mb-3">Designate Primary Assistant</h3>
      <button className="btn btn-primary" onClick={handleCreate} disabled={loading}>
        {loading ? "Creating..." : "Create Primary Assistant"}
      </button>
    </div>
  );
}

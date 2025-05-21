import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import apiFetch from "../../utils/apiClient";

export default function LogoutPage() {
  const navigate = useNavigate();
  useEffect(() => {
    async function doLogout() {
      try {
        await apiFetch("/dj-rest-auth/logout/", { method: "POST" });
        toast.success("✅ Logged out");
      } catch {
        toast.error("❌ Logout failed");
      } finally {
        navigate("/");
      }
    }
    doLogout();
  }, [navigate]);

  return (
    <div className="container my-5">
      <h2>Logging out...</h2>
    </div>
  );
}

import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import { logoutUser } from "@/api/auth";

export default function LogoutPage() {
  const navigate = useNavigate();
  useEffect(() => {
    async function doLogout() {
      try {
        logoutUser();
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

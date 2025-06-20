import { useState } from "react";
import { useNavigate, Link, useLocation } from "react-router-dom";
import useAuthGuard from "../../hooks/useAuthGuard";

export function getNextPath(search) {
  return new URLSearchParams(search).get("next");
}
import { toast } from "react-toastify";
import apiFetch from "../../utils/apiClient";
import { loginUser } from "@/api/auth";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();
  const location = useLocation();
  const { authChecked } = useAuthGuard({ allowUnauthenticated: true });
  if (!authChecked) {
    return <div className="container my-5">Loading...</div>;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await loginUser(username, password);
      toast.success("✅ Logged in!");
      const nextPath = getNextPath(location.search);
      if (nextPath) {
        navigate(nextPath);
        return;
      }
      const info = await apiFetch("/auth/user/", { allowUnauthenticated: true });
      if (info.onboarding_complete) {
        navigate("/home");
      } else {
        navigate("/onboarding/world");
      }
    } catch (err) {
      toast.error("❌ Login failed");
    }
  };

  return (
    <div className="container my-5 text-light bg-dark p-4 rounded">
      <h2 className="mb-1">Login</h2>
      <p className="text-secondary mb-4">You don’t prompt MythOS. You grow it.</p>
      <form onSubmit={handleSubmit} className="mt-2">
        <div className="mb-3">
          <label className="form-label">Username or Email</label>
          <input
            type="text"
            className="form-control"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
            required
          />
        </div>
        <div className="mb-3">
          <label className="form-label">Password</label>
          <input
            type="password"
            className="form-control"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            required
          />
        </div>
        <button type="submit" className="btn btn-primary">
          Login
        </button>
        <p className="mt-3">
          Don’t have an account?{' '}
          <Link to="/register" className="text-info">
            Register
          </Link>
        </p>
      </form>
    </div>
  );
}

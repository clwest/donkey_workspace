import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import apiFetch from "../../utils/apiClient";
import { loginUser } from "@/api/auth";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const data = await loginUser(username, password);
      toast.success("✅ Logged in!");
      let user;
      try {
        user = await apiFetch("/user/");
      } catch (err) {
        console.error("user fetch failed", err);
      }
      if (user?.assistant_count === 0) {
        navigate("/assistants/launch");
      } else if (user?.onboarding_complete) {
        try {
          const primary = await apiFetch("/assistants/primary/");
          navigate(`/assistants/${primary.slug}/dashboard`);
        } catch {
          navigate("/assistants/primary/create");
        }
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
      </form>
    </div>
  );
}

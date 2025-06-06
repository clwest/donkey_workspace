import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import apiFetch from "../../utils/apiClient";
import { registerUser } from "@/api/auth";

export default function RegisterPage() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password1, setPassword1] = useState("");
  const [password2, setPassword2] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (password1 !== password2) {
      toast.error("Passwords do not match");
      return;
    }
    try {
      await registerUser({
        username,
        email,
        password1,
        password2,
      });

      toast.success("✅ Registered!");
      navigate("/onboarding/world");
    } catch (err) {
      toast.error("❌ Registration failed");
    }
  };

  return (
    <div className="container my-5 text-light bg-dark p-4 rounded">
      <h2 className="mb-1">Register</h2>
      <p className="text-secondary mb-4">You don’t prompt MythOS. You grow it.</p>
      <form onSubmit={handleSubmit} className="mt-2">
        <div className="mb-3">
          <label className="form-label">Username</label>
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
          <label className="form-label">Email</label>
          <input
            type="email"
            className="form-control"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="email"
            required
          />
        </div>
        <div className="mb-3">
          <label className="form-label">Password</label>
          <input
            type="password"
            className="form-control"
            value={password1}
            onChange={(e) => setPassword1(e.target.value)}
            autoComplete="new-password"
            required
          />
        </div>
        <div className="mb-3">
          <label className="form-label">Confirm Password</label>
          <input
            type="password"
            className="form-control"
            value={password2}
            onChange={(e) => setPassword2(e.target.value)}
            autoComplete="new-password"
            required
          />
        </div>
        <button type="submit" className="btn btn-success">
          Register
        </button>
      </form>
    </div>
  );
}

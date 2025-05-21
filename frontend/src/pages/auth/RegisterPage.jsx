import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import apiFetch from "../../utils/apiClient";

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
      await apiFetch("/dj-rest-auth/registration/", {
        method: "POST",
        body: { username, email, password1, password2 },
      });
      toast.success("✅ Registered! Please log in.");
      navigate("/login");
    } catch (err) {
      toast.error("❌ Registration failed");
    }
  };

  return (
    <div className="container my-5">
      <h2>Register</h2>
      <form onSubmit={handleSubmit} className="mt-4">
        <div className="mb-3">
          <label className="form-label">Username</label>
          <input
            type="text"
            className="form-control"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
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

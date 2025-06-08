import { useEffect, useState } from "react";
import { toast } from "react-toastify";
import apiFetch from "../../utils/apiClient";

export default function ProfilePage() {
  const [profile, setProfile] = useState({});

  useEffect(() => {
    async function loadProfile() {
      try {
        const data = await apiFetch("/auth/user/", { allowUnauthenticated: true });
        setProfile(data);
      } catch {
        toast.error("❌ Failed to load profile");
      }
    }
    loadProfile();
  }, []);

  const handleChange = (field, value) => {
    setProfile((p) => ({ ...p, [field]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await apiFetch("/auth/user/", {
        method: "PUT",
        body: profile,
        allowUnauthenticated: true,
      });
      toast.success("✅ Profile updated");
    } catch {
      toast.error("❌ Update failed");
    }
  };

  return (
    <div className="container my-5">
      <h2>User Profile</h2>
      <form onSubmit={handleSubmit} className="mt-4">
        <div className="mb-3">
          <label className="form-label">Username</label>
          <input
            type="text"
            className="form-control"
            value={profile.username || ""}
            onChange={(e) => handleChange("username", e.target.value)}
          />
        </div>
        <div className="mb-3">
          <label className="form-label">First Name</label>
          <input
            type="text"
            className="form-control"
            value={profile.first_name || ""}
            onChange={(e) => handleChange("first_name", e.target.value)}
          />
        </div>
        <div className="mb-3">
          <label className="form-label">Last Name</label>
          <input
            type="text"
            className="form-control"
            value={profile.last_name || ""}
            onChange={(e) => handleChange("last_name", e.target.value)}
          />
        </div>
        <button type="submit" className="btn btn-primary">
          Save Profile
        </button>
      </form>
    </div>
  );
}

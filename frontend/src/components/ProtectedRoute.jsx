import { Outlet } from "react-router-dom";
import useAuthGuard from "../hooks/useAuthGuard";

export default function ProtectedRoute({ children }) {
  useAuthGuard();
  return children ? children : <Outlet />;
}

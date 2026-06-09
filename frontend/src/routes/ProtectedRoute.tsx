import { Navigate, Outlet, useLocation } from "react-router-dom";
import { Spin } from "antd";
import { useAuthStore } from "../stores/authStore";

interface ProtectedRouteProps {
  adminOnly?: boolean;
}

export function ProtectedRoute({ adminOnly = false }: ProtectedRouteProps) {
  const location = useLocation();
  const { token, user, bootstrapped } = useAuthStore();

  if (!bootstrapped) {
    return (
      <div className="app-loading">
        <Spin size="large" />
      </div>
    );
  }

  if (!token || !user) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  if (adminOnly && user.role.name === "student") {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
}
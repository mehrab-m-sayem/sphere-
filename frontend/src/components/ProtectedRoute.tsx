import React from 'react';
import { Navigate } from 'react-router-dom';
import { isAuthenticated, getUserRole } from '../utils/auth';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: string;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, requiredRole }) => {
  if (!isAuthenticated()) {
    return <Navigate to="/" replace />;
  }

  if (requiredRole) {
    const userRole = getUserRole();
    if (userRole !== requiredRole) {
      return <Navigate to="/profile" replace />;
    }
  }

  return <>{children}</>;
};

export default ProtectedRoute;
import type { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStatusContext } from '@/contexts/AuthStatusContextProvider';

/**
 * Gates a route behind an active session. While the initial auth check is in
 * flight we render a placeholder rather than redirecting — otherwise a hard
 * refresh would bounce a logged-in user off the page before the cookie is checked.
 *
 * This is UX only. The API routes enforce access with @login_required.
 */
function ProtectedRoute({ children }: { children: ReactNode }) {
  const { isAuthenticated, isLoading } = useAuthStatusContext();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="h-screen bg-primary flex justify-center items-center">
        <p className="font-pixel text-2xl text-white">Summoning...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    // `from` is forwarded by LandingPage so the user lands back where they
    // were headed once they pick a login method.
    return <Navigate to="/" state={{ from: location.pathname }} replace />;
  }

  return <>{children}</>;
}

export default ProtectedRoute;

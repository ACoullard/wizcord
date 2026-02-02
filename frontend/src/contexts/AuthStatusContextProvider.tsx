import React, { createContext, useState, useContext, useEffect } from 'react';
import type { ReactNode } from 'react';
import type { UserData } from '@/features/main/types';


interface AuthStatusContextType {
  isAuthenticated: boolean;
  isAnonymous: boolean;
  userData: UserData | null;
  setStateLoggedin: (userData: UserData) => void;
  setStateLoggedout: () => void;
  setStateLoggedinAnonymous: (userData: UserData) => void;
}


const AuthStatusContext = createContext<AuthStatusContextType | undefined>(undefined);

export const AuthStatusContextProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isAnonymous, setIsAnonymous] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [userData, setUserData] = useState<UserData | null>(null);

  const setStateLoggedin = (userData: UserData) => {
    setIsAuthenticated(true);
    setIsAnonymous(false);
    setUserData(userData);
  };

  const setStateLoggedinAnonymous = (userData: UserData) => {
    setIsAuthenticated(true);
    setIsAnonymous(true);
    setUserData(userData);
  };

  const setStateLoggedout = () => {
    setIsAuthenticated(false);
    setIsAnonymous(false);
    setUserData(null);
  };

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const res = await fetch("api/login/current-user", {
          method: 'GET',
          credentials: 'include',
        })
        if (!res.ok) {
          throw new Error("Not authenticated");
        }
        const data = await res.json();
        setStateLoggedin(data as UserData);
      } catch {
        setStateLoggedout();
      } finally {
        setIsLoading(false);
      }
    }
    checkAuth();
  }, [])

  return (
    <AuthStatusContext.Provider
      value={{ 
        isAuthenticated, 
        isAnonymous, 
        userData, 
        setStateLoggedin, 
        setStateLoggedout, 
        setStateLoggedinAnonymous 
      }}
    >
      {children}
    </AuthStatusContext.Provider>
  );
};

export const useAuthStatusContext = () => {
  const context = useContext(AuthStatusContext);
  if (!context) {
    throw new Error('useAuthStatus must be used within an AuthStatusContextProvider');
  }
  return context;
};
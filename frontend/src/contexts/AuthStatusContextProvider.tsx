import React, { createContext, useState, useContext } from 'react';
import type { ReactNode } from 'react';

interface AuthStatusContextType {
  isAuthenticated: boolean;
  isAnonymous: boolean;
  username: string | null;
  userId: string | null;
  setStateLoggedin: (username: string, userId: string) => void;
  setStateLoggedout: () => void;
  setStateLoggedinAnonymous: () => void;
}


const AuthStatusContext = createContext<AuthStatusContextType | undefined>(undefined);

export const AuthStatusContextProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isAnonymous, setIsAnonymous] = useState(false);
  const [username, setUsername] = useState<string | null>(null);
  const [userId, setUserId] = useState<string | null>(null);

  const setStateLoggedin = (username: string, userId: string) => {
    setIsAuthenticated(true);
    setUsername(username);
    setUserId(userId);
  };

  const setStateLoggedinAnonymous = () => {
    setIsAuthenticated(true);
    setIsAnonymous(true);
    setUsername("guest");
    setUserId("guest");
  };

  const setStateLoggedout = () => {
    setIsAuthenticated(false);
    setUsername(null);
    setUserId(null);
  };

  return (
    <AuthStatusContext.Provider
      value={{ isAuthenticated, isAnonymous, username, userId, setStateLoggedin, setStateLoggedout, setStateLoggedinAnonymous }}
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
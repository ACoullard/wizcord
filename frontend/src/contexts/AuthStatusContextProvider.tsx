import React, { createContext, useState, useContext } from 'react';
import type { ReactNode } from 'react';
import type { UserData } from '../features/main/types';

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
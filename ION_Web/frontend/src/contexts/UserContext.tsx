import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { loginUser } from '../API/requests';

interface UserContextType {
  userId: string | null;
  setUserId: (userId: string | null) => void;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export const UserProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [userId, setUserId] = useState<string | null>(null);
  const defaultEmail = 'tttt@q.com';

  useEffect(() => {
    const initializeUser = async () => {
      try {
        // Try to login/create the default user
        const userIdFromAPI = await loginUser(defaultEmail);
        setUserId(userIdFromAPI);
        console.log(`Default user initialized: ${userIdFromAPI}`);
      } catch (error) {
        console.error('Failed to initialize default user:', error);
        // Fallback to using the email as userId if API call fails
        setUserId(defaultEmail);
      }
    };

    initializeUser();
  }, []);

  return (
    <UserContext.Provider value={{ userId, setUserId }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = (): UserContextType => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
}; 
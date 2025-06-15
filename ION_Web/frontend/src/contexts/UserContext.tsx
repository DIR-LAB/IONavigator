import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { loginUser, authenticateUser, registerUser } from '../API/requests';

interface UserContextType {
  userId: string | null;
  userEmail: string | null;
  isTestUser: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshUserData: () => Promise<void>;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export const UserProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [userId, setUserId] = useState<string | null>(null);
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const [isTestUser, setIsTestUser] = useState<boolean>(true);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const defaultEmail = 'tttt@q.com';

  const initializeTestUser = async () => {
    try {
      // Initialize test user
      const userIdFromAPI = await loginUser(defaultEmail);
      setUserId(userIdFromAPI);
      setUserEmail(defaultEmail);
      setIsTestUser(true);
      setIsAuthenticated(false);
      console.log(`Test user initialized: ${userIdFromAPI}`);
    } catch (error) {
      console.error('Failed to initialize test user:', error);
      // Fallback to using the email as userId if API call fails
      setUserId(defaultEmail);
      setUserEmail(defaultEmail);
      setIsTestUser(true);
      setIsAuthenticated(false);
    }
  };

  const login = async (email: string, password: string) => {
    try {
      const userIdFromAPI = await authenticateUser(email, password);
      setUserId(userIdFromAPI);
      setUserEmail(email);
      setIsTestUser(false);
      setIsAuthenticated(true);
      
      // Store authentication state in localStorage
      localStorage.setItem('auth_user_id', userIdFromAPI);
      localStorage.setItem('auth_user_email', email);
      
      console.log(`User logged in: ${email}`);
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const register = async (email: string, password: string) => {
    try {
      const userIdFromAPI = await registerUser(email, password);
      setUserId(userIdFromAPI);
      setUserEmail(email);
      setIsTestUser(false);
      setIsAuthenticated(true);
      
      // Store authentication state in localStorage
      localStorage.setItem('auth_user_id', userIdFromAPI);
      localStorage.setItem('auth_user_email', email);
      
      console.log(`User registered and logged in: ${email}`);
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  };

  const logout = () => {
    // Clear authentication state
    localStorage.removeItem('auth_user_id');
    localStorage.removeItem('auth_user_email');
    
    // Reset to test user
    initializeTestUser();
    console.log('User logged out, switched to test user');
  };

  const refreshUserData = async () => {
    // This can be used to refresh user traces after login
    console.log('Refreshing user data...');
  };

  useEffect(() => {
    const initializeUser = async () => {
      // Check if user was previously authenticated
      const storedUserId = localStorage.getItem('auth_user_id');
      const storedUserEmail = localStorage.getItem('auth_user_email');
      
      if (storedUserId && storedUserEmail) {
        // User was previously authenticated
        setUserId(storedUserId);
        setUserEmail(storedUserEmail);
        setIsTestUser(false);
        setIsAuthenticated(true);
        console.log(`Restored authenticated user: ${storedUserEmail}`);
      } else {
        // Initialize with test user
        await initializeTestUser();
      }
    };

    initializeUser();
  }, []);

  return (
    <UserContext.Provider value={{ 
      userId, 
      userEmail,
      isTestUser, 
      isAuthenticated,
      login, 
      register, 
      logout,
      refreshUserData
    }}>
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
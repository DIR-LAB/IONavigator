import React, { useState } from 'react';
import './App.css';
import EmailInput from './components/emailInput';
import HomePage from './pages/homePage';
import { UserProvider } from './contexts/UserContext';

function App() {
  const [userId, setUserId] = useState<string | null>(null);

  const handleEmailSubmit = (userId: string) => {
    setUserId(userId);
    console.log(userId);
  };

  return (
    <div className="App">
      <UserProvider>
        {!userId && (
          <div className="overlay">
            <EmailInput onEmailSubmit={handleEmailSubmit} />
          </div>
        )}
        <div className={userId ? '' : 'blur'}>
          <HomePage />
        </div>
      </UserProvider>
    </div>
  );
}

export default App;
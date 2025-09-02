import React from 'react';
import './App.css';
import HomePage from './pages/homePage';
import { UserProvider } from './contexts/UserContext';

function App() {
  return (
    <div className="App">
      <UserProvider>
        <HomePage />
      </UserProvider>
    </div>
  );
}

export default App;
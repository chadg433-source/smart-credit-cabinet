import { useState } from 'react';
import { RegistrationCard } from './components/registration';
import { Dashboard } from './components/Dashboard';

function App() {
  const [currentPage, setCurrentPage] = useState<'register' | 'dashboard'>('register');

  return (
    <>
      {currentPage === 'register' ? (
        <RegistrationCard onSuccess={() => setCurrentPage('dashboard')} />
      ) : (
        <Dashboard onLogout={() => setCurrentPage('register')} />
      )}
    </>
  );
}

export default App;
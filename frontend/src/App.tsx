// src/App.tsx
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom';

import { RegistrationCard } from './pages/registration';
import { Dashboard } from './pages/Dashboard';
import { ClientHome } from './pages/ClientHome';
import { ClientApplicationsList } from './pages/ClientApplicationsList';
import { LoanApplication } from './pages/LoanApplication';
import { ClientStatus } from './pages/ClientStatus';
import { ClientDecision } from './pages/ClientDecision';
import { Documents } from './pages/Documents';
import { Products } from './pages/Product'; 

function App() {
  const navigate = useNavigate();

  return (
    <Routes>
      <Route 
        path="/" 
        element={<RegistrationCard onSuccess={() => navigate('/dashboard')} />} 
      />
      
      <Route path="/dashboard" element={<Dashboard />} />
      
      <Route path="/home" element={<ClientHome />} />
      
      <Route path="/applications" element={<ClientApplicationsList />} />
      
      <Route path="/products" element={<Products />} />
      
      <Route path="/application/new" element={<LoanApplication />} />
      
      <Route path="/application/:id/status" element={<ClientStatus />} />
      
      <Route path="/application/:id/decision" element={<ClientDecision />} />
      
      <Route path="/documents" element={<Documents />} />
      
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
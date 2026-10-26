
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom';

import { RegistrationCard } from './pages/registration';
import { ClientApplicationsList } from './pages/ClientApplicationsList';
import { LoanApplication } from './pages/LoanApplication';
import { ClientStatus } from './pages/ClientStatus';
import { ClientDecision } from './pages/ClientDecision';
import { Documents } from './pages/Documents';
import { Products } from './pages/Product';
import { Header } from './components/Header';

function RegistrationGate() {
  const navigate = useNavigate();

  return (
    <div className="registration-gate">
      <RegistrationCard
        onSuccess={() => navigate('/applications', { replace: true })}
      />
    </div>
  );
}

function App() {
  return (
    <div className="app-layout">
      <Header />

      <Routes>
        <Route path="/" element={<RegistrationGate />} />

        <Route
          path="/dashboard"
          element={<Navigate to="/applications" replace />}
        />

        <Route
          path="/home"
          element={<Navigate to="/applications" replace />}
        />

        <Route
          path="/applications"
          element={<ClientApplicationsList />}
        />

        <Route path="/products" element={<Products />} />

        <Route
          path="/application/new"
          element={<LoanApplication />}
        />

        <Route path="/application/:id/edit"
               element={<LoanApplication />} />

        <Route
          path="/application/:id/status"
          element={<ClientStatus />}
        />

        <Route
          path="/application/:id/decision"
          element={<ClientDecision />}
        />

        <Route path="/documents" element={<Documents />} />

        <Route
          path="*"
          element={<Navigate to="/" replace />}
        />
      </Routes>
    </div>
  );
}

export default App;

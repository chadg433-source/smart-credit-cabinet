import { useNavigate } from 'react-router-dom';
import './Header.css';

export function Header() {
  const navigate = useNavigate();

  return (
    <header className="app-header">
      <button
        className="account-button"
        onClick={() => navigate('/applications')}
      >
        Личный кабинет
      </button>
    </header>
  );
}
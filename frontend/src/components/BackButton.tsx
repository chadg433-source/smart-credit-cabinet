import { useNavigate, useLocation } from 'react-router-dom';
import './Header.css';
export function Header() {
  const navigate = useNavigate();
  const location = useLocation();

  const isHideBack =
    location.pathname === '/' ||
    location.pathname.startsWith('/applications');

  const handleBack = () => {
    if (window.history.state && window.history.state.idx > 0) {
      navigate(-1);
    } else {
      navigate('/applications');
    }
  };

  return (
    <header
      className="app-header"
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '16px',
        justifyContent: 'flex-end'
      }}
    >
      <button
        className="account-button"
        onClick={() => navigate('/applications')}
      >
        Личный кабинет
      </button>

      {!isHideBack && (
        <button className="btn-back" onClick={handleBack}>
          ← Назад
        </button>
      )}
    </header>
  );
}
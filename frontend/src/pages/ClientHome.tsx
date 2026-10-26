// тут карточки с тем, какой кредит мы можем предложить и форма заявки
import { useNavigate } from 'react-router-dom';

export const ClientHome = () => {
  const navigate = useNavigate();

  return (
    <div className="dashboard-page">
      <div className="dashboard-header" style={{ width: '100%', maxWidth: '1000px' }}>
        <h1>Добро пожаловать!</h1>
      </div>
      <div className="loan-card" style={{ textAlign: 'center', maxWidth: '600px' }}>
        <h2>Умный кредитный кабинет</h2>
        <p>Здесь вы можете управлять своими заявками на кредит, отслеживать их статус и загружать документы.</p>
        <div style={{ display: 'flex', gap: '20px', justifyContent: 'center', marginTop: '30px' }}>
          <button className="btn-submit" onClick={() => navigate('/applications')}>Мои заявки</button>
          <button className="btn-submit" onClick={() => navigate('/products')}>Оформить кредит</button>
        </div>
      </div>
    </div>
  );
};
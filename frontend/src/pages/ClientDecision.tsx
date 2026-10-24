// тут результат и условия кредита
import { useParams, useNavigate } from 'react-router-dom';

export const ClientDecision = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  return (
    <div className="dashboard-page">
      <div className="dashboard-header" style={{ width: '100%', maxWidth: '800px' }}>
        <h1>Решение по заявке {id}</h1>
        <button className="logout-btn" onClick={() => navigate('/applications')}>Закрыть</button>
      </div>
      <div className="loan-card" style={{ border: '2px solid #10b981' }}>
        <h2 style={{ color: '#10b981' }}>Одобрено!</h2>
        <p>Поздравляем, ваша заявка одобрена. (Это демонстрационный экран).</p>
      </div>
    </div>
  );
};
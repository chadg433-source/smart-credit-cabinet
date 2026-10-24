// тут статус конкретной заявки и история
import { useParams, useNavigate } from 'react-router-dom';

export const ClientStatus = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  return (
    <div className="dashboard-page">
      <div className="dashboard-header" style={{ width: '100%', maxWidth: '800px' }}>
        <h1>Статус заявки {id}</h1>
        <button className="logout-btn" onClick={() => navigate('/applications')}>Назад</button>
      </div>
      <div className="loan-card">
        <h2>Заявка в обработке</h2>
        <p>Здесь будет отображаться история переходов статусов (таймлайн).</p>
        <button className="btn-submit" style={{ marginTop: '20px' }} onClick={() => navigate(`/application/${id}/decision`)}>
          Посмотреть решение (демо)
        </button>
      </div>
    </div>
  );
};
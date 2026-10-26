// тут подписание документов и выдача кредита
import { useNavigate } from 'react-router-dom';

export const Documents = () => {
  const navigate = useNavigate();

  return (
    <div className="dashboard-page">
      <div className="dashboard-header" style={{ width: '100%', maxWidth: '800px' }}>
        <h1>Документы</h1>
        <button className="logout-btn" onClick={() => navigate('/home')}>На главную</button>
      </div>
      <div className="loan-card">
        <h2>Загрузка документов</h2>
        <p>Здесь вы сможете прикрепить справки и выписки.</p>
        <input type="file" style={{ marginTop: '20px' }} />
      </div>
    </div>
  );
};
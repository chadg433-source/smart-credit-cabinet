// тут все заявки одного клиента
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import type { Application } from '../types';

export const ClientApplicationsList = () => {
  const navigate = useNavigate();
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getApplications().then(data => {
      setApplications(data);
      setLoading(false);
    });
  }, []);

  return (
    <div className="dashboard-page">
      <div className="dashboard-header" style={{ width: '100%', maxWidth: '1000px' }}>
        <h1>Мои заявки</h1>
        <button className="logout-btn" onClick={() => navigate('/home')}>На главную</button>
      </div>
      
      <div style={{ width: '100%', maxWidth: '1000px' }}>
        {loading ? <p>Загрузка...</p> : (
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {applications.map(app => (
              <li key={app.id} style={{ background: 'white', padding: '20px', marginBottom: '10px', borderRadius: '10px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)', cursor: 'pointer' }} onClick={() => navigate(`/application/${app.id}/status`)}>
                <strong>{app.productName}</strong> на сумму {app.amount.toLocaleString()} ₽ — <span style={{ color: 'blue' }}>{app.status}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

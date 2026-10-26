// src/pages/Dashboard.tsx
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import type { Application } from '../types';

export const Dashboard = () => {
  const navigate = useNavigate();
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getApplications().then(data => {
      setApplications(data);
      setLoading(false);
    });
  }, []);

  const handleLogout = () => navigate('/');

  const getStatusColor = (status: string) => {
    if (status === 'APPROVED') return '#10b981';
    if (status === 'DECLINED') return '#ef4444';
    if (status === 'DRAFT') return '#9ca3af';
    return '#3b82f6';
  };

  return (
    <div className="dashboard-page">
      <button type="button" className="logout-btn" onClick={handleLogout}>Выйти</button>

      <div className="dashboard-header" style={{ width: '100%', maxWidth: '1000px' }}>
        <h1>Мои заявки</h1>
        <button className="btn-submit" style={{ width: 'auto' }} onClick={() => navigate('/products')}>
          + Создать заявку
        </button>
      </div>

      <div style={{ width: '100%', maxWidth: '1000px' }}>
        {loading ? (
          <p>Загрузка заявок...</p>
        ) : applications.length === 0 ? (
          <p>У вас пока нет заявок.</p>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse', background: 'white', borderRadius: '12px', overflow: 'hidden', boxShadow: '0 4px 12px rgba(0,0,0,0.05)' }}>
            <thead style={{ background: '#f9fafb', textAlign: 'left' }}>
              <tr>
                <th style={{ padding: '16px', borderBottom: '1px solid #e5e7eb' }}>ID</th>
                <th style={{ padding: '16px', borderBottom: '1px solid #e5e7eb' }}>Продукт</th>
                <th style={{ padding: '16px', borderBottom: '1px solid #e5e7eb' }}>Сумма</th>
                <th style={{ padding: '16px', borderBottom: '1px solid #e5e7eb' }}>Статус</th>
                <th style={{ padding: '16px', borderBottom: '1px solid #e5e7eb' }}>Дата</th>
              </tr>
            </thead>
            <tbody>
              {applications.map(app => (
                <tr
                  key={app.id}
                  style={{ borderBottom: '1px solid #e5e7eb', cursor: 'pointer' }}
                  onClick={() => navigate(`/application/${app.id}/status`)}
                >
                  <td style={{ padding: '16px', color: '#6b7280' }}>{app.id}</td>
                  <td style={{ padding: '16px', fontWeight: 500 }}>{app.product_name}</td>
                  <td style={{ padding: '16px' }}>{app.requested_amount.toLocaleString()} ₽</td>
                  <td style={{ padding: '16px' }}>
                    <span style={{
                      padding: '4px 12px',
                      borderRadius: '20px',
                      fontSize: '13px',
                      fontWeight: 600,
                      color: 'white',
                      backgroundColor: getStatusColor(app.status)
                    }}>
                      {app.status}
                    </span>
                  </td>
                  <td style={{ padding: '16px', color: '#6b7280' }}>{app.created_at}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};
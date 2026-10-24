import React from 'react';

interface DashboardProps {
  onLogout: () => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onLogout }) => {
  return (
    <div className="dashboard-page">
      
      <button type="button" className="logout-btn" onClick={onLogout}>
        Выйти
      </button>

      <div className="dashboard-content">
        <div className="loan-card">
          <h2>Заявка на кредит</h2>
          <p>Заполните данные, чтобы получить решение за 2 минуты.</p>

          <form className="loan-form" onSubmit={(e) => e.preventDefault()}>
            <div className="form-group">
              <label>Сумма кредита (₽)</label>
              <input type="number" placeholder="Например, 100 000" className="reg-input" />
            </div>

            <div className="form-group">
              <label>Срок кредита</label>
              <select className="reg-input" defaultValue="12">
                <option value="6">6 месяцев</option>
                <option value="12">12 месяцев</option>
                <option value="24">24 месяца</option>
                <option value="36">36 месяцев</option>
              </select>
            </div>

            <div className="form-group">
              <label>Цель кредита</label>
              <input type="text" placeholder="Например, ремонт" className="reg-input" />
            </div>

            <button type="submit" className="btn-submit" style={{ marginTop: '20px' }}>
              Отправить заявку
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
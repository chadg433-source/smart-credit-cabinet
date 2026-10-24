import React from 'react';

interface LoanApplicationProps {
  onLogout: () => void;
}

export const LoanApplication: React.FC<LoanApplicationProps> = ({ onLogout }) => {
  return (
    <div className="card">
      <table className="card-table">
        <tbody>
          <tr>
            <td className="image-cell">
              <img src="/images/Zarp_Main-image-d.webp" alt="Кредитование" />
            </td>

            <td className="content-cell">
              <div className="content-center">
                <form className="reg-form" onSubmit={(e) => e.preventDefault()}>
                  <h1>Заявка на кредит</h1>
                  <p>Заполните данные, чтобы получить решение за 2 минуты.</p>
                  
                  <input 
                    type="number" 
                    placeholder="Сумма кредита (₽)" 
                    className="reg-input" 
                    min="10000" 
                    max="5000000" 
                    required
                  />
                  
                  <select className="reg-input" defaultValue="12">
                    <option value="6">6 месяцев</option>
                    <option value="12">12 месяцев</option>
                    <option value="24">24 месяца</option>
                    <option value="36">36 месяцев</option>
                  </select>

                  <input 
                    type="text" 
                    placeholder="Цель кредита (например, ремонт)" 
                    className="reg-input" 
                    required
                  />
                  
                  <button type="submit" className="btn-submit">
                    Отправить заявку
                  </button>
                </form>
              </div>

              <button 
                type="button" 
                className="btn" 
                onClick={onLogout}
              >
                Назад
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  );
};
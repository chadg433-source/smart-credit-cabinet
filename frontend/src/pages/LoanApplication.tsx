// src/pages/LoanApplication.tsx
import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import type { CreditProduct } from '../types';

export const LoanApplication = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const product = location.state?.product as CreditProduct;

  const [amount, setAmount] = useState(product?.minAmount || 100000);
  const [term, setTerm] = useState(product?.terms[0] || 12);
  
  const [revenue, setRevenue] = useState(500000);
  const [expenses, setExpenses] = useState(200000);
  const [loanPayments, setLoanPayments] = useState(0);
  
  const [loading, setLoading] = useState(false);

  if (!product) {
    navigate('/products', { replace: true });
    return null;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.createApplication({ 
        productId: product.id, 
        amount, 
        term,
        financials: {
          monthlyRevenue: revenue,
          monthlyExpenses: expenses,
          existingLoanPayments: loanPayments
        }
      });
      navigate('/dashboard');
    } catch (error) {
      console.error(error);
      setLoading(false);
      alert('Ошибка при создании заявки');
    }
  };

  return (
    <div className="dashboard-page">
      <div className="dashboard-header" style={{ width: '100%', maxWidth: '600px' }}>
        <h1>Заявка: {product.name}</h1>
      </div>

      <div className="loan-card">
        <form className="loan-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Сумма кредита (₽)</label>
            <input 
              type="number" 
              className="reg-input" 
              value={amount}
              onChange={(e) => setAmount(Number(e.target.value))}
              min={product.minAmount} 
              max={product.maxAmount} 
              required
            />
          </div>

          <div className="form-group">
            <label>Срок (мес.)</label>
            <select className="reg-input" value={term} onChange={(e) => setTerm(Number(e.target.value))}>
              {product.terms.map(t => <option key={t} value={t}>{t} мес.</option>)}
            </select>
          </div>

          <hr style={{ border: 'none', borderTop: '1px solid #e5e7eb', margin: '10px 0' }} />

          <h3 style={{ margin: '0 0 10px 0', fontSize: '18px' }}>Финансы бизнеса</h3>
          
          <div className="form-group">
            <label>Средняя месячная выручка (₽)</label>
            <input 
              type="number" 
              className="reg-input" 
              value={revenue}
              onChange={(e) => setRevenue(Number(e.target.value))}
              min="0"
              required
            />
          </div>

          <div className="form-group">
            <label>Средние месячные расходы (₽)</label>
            <input 
              type="number" 
              className="reg-input" 
              value={expenses}
              onChange={(e) => setExpenses(Number(e.target.value))}
              min="0"
              required
            />
          </div>

          <div className="form-group">
            <label>Текущие платежи по кредитам (₽)</label>
            <input 
              type="number" 
              className="reg-input" 
              value={loanPayments}
              onChange={(e) => setLoanPayments(Number(e.target.value))}
              min="0"
              required
            />
          </div>

          <button type="submit" className="btn-submit" disabled={loading} style={{ marginTop: '20px' }}>
            {loading ? 'Отправка...' : 'Отправить заявку на рассмотрение'}
          </button>
        </form>
      </div>
    </div>
  );
};
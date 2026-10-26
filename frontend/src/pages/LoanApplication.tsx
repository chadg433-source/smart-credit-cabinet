// src/pages/LoanApplication.tsx
import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import type { CreditProduct } from '../types';

export const LoanApplication = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const product = location.state?.product as CreditProduct;

  // Берем правильные поля из бэкенда (snake_case)
  const [amount, setAmount] = useState(product?.min_amount || 100000);
  const [term, setTerm] = useState(product?.min_term_months || 12);
  const [purpose, setPurpose] = useState('');
  const [loading, setLoading] = useState(false);

  // Если продукт не передан — на витрину
  if (!product) {
    navigate('/products', { replace: true });
    return null;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      // 1. Создаем заявку
      const app = await api.createApplication({
        business_id: "ad5e03f9-8a21-4531-a868-d199347418ff", // ID из сида
        credit_product_id: product.id, // Реальный UUID продукта
        requested_amount: amount,
        requested_term_months: term,
        purpose: purpose,
      });

      // 2. Сразу отправляем в банк
      await api.submitApplication(app.id);

      // 3. Переходим на статус
      navigate(`/application/${app.id}/status`);
    } catch (error) {
      console.error(error);
      alert('Ошибка при создании заявки');
      setLoading(false);
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
              min={product.min_amount}
              max={product.max_amount}
              required
            />
          </div>

          <div className="form-group">
            <label>Срок (мес.)</label>
            <input
              type="number"
              className="reg-input"
              value={term}
              onChange={(e) => setTerm(Number(e.target.value))}
              min={product.min_term_months}
              max={product.max_term_months}
              required
            />
          </div>

          <div className="form-group">
            <label>Цель кредита</label>
            <input
              type="text"
              className="reg-input"
              placeholder="Например, покупка оборудования"
              value={purpose}
              onChange={(e) => setPurpose(e.target.value)}
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

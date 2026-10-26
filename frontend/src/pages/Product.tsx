// src/pages/Products.tsx
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import type { CreditProduct } from '../types';

export const Products = () => {
  const [products, setProducts] = useState<CreditProduct[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    api.getProducts().then(data => {
      setProducts(data);
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="dashboard-page">Загрузка продуктов...</div>;

  return (
    <div className="dashboard-page">
      <div className="dashboard-header" style={{ width: '100%', maxWidth: '1000px' }}>
        <h1>Каталог продуктов</h1>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px', width: '100%', maxWidth: '1000px' }}>
        {products.map(product => (
          <div key={product.id} className="loan-card" style={{ maxWidth: '100%', margin: 0 }}>
            <h2>{product.name}</h2>
            <p>{product.description}</p>
            <div style={{ marginBottom: '20px', fontSize: '14px', color: '#6b7280' }}>
              {/* ЗАМЕНИЛИ minAmount -> min_amount, maxAmount -> max_amount */}
              <p>Сумма: от {product.min_amount.toLocaleString()} до {product.max_amount.toLocaleString()} ₽</p>
              {/* ЗАМЕНИЛИ terms.join -> min_term_months / max_term_months */}
              <p>Сроки: от {product.min_term_months} до {product.max_term_months} мес.</p>
            </div>
            <button
              className="btn-submit"
              onClick={() => navigate('/application/new', { state: { product } })}
            >
              Оформить заявку
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

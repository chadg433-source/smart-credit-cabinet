import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import type { Business, CreditProduct } from '../types';

export const LoanApplication = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const product = location.state?.product as CreditProduct | undefined;

  const [amount, setAmount] = useState(product?.min_amount ?? 100000);
  const [term, setTerm] = useState(product?.min_term_months ?? 12);
  const [purpose, setPurpose] = useState('');

  const [businesses, setBusinesses] = useState<Business[]>([]);
  const [selectedBusinessId, setSelectedBusinessId] = useState('');
  const [businessesLoading, setBusinessesLoading] = useState(true);
  const [businessesError, setBusinessesError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;

    const loadBusinesses = async () => {
      try {
        const data = await api.getBusinesses();

        if (cancelled) return;

        setBusinesses(data);

        if (data.length > 0) {
          setSelectedBusinessId(data[0].id);
        }
      } catch (error) {
        console.error(error);

        if (!cancelled) {
          setBusinessesError('Не удалось загрузить список компаний.');
        }
      } finally {
        if (!cancelled) {
          setBusinessesLoading(false);
        }
      }
    };

    void loadBusinesses();

    return () => {
      cancelled = true;
    };
  }, []);

  if (!product) {
    return (
      <div className="dashboard-page">
        <div className="loan-card">
          <p>Кредитный продукт не выбран.</p>
          <button
            type="button"
            className="btn-submit"
            onClick={() => navigate('/products', { replace: true })}
          >
            Вернуться к продуктам
          </button>
        </div>
      </div>
    );
  }

  const selectedBusiness = businesses.find(
    (business) => business.id === selectedBusinessId
  );

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!selectedBusinessId) {
      alert('Выберите компанию для оформления кредита.');
      return;
    }

    if (
      amount < product.min_amount ||
      amount > product.max_amount ||
      term < product.min_term_months ||
      term > product.max_term_months
    ) {
      alert('Проверьте сумму и срок кредита.');
      return;
    }

    setLoading(true);

    try {
      const app = await api.createApplication({
        business_id: selectedBusinessId,
        credit_product_id: product.id,
        requested_amount: amount,
        requested_term_months: term,
        purpose: purpose.trim(),
      });

      await api.submitApplication(app.id);

      navigate(`/application/${app.id}/status`);
    } catch (error) {
      console.error(error);
      alert('Не удалось создать или отправить заявку. Попробуйте ещё раз.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dashboard-page">
      <div
        className="dashboard-header"
        style={{ width: '100%', maxWidth: '600px' }}
      >
        <h1>Заявка: {product.name}</h1>
      </div>

      <div className="loan-card">
        <form className="loan-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="business">Компания-заёмщик</label>

            {businessesLoading ? (
              <p>Загрузка компаний...</p>
            ) : businessesError ? (
              <>
                <p role="alert">{businessesError}</p>
                <button
                  type="button"
                  className="btn-submit"
                  onClick={() => window.location.reload()}
                >
                  Повторить загрузку
                </button>
              </>
            ) : businesses.length === 0 ? (
              <p>Нет доступных компаний для оформления кредита.</p>
            ) : (
              <>
                <select
                  id="business"
                  className="reg-input"
                  value={selectedBusinessId}
                  onChange={(e) => setSelectedBusinessId(e.target.value)}
                  required
                >
                  <option value="" disabled>
                    Выберите компанию
                  </option>

                  {businesses.map((business) => (
                    <option key={business.id} value={business.id}>
                      {business.name} — ИНН {business.tax_id}
                    </option>
                  ))}
                </select>

                {selectedBusiness && (
                  <div style={{ marginTop: '10px' }}>
                    <p>
                      Вид деятельности: {selectedBusiness.business_type}
                    </p>
                    <p>
                      Выручка в месяц:{' '}
                      {selectedBusiness.monthly_revenue.toLocaleString('ru-RU')}{' '}
                      ₽
                    </p>
                    <p>
                      Расходы в месяц:{' '}
                      {selectedBusiness.monthly_expenses.toLocaleString('ru-RU')}{' '}
                      ₽
                    </p>
                    <p>
                      Платежи по действующим кредитам:{' '}
                      {selectedBusiness.existing_monthly_loan_payments.toLocaleString(
                        'ru-RU'
                      )}{' '}
                      ₽
                    </p>
                  </div>
                )}
              </>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="amount">Сумма кредита (₽)</label>
            <input
              id="amount"
              type="number"
              className="reg-input"
              value={amount}
              onChange={(e) => setAmount(Number(e.target.value))}
              min={product.min_amount}
              max={product.max_amount}
              step="any"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="term">Срок (мес.)</label>
            <input
              id="term"
              type="number"
              className="reg-input"
              value={term}
              onChange={(e) => setTerm(Number(e.target.value))}
              min={product.min_term_months}
              max={product.max_term_months}
              step="1"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="purpose">Цель кредита</label>
            <input
              id="purpose"
              type="text"
              className="reg-input"
              placeholder="Например, покупка оборудования"
              value={purpose}
              onChange={(e) => setPurpose(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            className="btn-submit"
            disabled={
              loading ||
              businessesLoading ||
              !!businessesError ||
              businesses.length === 0 ||
              !selectedBusinessId
            }
            style={{ marginTop: '20px' }}
          >
            {loading ? 'Отправка...' : 'Отправить заявку на рассмотрение'}
          </button>
        </form>
      </div>
    </div>
  );
};
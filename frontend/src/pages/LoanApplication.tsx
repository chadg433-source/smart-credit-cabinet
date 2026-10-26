
import { useEffect, useState } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { api } from '../api/client';
import type { Application, Business, CreditProduct } from '../types';

export const LoanApplication = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { id } = useParams();

  const editing = Boolean(id);
  const initialProduct = location.state?.product as
    | CreditProduct
    | undefined;

  const [product, setProduct] = useState<CreditProduct | undefined>(
    initialProduct,
  );
  const [application, setApplication] = useState<Application | null>(null);
  const [applicationLoading, setApplicationLoading] = useState(editing);
  const [applicationError, setApplicationError] = useState('');

  const [amount, setAmount] = useState(initialProduct?.min_amount ?? 100000);
  const [term, setTerm] = useState(initialProduct?.min_term_months ?? 12);
  const [purpose, setPurpose] = useState('');

  const [businesses, setBusinesses] = useState<Business[]>([]);
  const [selectedBusinessId, setSelectedBusinessId] = useState('');
  const [businessesLoading, setBusinessesLoading] = useState(true);
  const [businessesError, setBusinessesError] = useState('');

  const [loading, setLoading] = useState(false);

  // Загружаем компании заёмщика.
  useEffect(() => {
    let cancelled = false;

    const loadBusinesses = async () => {
      try {
        const data = await api.getBusinesses();

        if (cancelled) return;

        setBusinesses(data);

        // При создании выбираем первую компанию.
        // При редактировании компанию установим из существующей заявки.
        if (!id && data.length > 0) {
          setSelectedBusinessId(data[0].id);
        }
      } catch (error) {
        console.error('Ошибка загрузки компаний:', error);

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
  }, [id]);

  // При редактировании загружаем заявку и её кредитный продукт.
  useEffect(() => {
    if (!id) return;
    let cancelled = false;

    const loadApplication = async () => {
      try {
        const result = await api.getApplicationById(id);

        if (!result) {
          throw new Error('Заявка не найдена.');
        }

        if (result.status !== 'NEED_MORE_INFO') {
          throw new Error(
            'Эту заявку нельзя редактировать: она больше не требует дополнения.',
          );
        }

        const products = await api.getProducts();

        const matchingProduct = products.find(
          (item) => item.id === result.credit_product_id,
        );

        if (!matchingProduct) {
          throw new Error('Кредитный продукт не найден.');
        }

        if (cancelled) return;

        setApplication(result);
        setProduct(matchingProduct);
        setAmount(result.requested_amount);
        setTerm(result.requested_term_months);
        setPurpose(result.purpose ?? '');
        setSelectedBusinessId(result.business_id);
      } catch (error) {
        console.error('Ошибка загрузки заявки:', error);

        if (!cancelled) {
          setApplicationError(
            error instanceof Error
              ? error.message
              : 'Не удалось загрузить заявку.',
          );
        }
      } finally {
        if (!cancelled) {
          setApplicationLoading(false);
        }
      }
    };

    void loadApplication();

    return () => {
      cancelled = true;
    };
  }, [id]);

  const selectedBusiness = businesses.find(
    (business) => business.id === selectedBusinessId,
  );

  const handleSubmit = async (
    e: React.FormEvent<HTMLFormElement>,
  ) => {
    e.preventDefault();

    if (!product) {
      alert('Кредитный продукт не выбран.');
      return;
    }

    if (editing && (!id || !application)) {
      alert('Не удалось загрузить заявку для редактирования.');
      return;
    }

    if (!selectedBusinessId) {
      alert('Выберите компанию для оформления кредита.');
      return;
    }

    const trimmedPurpose = purpose.trim();

    if (!trimmedPurpose || trimmedPurpose.length > 255) {
      alert('Укажите цель кредита длиной не более 255 символов.');
      return;
    }

    if (
      !Number.isFinite(amount) ||
      amount < product.min_amount ||
      amount > product.max_amount
    ) {
      alert('Проверьте сумму кредита.');
      return;
    }

    if (
      !Number.isInteger(term) ||
      term < product.min_term_months ||
      term > product.max_term_months
    ) {
      alert('Проверьте срок кредита.');
      return;
    }

    setLoading(true);

    try {
      if (editing && id && application) {
        // Обновляем существующую заявку, не создавая новую.
        await api.updateApplication(id, {
          requested_amount: amount,
          requested_term_months: term,
          purpose: trimmedPurpose,
        });

        // Повторно отправляем её на обработку.
        await api.submitApplication(id);

        navigate(`/application/${id}/status`);
      } else {
        // Обычное создание новой заявки.
        const app = await api.createApplication({
          business_id: selectedBusinessId,
          credit_product_id: product.id,
          requested_amount: amount,
          requested_term_months: term,
          purpose: trimmedPurpose,
        });

        await api.submitApplication(app.id);

        navigate(`/application/${app.id}/status`);
      }
    } catch (error) {
      console.error('Ошибка отправки заявки:', error);

      alert(
        error instanceof Error
          ? error.message
          : 'Не удалось сохранить или отправить заявку. Попробуйте ещё раз.',
      );
    } finally {
      setLoading(false);
    }
  };

  if (applicationLoading) {
    return (
      <div className="dashboard-page">
        <div className="loan-card">
          <p>Загрузка заявки...</p>
        </div>
      </div>
    );
  }

  if (applicationError) {
    return (
      <div className="dashboard-page">
        <div className="loan-card">
          <h2>Не удалось открыть заявку</h2>
          <p role="alert">{applicationError}</p>

          <button
            type="button"
            className="btn-submit"
            onClick={() => navigate('/applications')}
          >
            Вернуться к заявкам
          </button>
        </div>
      </div>
    );
  }

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

  return (
    <div className="dashboard-page">
      <div
        className="dashboard-header"
        style={{ width: '100%', maxWidth: '600px' }}
      >
        <h1>
          {editing ? 'Дополнение заявки: ' : 'Заявка: '}
          {product.name}
        </h1>
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
                      {selectedBusiness.monthly_revenue.toLocaleString(
                        'ru-RU',
                      )}{' '}
                      ₽
                    </p>

                    <p>
                      Расходы в месяц:{' '}
                      {selectedBusiness.monthly_expenses.toLocaleString(
                        'ru-RU',
                      )}{' '}
                      ₽
                    </p>

                    <p>
                      Платежи по действующим кредитам:{' '}
                      {selectedBusiness.existing_monthly_loan_payments.toLocaleString(
                        'ru-RU',
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
              maxLength={255}
              required
            />
          </div>

          <button
            type="submit"
            className="btn-submit"
            disabled={
              loading ||
              applicationLoading ||
              businessesLoading ||
              !!businessesError ||
              businesses.length === 0 ||
              !selectedBusinessId
            }
            style={{ marginTop: '20px' }}
          >
            {loading
              ? 'Отправка...'
              : editing
                ? 'Сохранить и отправить повторно'
                : 'Отправить заявку на рассмотрение'}
          </button>
        </form>
      </div>
    </div>
  );
};

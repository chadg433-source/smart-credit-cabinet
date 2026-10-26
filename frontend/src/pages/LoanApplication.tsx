import { useEffect, useState } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { api } from '../api/client';
import { ApplicationAttachments } from '../components/ApplicationAttachments';
import type { Application, Business, CreditProduct } from '../types';

export const LoanApplication = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { id } = useParams();

  const editing = Boolean(id);
  const initialProduct = location.state?.product as CreditProduct | undefined;

  const [product, setProduct] = useState<CreditProduct | undefined>(initialProduct);
  const [application, setApplication] = useState<Application | null>(null);
  const [createdApplicationId, setCreatedApplicationId] = useState<string | null>(null);
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
  const [formSaved, setFormSaved] = useState(false);
  const [submitError, setSubmitError] = useState('');

  const activeApplicationId = id ?? createdApplicationId;

  useEffect(() => {
    let cancelled = false;

    const loadBusinesses = async () => {
      try {
        const data = await api.getBusinesses();

        if (cancelled) return;

        setBusinesses(data);

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

  const handleSave = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitError('');

    if (!product) {
      setSubmitError('Кредитный продукт не выбран.');
      return;
    }

    if (editing && (!id || !application)) {
      setSubmitError('Не удалось загрузить заявку для редактирования.');
      return;
    }

    if (!selectedBusinessId) {
      setSubmitError('Выберите компанию для оформления кредита.');
      return;
    }

    const trimmedPurpose = purpose.trim();

    if (!trimmedPurpose || trimmedPurpose.length > 255) {
      setSubmitError('Укажите цель кредита длиной не более 255 символов.');
      return;
    }

    if (
      !Number.isFinite(amount) ||
      amount < product.min_amount ||
      amount > product.max_amount
    ) {
      setSubmitError('Проверьте сумму кредита.');
      return;
    }

    if (
      !Number.isInteger(term) ||
      term < product.min_term_months ||
      term > product.max_term_months
    ) {
      setSubmitError('Проверьте срок кредита.');
      return;
    }

    setLoading(true);

    try {
      if (editing && id) {
        await api.updateApplication(id, {
          requested_amount: amount,
          requested_term_months: term,
          purpose: trimmedPurpose,
        });

        setFormSaved(true);
      } else {
        const result = await api.createApplication({
          business_id: selectedBusinessId,
          credit_product_id: product.id,
          requested_amount: amount,
          requested_term_months: term,
          purpose: trimmedPurpose,
        });

        setCreatedApplicationId(result.id);
        setFormSaved(true);
      }
    } catch (error) {
      console.error('Ошибка сохранения заявки:', error);

      setSubmitError(
        error instanceof Error
          ? error.message
          : 'Не удалось сохранить заявку.',
      );
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitForReview = async () => {
    if (!activeApplicationId) return;

    setLoading(true);
    setSubmitError('');

    try {
      await api.submitApplication(activeApplicationId);
      navigate(`/application/${activeApplicationId}/status`);
    } catch (error) {
      console.error('Ошибка отправки заявки:', error);

      setSubmitError(
        error instanceof Error
          ? error.message
          : 'Не удалось отправить заявку на рассмотрение.',
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
        <form className="loan-form" onSubmit={handleSave}>
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
                  onChange={(event) =>
                    setSelectedBusinessId(event.target.value)
                  }
                  required
                  disabled={editing}
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
                  <div style={{ marginTop: 10 }}>
                    <p>Вид деятельности: {selectedBusiness.business_type}</p>
                    <p>
                      Выручка в месяц:{' '}
                      {selectedBusiness.monthly_revenue.toLocaleString('ru-RU')} ₽
                    </p>
                    <p>
                      Расходы в месяц:{' '}
                      {selectedBusiness.monthly_expenses.toLocaleString('ru-RU')} ₽
                    </p>
                    <p>
                      Платежи по действующим кредитам:{' '}
                      {selectedBusiness.existing_monthly_loan_payments.toLocaleString('ru-RU')} ₽
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
              onChange={(event) => setAmount(Number(event.target.value))}
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
              onChange={(event) => setTerm(Number(event.target.value))}
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
              onChange={(event) => setPurpose(event.target.value)}
              maxLength={255}
              required
            />
          </div>

          {submitError && <p role="alert">{submitError}</p>}

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
            style={{ marginTop: 20 }}
          >
            {loading
              ? 'Сохранение...'
              : formSaved
                ? 'Сохранить изменения'
                : 'Сохранить заявку'}
          </button>
        </form>
      </div>

      {activeApplicationId && formSaved && (
        <>
          <ApplicationAttachments applicationId={activeApplicationId} />

          <div className="loan-card" style={{ marginTop: 24 }}>
            <h2>Отправка заявки</h2>
            <p>
              Убедитесь, что необходимые документы загружены, затем отправьте
              заявку на рассмотрение.
            </p>
            {submitError && <p role="alert">{submitError}</p>}
            <button
              type="button"
              className="btn-submit"
              onClick={() => void handleSubmitForReview()}
              disabled={loading}
            >
              {loading ? 'Отправка...' : 'Отправить на рассмотрение'}
            </button>
          </div>
        </>
      )}
    </div>
  );
};

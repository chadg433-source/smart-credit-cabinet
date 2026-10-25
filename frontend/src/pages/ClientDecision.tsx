// тут результат и условия кредита
import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import type { Application } from '../types';

export const ClientDecision = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [application, setApplication] = useState<Application | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;

    const loadApplication = async () => {
      setLoading(true);

      try {
        const result = id ? await api.getApplicationById(id) : null;

        if (active) {
          setApplication(result);
        }
      } catch {
        if (active) {
          setApplication(null);
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };

    void loadApplication();

    return () => {
      active = false;
    };
  }, [id]);

  const isApproved = application?.status === 'APPROVED';
  const isDeclined = application?.status === 'DECLINED';
  const hasDecision =
    isApproved ||
    isDeclined ||
    application?.status === 'ALTERNATIVE_OFFER';

  return (
    <div className="dashboard-page">
      <div className="dashboard-header" style={{ width: '100%', maxWidth: '800px' }}>
        <h1>Решение по заявке {id}</h1>
      </div>

      <div className="loan-card">
        {loading ? (
          <p>Загрузка решения...</p>
        ) : !application ? (
          <>
            <h2>Заявка не найдена</h2>
            <p>Не удалось найти заявку с таким номером.</p>
          </>
        ) : hasDecision ? (
          <>
            <h2
              style={{
                color: isApproved ? '#10b981' : isDeclined ? '#ef4444' : '#d97706'
              }}
            >
              {isApproved
                ? 'Одобрено!'
                : isDeclined
                  ? 'Отказано'
                  : 'Предложен другой вариант'}
            </h2>
            <p>Номер заявки: {application.id}</p>
            <p>Продукт: {application.productName}</p>
            <p>Сумма заявки: {application.amount.toLocaleString('ru-RU')} ₽</p>
            <p>Срок: {application.term} мес.</p>
          </>
        ) : (
          <>
            <h2>Решение пока не принято</h2>
            <p>
              Текущий статус заявки: {application.status}
            </p>
            <p>Вернись сюда позже, когда обработка заявки завершится.</p>
          </>
        )}

        <button
          className="btn-submit"
          style={{ marginTop: '20px' }}
          onClick={() => navigate(`/application/${id}/status`)}
        >
          Вернуться к статусу
        </button>
      </div>
    </div>
  );
};

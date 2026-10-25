
import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import type { Application, ApplicationStatus } from '../types';

const statusLabels: Record<ApplicationStatus, string> = {
  DRAFT: 'Черновик',
  SUBMITTED: 'Заявка отправлена',
  DATA_CHECK: 'Проверка данных',
  MORE_INFO_REQUIRED: 'Требуется дополнительная информация',
  EXTERNAL_CHECK: 'Внешняя проверка',
  SCORING: 'Оценка заявки',
  DECISION: 'Подготовка решения',
  APPROVED: 'Одобрена',
  DECLINED: 'Отказано',
  ALTERNATIVE_OFFER: 'Предложен другой вариант'
};

export const ClientStatus = () => {
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

  return (
    <div className="dashboard-page">
      <div className="dashboard-header" style={{ width: '100%', maxWidth: '800px' }}>
        <h1>Статус заявки {id}</h1>
      </div>

      <div className="loan-card">
        {loading ? (
          <p>Загрузка заявки...</p>
        ) : !application ? (
          <>
            <h2>Заявка не найдена</h2>
            <p>Проверь ID заявки и попробуй ещё раз.</p>
          </>
        ) : (
          <>
            <h2>{statusLabels[application.status]}</h2>
            <p>Номер заявки: {application.id}</p>
            <p>Продукт: {application.productName}</p>
            <p>Сумма: {application.amount.toLocaleString('ru-RU')} ₽</p>
            <p>Срок: {application.term} мес.</p>

            <h3>История статусов</h3>

            {application.history && application.history.length > 0 ? (
              <div>
                {application.history.map((item) => (
                  <div key={item.id} style={{ marginBottom: '16px' }}>
                    <p>
                      <strong>{statusLabels[item.newStatus]}</strong>
                    </p>
                    <p>{item.reason}</p>
                    <p>{new Date(item.date).toLocaleString('ru-RU')}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p>История переходов пока отсутствует.</p>
            )}

            <button
              className="btn-submit"
              style={{ marginTop: '20px' }}
              onClick={() => navigate(`/application/${application.id}/decision`)}
            >
              Посмотреть решение
            </button>
          </>
        )}
      </div>
    </div>
  );
};

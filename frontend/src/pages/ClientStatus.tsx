
import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import type { Application, ApplicationStatus, HistoryItem } from '../types';

const statusLabels: Record<ApplicationStatus, string> = {
  DRAFT: 'Черновик',
  SUBMITTED: 'Заявка отправлена',
  VALIDATION: 'Проверка данных',
  NEED_MORE_INFO: 'Требуется дополнительная информация',
  EXTERNAL_CHECKS: 'Внешняя проверка',
  SCORING: 'Оценка заявки',
  DECISION_PENDING: 'Подготовка решения',
  APPROVED: 'Одобрена',
  APPROVED_WITH_CONDITIONS: 'Одобрена с условиями',
  REJECTED: 'Отказано',
  DOCUMENTS: 'Оформление документов',
  DISBURSED: 'Кредит выдан'
};

export const ClientStatus = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [application, setApplication] = useState<Application | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;

    const loadApplication = async () => {
  setLoading(true);

  try {
    const result = id ? await api.getApplicationById(id) : null;

    if (!active) return;

    setApplication(result);

    if (result && id) {
      try {
        const historyResult = await api.getHistory(id);

        if (active) {
          setHistory(historyResult);
        }
      } catch (error) {
        console.error('Ошибка загрузки истории:', error);

        if (active) {
          setHistory([]);
        }
      }
    } else {
      setHistory([]);
    }
  } catch (error) {
    console.error('Ошибка загрузки заявки:', error);

    if (active) {
      setApplication(null);
      setHistory([]);
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
            <h2>{statusLabels[application.status] ?? application.status}</h2>
            <p>Номер заявки: {application.id}</p>
            <p>Сумма: {Number(application.requested_amount).toLocaleString('ru-RU')} ₽</p>
            <p>Срок: {application.requested_term_months} мес.</p>
            <h3>История статусов</h3>

            {history.length > 0 ? (
              <div>
                {history.map((item, index) => (
                  <div key={`${item.created_at}-${index}`} style={{ marginBottom: '16px' }}>
                    <p>
                      <strong>
                        {statusLabels[item.new_status] ?? item.new_status}
                      </strong>
                    </p>
                    <p>{item.comment}</p>
                    <p>{new Date(item.created_at).toLocaleString('ru-RU')}</p>
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

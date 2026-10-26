import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';
import type { Application } from '../types';

const formatAmount = (amount: number) =>
  new Intl.NumberFormat('ru-RU', {
    maximumFractionDigits: 0,
  }).format(amount) + ' ₽';

const formatDate = (date: string) => {
  const parsedDate = new Date(date);

  if (Number.isNaN(parsedDate.getTime())) {
    return date;
  }

  return new Intl.DateTimeFormat('ru-RU', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
  }).format(parsedDate);
};

const getStatusInfo = (status: string) => {
  const normalized = status.toUpperCase();

  switch (normalized) {
    case 'DRAFT':
      return { label: 'Черновик', className: 'draft', icon: '✎' };
    case 'SCORING':
      return { label: 'На рассмотрении', className: 'scoring', icon: '◷' };
    case 'APPROVED':
      return { label: 'Одобрена', className: 'approved', icon: '✓' };
    case 'REJECTED':
      return { label: 'Отказ', className: 'rejected', icon: '×' };
    case 'PENDING':
      return { label: 'Ожидает решения', className: 'pending', icon: '◷' };
    default:
      return { label: status, className: 'default', icon: '•' };
  }
};

export const ClientApplicationsList = () => {
  const navigate = useNavigate();
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;

    api
      .getApplications()
      .then((data) => {
        if (active) {
          setApplications(data);
          setError('');
        }
      })
      .catch(() => {
        if (active) {
          setError('Не удалось загрузить заявки. Попробуйте ещё раз.');
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, []);

  const stats = useMemo(
    () => ({
      total: applications.length,
      review: applications.filter((app) =>
        ['SCORING', 'PENDING'].includes(app.status.toUpperCase()),
      ).length,
      approved: applications.filter(
        (app) => app.status.toUpperCase() === 'APPROVED',
      ).length,
      totalAmount: applications.reduce((sum, app) => sum + app.requested_amount, 0),
    }),
    [applications],
  );

  const openApplication = (id: string) => {
    navigate(`/application/${id}/status`);
  };

  const openProductCatalog = () => {
    navigate('/products');
  };

  return (
    <main className="applications-page">
      <div className="applications-container">
        <section className="applications-heading">
          <div>
            <h1>Мои заявки</h1>
            <p>
              Отслеживайте состояние заявок и управляйте кредитованием бизнеса.
            </p>
          </div>

          <button
            className="applications-primary-button"
            type="button"
            onClick={openProductCatalog}
          >
            <span aria-hidden="true">＋</span>
            Добавить заявку
          </button>
        </section>

        <section className="applications-stats" aria-label="Статистика заявок">
          <article className="applications-stat-card">
            <div className="applications-stat-top">
              <span className="applications-stat-icon icon-blue">▤</span>
              <span className="applications-stat-caption">Всего</span>
            </div>
            <strong>{stats.total}</strong>
            <span className="applications-stat-description">Все заявки</span>
          </article>

          <article className="applications-stat-card">
            <div className="applications-stat-top">
              <span className="applications-stat-icon icon-orange">◷</span>
              <span className="applications-stat-caption">В процессе</span>
            </div>
            <strong>{stats.review}</strong>
            <span className="applications-stat-description">
              Ожидают решения
            </span>
          </article>

          <article className="applications-stat-card">
            <div className="applications-stat-top">
              <span className="applications-stat-icon icon-green">✓</span>
              <span className="applications-stat-caption">Одобрено</span>
            </div>
            <strong>{stats.approved}</strong>
            <span className="applications-stat-description">
              Положительные решения
            </span>
          </article>

          <article className="applications-stat-card">
            <div className="applications-stat-top">
              <span className="applications-stat-icon icon-purple">₽</span>
              <span className="applications-stat-caption">Сумма заявок</span>
            </div>
            <strong className="applications-stat-amount">
              {formatAmount(stats.totalAmount)}
            </strong>
            <span className="applications-stat-description">
              По всем заявкам
            </span>
          </article>
        </section>

        <section className="applications-list-section">
          <div className="applications-list-heading">
            <div>
              <h2>История заявок</h2>
              <p>Выберите заявку, чтобы посмотреть подробности.</p>
            </div>

            {!loading && (
              <span className="applications-count">
                {applications.length} шт.
              </span>
            )}
          </div>

          {loading ? (
            <div className="applications-state">
              <span className="applications-loader" />
              <strong>Загружаем заявки</strong>
              <p>Пожалуйста, подождите немного.</p>
            </div>
          ) : error ? (
            <div className="applications-state applications-error">
              <span className="applications-state-icon">!</span>
              <strong>Не удалось загрузить данные</strong>
              <p>{error}</p>
              <button
                type="button"
                className="applications-secondary-button"
                onClick={() => window.location.reload()}
              >
                Повторить
              </button>
            </div>
          ) : applications.length === 0 ? (
            <div className="applications-state">
              <span className="applications-empty-icon">▤</span>
              <strong>Пока нет заявок</strong>
              <p>
                Создайте первую заявку, чтобы начать работу с кредитным кабинетом.
              </p>
              <button
                className="applications-primary-button"
                type="button"
                onClick={openProductCatalog}
              >
                Выбрать продукт
              </button>
            </div>
          ) : (
            <div className="applications-list">
              {applications.map((app) => {
                const status = getStatusInfo(app.status);

                return (
                  <article
                    className="application-card"
                    key={app.id}
                    role="button"
                    tabIndex={0}
                    onClick={() => openApplication(app.id)}
                    onKeyDown={(event) => {
                      if (event.key === 'Enter' || event.key === ' ') {
                        event.preventDefault();
                        openApplication(app.id);
                      }
                    }}
                  >
                    <div className="application-product-icon" aria-hidden="true">
                      ₽
                    </div>

                    <div className="application-main">
                      <div className="application-card-meta">
                        <span className="application-id">№ {app.id}</span>
                        <span className="application-meta-dot">·</span>
                        <span>{formatDate(app.created_at)}</span>
                      </div>

                      <h3>{app.product_name}</h3>

                      <div className="application-details">
                        <span className="application-amount">
                          {formatAmount(app.requested_amount)}
                        </span>
                        <span className="application-meta-dot">·</span>
                        <span>{app.requested_term_months} мес.</span>
                      </div>
                    </div>

                    <div className="application-card-right">
                      <span
                        className={`application-status status-${status.className}`}
                      >
                        <span aria-hidden="true">{status.icon}</span>
                        {status.label}
                      </span>
                      <span className="application-open">
                        Подробнее <span aria-hidden="true">→</span>
                      </span>
                    </div>
                  </article>
                );
              })}
            </div>
          )}
        </section>

        <footer className="applications-footer">
          <span>Кредитный кабинет предпринимателя</span>
          <span>Данные отображаются в рамках текущего проекта</span>
        </footer>
      </div>
    </main>
  );
};
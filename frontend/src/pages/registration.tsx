
import React, { useState } from 'react';
import { api } from '../api/client';
import { useCardController } from '../controller/Controller.ts';

interface RegistrationCardProps {
  onSuccess?: () => void;
}

export const RegistrationCard: React.FC<RegistrationCardProps> = ({
  onSuccess,
}) => {
  const { isRegistering, handleOpenRegistration } = useCardController();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    setLoading(true);
    setError('');

    try {
      await api.demoLogin();
      await api.getMe();
      onSuccess?.();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Не удалось войти в систему',
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="registration-overlay">
      <div
        className="registration-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="registration-title"
      >
        <div className="card">
          <table className="card-table">
            <tbody>
              <tr>
                <td className="image-cell">
                  <img
                    src="/images/Zarp_Main-image-d.webp"
                    alt="Иллюстрация кредитного кабинета"
                  />
                </td>

                <td className="content-cell">
                  <div className="content-center">
                    {!isRegistering ? (
                      <>
                        <h1 id="registration-title">
                          Финансовые возможности для вашего бизнеса
                        </h1>

                        <p>
                          Создайте аккаунт, чтобы оформлять кредитные заявки,
                          управлять ими и отслеживать решения в одном месте.
                        </p>
                      </>
                    ) : (
                      <form className="reg-form" onSubmit={handleSubmit}>
                        <h1 id="registration-title">Вход в демо-кабинет</h1>

                        <p>
                          Войдите, чтобы получить доступ к демонстрационному
                          кабинету предпринимателя.
                        </p>

                        {error && <p role="alert">{error}</p>}

                        <button
                          type="submit"
                          className="btn-submit"
                          style={{ marginTop: '10px' }}
                          disabled={loading}
                        >
                          {loading ? 'Выполняется вход...' : 'Войти через демо-пользователя'}
                        </button>
                      </form>
                    )}
                  </div>

                  {!isRegistering && (
                    <button
                      type="button"
                      className="btn"
                      onClick={handleOpenRegistration}
                    >
                      Подробнее
                    </button>
                  )}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};


import React from 'react';
import { useCardController } from '../controller/Controller.ts';

interface RegistrationCardProps {
  onSuccess?: () => void;
}

export const RegistrationCard: React.FC<RegistrationCardProps> = ({
  onSuccess,
}) => {
  const { isRegistering, handleOpenRegistration } = useCardController();

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    onSuccess?.();
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
                      <form
                        className="reg-form"
                        onSubmit={handleSubmit}
                      >
                        <h1 id="registration-title">Регистрация</h1>

                        <p>
                          Создайте аккаунт для доступа к системе.
                        </p>

                        <button
                          type="submit"
                          className="btn-submit"
                          style={{ marginTop: '10px' }}
                        >
                          Зарегистрироваться через Альфа-Банк
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

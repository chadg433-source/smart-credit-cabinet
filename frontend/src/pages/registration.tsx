import React from 'react';
import { useCardController } from '../controller/Controller.ts';
interface RegistrationCardProps {
  onSuccess?: () => void;
}

export const RegistrationCard: React.FC<RegistrationCardProps> = ({ onSuccess }) => {
  const { isRegistering, handleOpenRegistration } = useCardController();
  const alfaAuthLink = `https://id-sandbox.alfabank.ru/oidc/authorize?client_id=ВАШ_CLIENT_ID&redirect_uri=http://localhost:5173/auth/callback&response_type=code&scope=openid profile email`;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault(); 
    if (onSuccess) onSuccess(); 
  };

  return (
    <div className="card">
      <table className="card-table">
        <tbody>
          <tr>
            <td className="image-cell">
              <img src="/images/Zarp_Main-image-d.webp" alt="Картинка" />
            </td>
            <td className="content-cell">
              <div className="content-center">
                {!isRegistering ? (
                  <>
                    <h1>Заголовок текста</h1>
                    <p>Нажмите на кнопку ниже, чтобы перейти к регистрации.</p>
                  </>
                ) : (
                  <form className="reg-form" onSubmit={handleSubmit}>
                    <h1>Регистрация</h1>
                    <p>Создайте аккаунт для доступа к системе.</p>
                    <a href={alfaAuthLink} className="btn-submit">Войти через Альфа-Банк</a>
                  </form>
                )}
              </div>
              {!isRegistering && (
                <button type="button" className="btn" onClick={handleOpenRegistration}>
                  Подробнее
                </button>
              )}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  );
};
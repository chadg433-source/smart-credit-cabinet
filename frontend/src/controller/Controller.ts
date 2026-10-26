import { useState } from 'react';

export const useCardController = () => {
  const [isRegistering, setIsRegistering] = useState(false);

  const handleOpenRegistration = () => {
    setIsRegistering(true);
  };

  const handleCloseRegistration = () => {
    setIsRegistering(false);
  };

  return {
    isRegistering,
    handleOpenRegistration,
    handleCloseRegistration,
  };
};
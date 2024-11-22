import { useState, useEffect } from 'react';

const useSessionStatus = () => {
  const [sessionStatus, setSessionStatus] = useState(null);

  useEffect(() => {
    const checkSession = async () => {
      try {
        const response = await fetch('/api/getsession', {
          credentials: 'include', // Incluye las cookies en la solicitud
        });

        // Intenta convertir la respuesta a JSON siempre
        const data = await response.json();
        console.log('Datos de la respuesta JSON:', data);

        if (response.ok) {
          if (data.status === 'OK') {
            setSessionStatus('OK');
          }
        } else {
          setSessionStatus('Unauthorized');
        }
      } catch (error) {
        console.error("Error al verificar la sesión:", error);
        setSessionStatus('Unauthorized');
      }
    };

    checkSession();
  }, []);

  return sessionStatus;
};

export default useSessionStatus;

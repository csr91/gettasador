import { useState, useEffect } from 'react';

const useSessionStatus = () => {
  const [sessionStatus, setSessionStatus] = useState(null);
  const [prestock, setPrestock] = useState(null);

  useEffect(() => {
    const checkSession = async () => {
      try {
        const response = await fetch('/api/getsession', {
          credentials: 'include', // Incluye las cookies en la solicitud
        });

        const data = await response.json();
        console.log('Datos de la respuesta JSON:', data);

        if (response.ok) {
          if (data.status === 'OK') {
            setSessionStatus('OK');
            setPrestock(data.prestock); // Guarda la información de prestock
          }
        } else {
          setSessionStatus('Unauthorized');
          setPrestock(null); // Limpia prestock si no está autorizado
        }
      } catch (error) {
        console.error('Error al verificar la sesión:', error);
        setSessionStatus('Unauthorized');
        setPrestock(null); // Limpia prestock en caso de error
      }
    };

    checkSession();
  }, []);

  return { sessionStatus, prestock }; // Devuelve ambos estados
};

export default useSessionStatus;

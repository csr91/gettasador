import { useState, useEffect } from 'react';

const useSessionStatus = () => {
  const [sessionStatus, setSessionStatus] = useState(null);

  useEffect(() => {
    const checkSession = async () => {
      try {
        const response = await fetch('/api/getsession', {
          credentials: 'include', // Incluye las cookies en la solicitud
        });
        if (response.ok) {
          const data = await response.json();
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




import { useState, useEffect } from 'react';

const useSessionStatus = () => {
  const [sessionStatus, setSessionStatus] = useState('OK'); // Inicializado como 'OK'

  useEffect(() => {
    // Desactiva temporalmente la lógica para pruebas
    /*
    const checkSession = async () => {
      try {
        const response = await fetch('/api/getsession', {
          credentials: 'include', // Incluye las cookies en la solicitud
        });
        if (response.ok) {
          const data = await response.json();
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
    */
  }, []);

  return sessionStatus;
};

export default useSessionStatus;

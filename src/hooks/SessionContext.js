import { createContext, useContext, useState, useEffect } from 'react';

// Crear el contexto
const SessionContext = createContext();

// Proveedor del contexto
export const SessionProvider = ({ children }) => {
  const [sessionStatus, setSessionStatus] = useState(null);
  const [prestock, setPrestock] = useState(null);

  useEffect(() => {
    const checkSession = async () => {
      try {
        const response = await fetch('/api/getsession', {
          credentials: 'include',
        });

        const data = await response.json();

        if (response.ok && data.status === 'OK') {
          setSessionStatus('OK');
          setPrestock(data.prestock);
          console.log('Datos de la respuesta JSON:', data.prestock);
        } else {
          setSessionStatus('Unauthorized');
          setPrestock(data.prestock);
        }
      } catch (error) {
        console.error('Error al verificar la sesión:', error);
        setSessionStatus('Unauthorized');
        setPrestock(0);
      }
    };

    checkSession();
  }, []);

  return (
    <SessionContext.Provider value={{ sessionStatus, prestock }}>
      {children}
    </SessionContext.Provider>
  );
};

// Hook para consumir el contexto
export const useSession = () => useContext(SessionContext);

import React, { useEffect } from "react";
import { useSession } from "../hooks/SessionContext"; // Importar el hook para usar el contexto
import Calc from "./Calc"; // Componente para no autenticados
import CalcFull from "./Calcfull"; // Componente para usuarios autenticados
import "../styles/CalcSplit.css";

const CalcSplit = () => {
  const { sessionStatus, prestock } = useSession(); // Obtener el estado de sesión y el valor de prestock

  // Función para hacer el POST
  const handlePostRequest = async () => {
    try {
      const response = await fetch('/api/consumo_prestock', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prestock }) // Enviamos prestock como dato
      });

      if (response.ok) {
        const data = await response.json();
        console.log("Respuesta del servidor:", data);
      } else {
        console.error("Error en la solicitud POST");
      }
    } catch (error) {
      console.error("Error al hacer la solicitud:", error);
    }
  };

  // Usamos useEffect para asegurarnos de que el log se ejecute una vez que los valores del contexto estén disponibles
  useEffect(() => {
    console.log("Contexto de sesión:", { sessionStatus, prestock });
  }, [sessionStatus, prestock]);

  return (
    <div className="split-screen">
      <div className="left-section">
        {/* Lógica de decisión para mostrar CalcFull o Calc */}
        {sessionStatus === "OK" || prestock === 1 ? (
          <CalcFull /> // Muestra CalcFull si está autenticado o prestock es 1
        ) : (
          <Calc /> // Muestra Calc si no está autenticado y prestock es 0
        )}
        
        {/* Botón para hacer el POST */}
        <button onClick={handlePostRequest}>Enviar Consumo</button>
      </div>
      <div className="right-section">
        <h1>Hola</h1>
      </div>
    </div>
  );
};

export default CalcSplit;

import React, { useEffect, useState } from "react";
import { useSession } from "../hooks/SessionContext";
import Calc from "./Calc";
import CalcFull from "./Calcfull";
import "../styles/CalcSplit.css";

const CalcSplit = () => {
  const { sessionStatus, prestock } = useSession();
  const [respuesta, setRespuesta] = useState(null); // Estado para almacenar la respuesta de la API

  const handlePostRequest = async () => {
    try {
      const response = await fetch("/api/consumo_prestock", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ prestock }),
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

  useEffect(() => {
    console.log("Contexto de sesión:", { sessionStatus, prestock });
  }, [sessionStatus, prestock]);

  return (
    <div className="split-screen">
      <div className="left-section">
        {/* Renderiza CalcFull o Calc según el estado de sesión */}
        {sessionStatus === "OK" || prestock === 1 ? (
          <CalcFull setRespuesta={setRespuesta} /> // Pasamos setRespuesta como prop
        ) : (
          <Calc setRespuesta={setRespuesta} /> // Pasamos setRespuesta también aquí
        )}
      </div>
      <div className="right-section">
        {/* Renderiza la respuesta en la sección derecha */}
        {respuesta ? (
          <div>
            <h4>Resultados del Servidor:</h4>
            <p>{respuesta.mensaje}</p>
            <p>
              <strong>Precio promedio por m²:</strong>{" "}
              {respuesta.m2price_average.toFixed(2)}
            </p>
            <p>
              <strong>Cantidad de resultados:</strong> {respuesta.m2price_count}
            </p>
            <p>
              <strong>Mapa:</strong>{" "}
              <a
                href={respuesta.map_url}
                target="_blank"
                rel="noopener noreferrer"
              >
                Ver en Google Maps
              </a>
            </p>
          </div>
        ) : (
          <div></div>
        )}
      </div>
    </div>
  );
};

export default CalcSplit;

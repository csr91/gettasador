import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import LoadingSpinner from './LoadingSpinner'; // Asegúrate de que el archivo del spinner esté en la carpeta 'componentes'
import '../styles/Calc.css';

function Calcfull({ setRespuesta }) {
  const [direccion, setDireccion] = useState("");
  const [metros, setMetros] = useState("");
  const [tipoInmueble, setTipoInmueble] = useState("DEPARTAMENTO");
  const [superficieM2, setSuperficieM2] = useState("50");
  const [ambientes, setAmbientes] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [apiSuccess, setApiSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    const requestBody = {
      direccion,
      roundmeters: metros ? parseInt(metros) : 50,
      tipoInmueble,
      m2property: parseFloat(superficieM2),
      ambientes: parseInt(ambientes),
    };

    try {
      const response = await fetch("/api/in_calc", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const result = await response.json();
      setRespuesta(result); // Actualizamos el estado en CalcSplit
      setApiSuccess(true); // Indicamos que la API respondió correctamente
    } catch (error) {
      console.error("Error in API call:", error);
      setRespuesta({ error: "Hubo un error en la solicitud." });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container">
      <h2>Formulario de Propiedad Full</h2>
      <form onSubmit={handleSubmit}>
        {/* Campos del formulario */}
        <div className="form-group">
          <label htmlFor="tipoInmueble">Tipo de Inmueble:</label>
          <select
            id="tipoInmueble"
            value={tipoInmueble}
            onChange={(e) => setTipoInmueble(e.target.value)}
            disabled={isLoading || apiSuccess}
          >
            <option value="DEPARTAMENTO">Departamento</option>
            <option value="CASA">Casa</option>
            <option value="PH">PH</option>
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="direccion">Dirección:</label>
          <input
            type="text"
            id="direccion"
            value={direccion}
            onChange={(e) => setDireccion(e.target.value)}
            placeholder="Ingrese la dirección"
            disabled={isLoading || apiSuccess}
          />
        </div>
        <div className="form-group">
          <label htmlFor="superficieM2">Superficie M2:</label>
          <input
            type="number"
            id="superficieM2"
            value={superficieM2}
            onChange={(e) => setSuperficieM2(e.target.value)}
            placeholder="Ingrese la superficie en m²"
            disabled={isLoading || apiSuccess}
          />
        </div>
        <div className="form-group">
          <label htmlFor="ambientes">Ambientes:</label>
          <input
            type="number"
            id="ambientes"
            value={ambientes}
            onChange={(e) => setAmbientes(e.target.value)}
            placeholder="Ingrese la cantidad de ambientes"
            disabled={isLoading || apiSuccess}
          />
        </div>
        <div className="form-group">
          <label htmlFor="metros">Rango de Búsqueda:</label>
          <select
            id="metros"
            value={metros}
            onChange={(e) => setMetros(e.target.value)}
            disabled={isLoading || apiSuccess}
          >
            <option value="50">50 metros</option>
            <option value="100">100 metros</option>
            <option value="150">150 metros</option>
            <option value="200">200 metros</option>
          </select>
        </div>

        {/* Botón de envío y mensaje */}
        {!apiSuccess ? (
          <>
            {isLoading && (
              <div className="spinner-container">
                <LoadingSpinner />
                <p>Estamos valuando tu propiedad</p>
              </div>
            )}
            {!isLoading && (
              <button type="submit">
                Calcular
              </button>
            )}
          </>
        ) : (
          <p>
            Perfecto, ya puedes ver tus resultados!
            <br />
            Para generar otra valuación, haz click{" "}
            <span
              className="redirect-link"
              onClick={() => window.location.reload()}
              style={{ color: "blue", textDecoration: "underline", cursor: "pointer" }}
            >
              aquí
            </span>.
          </p>
        )}
      </form>
    </div>
  );
}

export default Calcfull;
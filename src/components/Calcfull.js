import React, { useState } from 'react';
import '../styles/Calc.css';

function Calcfull() {
  const [direccion, setDireccion] = useState('');
  const [metros, setMetros] = useState('');
  const [tipoInmueble, setTipoInmueble] = useState('DEPARTAMENTO');
  const [superficieM2, setSuperficieM2] = useState('50');
  const [ambientes, setAmbientes] = useState('');
  const [respuesta, setRespuesta] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();

    const requestBody = {
      direccion,
      roundmeters: metros ? parseInt(metros) : 50,
      tipoInmueble,
      m2property: parseFloat(superficieM2),
      ambientes: parseInt(ambientes),
    };

    try {
      const response = await fetch('/api/in_calc', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const result = await response.json();
      setRespuesta(result);
    } catch (error) {
      console.error('Error in API call:', error);
      setRespuesta({ error: 'Hubo un error en la solicitud.' });
    }
  };

  return (
    <div className="container">
      <h2>Formulario de Propiedad Full</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="tipoInmueble">Tipo de Inmueble:</label>
          <select
            id="tipoInmueble"
            value={tipoInmueble}
            onChange={(e) => setTipoInmueble(e.target.value)}
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
          />
        </div>
        <div className="form-group">
          <label htmlFor="metros">Rango de Búsqueda:</label>
          <select
            id="metros"
            value={metros}
            onChange={(e) => setMetros(e.target.value)}
          >
            <option value="50">50 metros</option>
            <option value="100">100 metros</option>
            <option value="150">150 metros</option>
            <option value="200">200 metros</option>
          </select>
        </div>
        <button type="submit">Enviar</button>
      </form>
      {respuesta && (
        <div className="response">
          {respuesta.error ? (
            <p>Error: {respuesta.error}</p>
          ) : (
            <div>
              <h4>Resultados del Servidor:</h4>
              <p>{respuesta.mensaje}</p>
              <p>
                <strong>Precio promedio por m²:</strong>{' '}
                {respuesta.m2price_average.toFixed(2)}
              </p>
              <p>
                <strong>Cantidad de resultados:</strong>{' '}
                {respuesta.m2price_count}
              </p>
              <p>
                <strong>Mapa:</strong>{' '}
                <a
                  href={respuesta.map_url}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Ver en Google Maps
                </a>
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default Calcfull;

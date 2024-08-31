import React, { useState } from 'react';

function Home() {
  const [direccion, setDireccion] = useState('');
  const [metros, setMetros] = useState('');
  const [tipoInmueble, setTipoInmueble] = useState('DEPARTAMENTO');
  const [superficieM2, setSuperficieM2] = useState('');
  const [ambientes, setAmbientes] = useState('');
  const [respuesta, setRespuesta] = useState(null);  // Estado para almacenar la respuesta completa

  const handleSubmit = async (e) => {
    e.preventDefault();

    const requestBody = {
      direccion: direccion,
      roundmeters: parseInt(metros),
      tipoInmueble: tipoInmueble,
      m2property: parseFloat(superficieM2),
      ambientes: parseInt(ambientes),
    };

    try {
      const response = await fetch('/api/in_calc', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const result = await response.json();
      setRespuesta(result);  // Guardar la respuesta completa en el estado
    } catch (error) {
      console.error('Error in API call:', error);
      setRespuesta({ error: 'Hubo un error en la solicitud.' });
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '500px', margin: 'auto' }}>
      <h2>Formulario de Propiedad</h2>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '10px' }}>
          <label htmlFor="tipoInmueble">Tipo de Inmueble:</label>
          <select
            id="tipoInmueble"
            value={tipoInmueble}
            onChange={(e) => setTipoInmueble(e.target.value)}
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
          >
            <option value="DEPARTAMENTO">Departamento</option>
            <option value="CASA">Casa</option>
            <option value="PH">PH</option>
          </select>
        </div>
        <div style={{ marginBottom: '10px' }}>
          <label htmlFor="direccion">Dirección:</label>
          <input
            type="text"
            id="direccion"
            value={direccion}
            onChange={(e) => setDireccion(e.target.value)}
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
            placeholder="Ingrese la dirección"
          />
        </div>
        <div style={{ marginBottom: '10px' }}>
          <label htmlFor="superficieM2">Superficie M2:</label>
          <input
            type="number"
            id="superficieM2"
            value={superficieM2}
            onChange={(e) => setSuperficieM2(e.target.value)}
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
            placeholder="Ingrese la superficie en m²"
          />
        </div>
        <div style={{ marginBottom: '10px' }}>
          <label htmlFor="ambientes">Ambientes:</label>
          <input
            type="number"
            id="ambientes"
            value={ambientes}
            onChange={(e) => setAmbientes(e.target.value)}
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
            placeholder="Ingrese la cantidad de ambientes"
          />
        </div>
        <div style={{ marginBottom: '10px' }}>
          <label htmlFor="metros">Rango de Búsqueda:</label>
          <select
            id="metros"
            value={metros}
            onChange={(e) => setMetros(e.target.value)}
            style={{ width: '100%', padding: '8px', marginTop: '5px' }}
          >
            <option value="50">50 metros</option>
            <option value="100">100 metros</option>
            <option value="150">150 metros</option>
            <option value="200">200 metros</option>
          </select>
        </div>
        <button type="submit" style={{ padding: '10px 20px' }}>
          Enviar
        </button>
      </form>
      {respuesta && (
        <div style={{ marginTop: '20px', padding: '10px', backgroundColor: '#f0f0f0' }}>
          {respuesta.error ? (
            <p>Error: {respuesta.error}</p>
          ) : (
            <div>
              <h4>Resultados del Servidor:</h4>
              <p>{respuesta.mensaje}</p>
              <p><strong>Precio promedio por m²:</strong> {respuesta.m2price_average.toFixed(2)}</p>
              <p><strong>Cantidad de resultados:</strong> {respuesta.m2price_count}</p>
              <p><strong>Mapa:</strong> <a href={respuesta.map_url} target="_blank" rel="noopener noreferrer">Ver en Google Maps</a></p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default Home;
import React, { useState } from 'react';
import '../styles/CrearBusqueda.css';

function CrearBusqueda() {
  const [puesto, setPuesto] = useState('');
  const [empresa, setEmpresa] = useState('');
  const [seniority, setSeniority] = useState('');
  const [candidatos, setCandidatos] = useState('');
  const [status, setStatus] = useState('');
  const [fechaLimite, setFechaLimite] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Construir el objeto de datos para enviar al backend
    const busquedaData = {
      JobTitle: puesto,
      Employeer: empresa,
      Señority: seniority,
      FechaCierre: fechaLimite,
      Description: status,
      Status: 'Inicial', // Puedes cambiar este valor según tu lógica
    };

    try {
      const response = await fetch('/api/crear_busqueda', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Incluye cookies de sesión si es necesario
        body: JSON.stringify(busquedaData),
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Búsqueda creada exitosamente:', result);
      } else {
        console.error('Error al crear la búsqueda');
      }
    } catch (error) {
      console.error('Error en la solicitud:', error);
    }
  };

  return (
    <form id="crear-form" onSubmit={handleSubmit}>
      <div className="crear-form-header">
        <h3>Crear Búsqueda</h3>
      </div>
      <div className="form-container">
        <div className="form-left">
          <input
            type="text"
            placeholder="Job Title"
            value={puesto}
            onChange={(e) => setPuesto(e.target.value)}
            required
          />
          <input
            type="text"
            placeholder="Empresa"
            value={empresa}
            onChange={(e) => setEmpresa(e.target.value)}
            required
          />
          <div>Señority</div>
          <select
            value={seniority}
            onChange={(e) => setSeniority(e.target.value)}
            required
          >
            <option value="" disabled>
              Seleccione seniority
            </option>
            <option value="Junior">Junior</option>
            <option value="Semi-Senior">Semi-Senior</option>
            <option value="Senior">Senior</option>
            <option value="Specialist">Specialist</option>
            <option value="Coordinator">Coordinator</option>
            <option value="Leader">Leader</option>
            <option value="Manager">Manager</option>
            <option value="Director">Director</option>
          </select>
          <div>Fecha de cierre (Estimada)</div>
          <input
            type="date"
            placeholder="Fecha Límite"
            value={fechaLimite}
            onChange={(e) => setFechaLimite(e.target.value)}
            required
          />
        </div>
        <div className="form-right">
          <textarea
            placeholder="Description"
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            required
          />
        </div>
      </div>
      <div className="crear-button-container">
        <button id="crear-busqueda-button" type="submit">
          Crear Búsqueda
        </button>
      </div>
    </form>
  );
}

export default CrearBusqueda;

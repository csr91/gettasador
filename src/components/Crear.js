import React, { useState } from 'react';
import CrearBusqueda from './CrearBusqueda';
import CrearCandidato from './CrearCandidato';
import '../styles/Crear.css';

function Crear() {
  const [message, setMessage] = useState('');
  const [showButtons, setShowButtons] = useState(true);
  const [isBuscador, setIsBuscador] = useState(null); // Estado para saber cuál formulario mostrar

  const handleCrearBusqueda = () => {
    setIsBuscador(true);
    setMessage('');
    setShowButtons(false);
  };

  const handleCrearCandidato = () => {
    setIsBuscador(false);
    setMessage('');
    setShowButtons(false);
  };

  return (
    <div className='crear-container'>      
      <div className='crear-title-container'>
        <h2>Crear</h2>
      </div>
      {showButtons ? (
        <div className="crear-buttonContainer">
          <div className='crear-box'>
          <button onClick={handleCrearBusqueda}>
              Crear Búsqueda
            </button>
            <ul>
              <li>Definir el puesto y la descripción.</li>
              <li>Establecer el Señority requerido.</li>
              <li>Asociar candidatos a la búsqueda.</li>
              <li>Definir el status de la búsqueda.</li>
              <li>Establecer fechas límite.</li>
              <li>Generar reportes sobre el progreso.</li>
            </ul>
          </div>
          <div>
            <button onClick={handleCrearCandidato}>
              Crear Candidato
            </button>
            <ul >
              <li>Ingresar información personal.</li>
              <li>Añadir datos de contacto.</li>
              <li>Definir la experiencia y habilidades.</li>
              <li>Asociar a una búsqueda específica.</li>
              <li>Establecer el stage del candidato.</li>
              <li>Cargar un CV o documento relevante.</li>
            </ul>
          </div>
        </div>
      ) : (
        <div>
          {isBuscador ? <CrearBusqueda /> : <CrearCandidato />}
        </div>
      )}
      {message && <div className="message">{message}</div>}
    </div>
  );
}

export default Crear;

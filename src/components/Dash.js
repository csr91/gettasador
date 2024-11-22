import React from 'react';
import InfoBox from './InfoBox';
import { Line } from 'react-chartjs-2';
import { Chart, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, Title } from 'chart.js';
import '../styles/Dash.css';

// Registrar las escalas y elementos necesarios
Chart.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, Title);

function Dash() {
  // Datos de ejemplo para la tabla
  const reclutadores = [
    { nombre: 'Reclutador 1', qBusquedas: 10, qIniciales: 5 },
    { nombre: 'Reclutador 2', qBusquedas: 15, qIniciales: 7 },
    { nombre: 'Reclutador 3', qBusquedas: 8, qIniciales: 4 },
    { nombre: 'Reclutador 4', qBusquedas: 12, qIniciales: 6 },
    { nombre: 'Reclutador 5', qBusquedas: 20, qIniciales: 10 },
    { nombre: 'Reclutador 6', qBusquedas: 5, qIniciales: 2 },
  ];

  // Datos del gráfico
  const chartData = {
    labels: ['Semana 1', 'Semana 2', 'Semana 3', 'Semana 4'], // Cambia las etiquetas según tus datos
    datasets: [
      {
        label: 'Búsquedas Cerradas',
        data: [5, 10, 8, 15], // Cambia estos datos según tus datos
        borderColor: 'rgba(75, 192, 192, 1)',
        backgroundColor: 'rgba(75, 192, 192, 0.4)',
        fill: true, // Para llenar el área bajo la línea
        tension: 0.4, // Para hacer la línea curva
      },
      {
        label: 'Búsquedas Creadas',
        data: [3, 5, 7, 12], // Datos de ejemplo para búsquedas creadas
        borderColor: 'rgba(255, 99, 132, 1)',
        backgroundColor: 'rgba(255, 99, 132, 0.4)',
        fill: true, // Para llenar el área bajo la línea
        tension: 0.4, // Para hacer la línea curva
      },
    ],
  };

  return (
    <div className="container">
      <div className="infoBoxContainer">
        <InfoBox title="Búsquedas Abiertas" number={20} />
        <InfoBox title="Creadas hoy" number={3} />
        <InfoBox title="Cerradas hoy" number={5} />
      </div>
      <div className="horizontalContainer">
        <div className="tableContainer">
          <h2>Reclutadores</h2>
          <table className="table">
            <thead>
              <tr>
                <th>Reclutador</th>
                <th>Q Búsquedas</th>
                <th>Q Iniciales</th>
              </tr>
            </thead>
            <tbody>
              {reclutadores.map((reclutador, index) => (
                <tr key={index}>
                  <td>{reclutador.nombre}</td>
                  <td>{reclutador.qBusquedas}</td>
                  <td>{reclutador.qIniciales}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="chartContainer">
          <h2>Búsquedas Cerradas y Creadas por Semana</h2>
          <Line data={chartData} />
        </div>
      </div>
    </div>

  );
}

export default Dash;

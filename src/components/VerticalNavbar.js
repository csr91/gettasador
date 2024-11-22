import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import '../styles/NavBar.css';
import { FaTh, FaList, FaCalculator, FaHistory, FaCog, FaSignOutAlt } from 'react-icons/fa'; // Importar íconos

function VerticalNavbar({ sessionStatus }) {
  const [isCollapsed, setIsCollapsed] = useState(false);

  const toggleNavbar = () => {
    setIsCollapsed(!isCollapsed);
  };

  const handleLogout = async () => {
    try {
      const response = await fetch('/api/logout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        window.location.reload();
      } else {
        console.error('Error al cerrar sesión');
      }
    } catch (err) {
      console.error('Hubo un error al realizar la solicitud de logout:', err);
    }
  };

  console.log('Estado de sessionStatus:', sessionStatus); // Agrega este console.log para depuración

  return (
    <div className={`navbar ${isCollapsed ? 'collapsed' : ''}`}>
      <button className="navbar-vertical-toggle" onClick={toggleNavbar}>
        {isCollapsed ? '> ' : '<'}
      </button>

      <div className="navbar-vertical">
        <div className="navbar-header">
          <h1 className="hero-navtitle">
            {isCollapsed ? 'TT' : <>GETTASADOR</>}
          </h1>
        </div>
        <div className="navbar-menu">
          <Link to="/dash" className="navbar-link">
            <button className="navbar-button">
              <FaTh className="navbar-icon" />
              {!isCollapsed && 'Dashboard'}
            </button>
          </Link>
          <Link to="/calc" className="navbar-link">
            <button className="navbar-button">
              <FaCalculator className="navbar-icon" />
              {!isCollapsed && 'Calculadora'}
            </button>
          </Link>
          <Link to="/historial" className="navbar-link">
            <button className="navbar-button">
              <FaHistory className="navbar-icon" />
              {!isCollapsed && 'Historial'}
            </button>
          </Link>
        </div>
        <div className="navbar-bottomSection">
          <Link to="/config" className="navbar-link">
            <button className="navbar-button">
              <FaCog className="navbar-icon" />
              {!isCollapsed && 'Config'}
            </button>
          </Link>
          {sessionStatus === 'OK' ? (
            <button onClick={handleLogout} className="navbar-button">
              <FaSignOutAlt className="navbar-icon" />
              {!isCollapsed && 'Cerrar Sesión'}
            </button>
          ) : (
            <Link to="/login" className="navbar-link">
              <button className="navbar-button">
                <FaSignOutAlt className="navbar-icon" />
                {!isCollapsed && 'Iniciar Sesión'}
              </button>
            </Link>
          )}
        </div>
      </div>
    </div>
  );
}

export default VerticalNavbar;
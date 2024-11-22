import React, { useState } from 'react';
import LoginPage from './LoginPage';
import '../styles/Home.css'; // Importa los estilos

const HeroSection = () => {
  const [isLoginVisible, setIsLoginVisible] = useState(false);

  const showLoginForm = () => {
    setIsLoginVisible(true);
    setTimeout(() => {
      document.getElementById('loginForm').scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  return (
    <div className='half-hero'>
      <div className="hero-container">
        <div className="hero-image">
          <div className="overlay"></div>
        </div>
        <div className="hero-content">
          <h1 className="hero-title">CALCULO INMOBILIARIO</h1>
          <p className="hero-subtitle">
          Compara con facilidad el valor de tus inmuebles.
          </p>

          <button className="hero-button" onClick={showLoginForm}>
            Ingresa
          </button>
        </div>
      </div>

      {isLoginVisible && (
        <div id="loginForm" className="login-page-container">
          <LoginPage />
        </div>
      )}
    </div>
  );
};

export default HeroSection;

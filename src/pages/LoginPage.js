import React, { useState, useEffect } from 'react';
import LoginForm from './LoginForm';
import SignupForm from './Signup';
import '../styles/LoginPage.css';
import logo from '../assets/logo3.png';
import googleLogo from '../assets/googlelogo.png'; // Importa el logo de Google
import { useGoogleLogin } from '@react-oauth/google';

function LoginPage({ onLogin }) {
  const [isSignup, setIsSignup] = useState(false);
  const [loading, setLoading] = useState(false); // Estado para el spinner
  const [isHovered, setIsHovered] = useState(false); // Estado para controlar el hover
  const [isBlurred, setIsBlurred] = useState(false); // Estado para controlar el blur fijo

  const toggleForm = () => {
    setIsSignup(!isSignup);
  };

  const login = useGoogleLogin({
    onSuccess: async (tokenResponse) => {
      console.log("Token de Google:", tokenResponse);
  
      // Enviar el token al backend para obtener el email del usuario
      setLoading(true); // Activar el loader (spinner)
      try {
        const response = await fetch('/api/sso', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ token: tokenResponse.access_token }),
        });
  
        // Verificar si la respuesta es 200
        if (response.ok) {
          console.log("Respuesta 200 recibida");
          // Refrescar la página
          window.location.reload();
        } else {
          console.log("Error en la respuesta:", response.status);
        }
      } catch (error) {
        console.error("Error en la solicitud:", error);
      } finally {
        setLoading(false); // Desactivar el loader
      }
    },
  });

  // Manejar el clic fuera del componente de Google para eliminar el blur
  useEffect(() => {
    const handleClickOutside = (event) => {
      const googleLoginElement = document.querySelector('.google-login');
      if (googleLoginElement && !googleLoginElement.contains(event.target)) {
        setIsBlurred(false); // Desactivar el blur si se hace clic fuera
      }
    };

    document.addEventListener('click', handleClickOutside);
    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  }, []);

  const handleGoogleLoginClick = () => {
    setIsBlurred(true); // Activar el blur cuando se hace clic en el logo de Google
    login(); // Iniciar el proceso de autenticación de Google
  };

  return (
    <div className="login-container">
      <img src={logo} alt="Logo" className="logo" />
      <div className={`form-section ${isBlurred || isHovered ? 'blurred' : ''}`}>
        {isSignup ? (
          <SignupForm />
        ) : (
          <LoginForm toggleForm={toggleForm} onLogin={onLogin} />
        )}
        <p>
          {isSignup ? '¿Ya tienes cuenta?' : '¿No tienes cuenta?'}
          <span onClick={toggleForm} style={{ cursor: 'pointer', color: 'blue' }}>
            {isSignup ? ' Inicia sesión' : ' Regístrate'}
          </span>
        </p>
      </div>

      {/* Botón de inicio de sesión con Google */}
      <div 
        className="google-login" 
        onClick={handleGoogleLoginClick} // Llamar a la función que maneja el clic
        style={{ cursor: 'pointer' }}
        onMouseEnter={() => setIsHovered(true)} // Activar el difuminado al pasar el mouse
        onMouseLeave={() => setIsHovered(false)} // Desactivar el difuminado cuando el mouse sale
      >
        {loading ? (
          <div className="spinner"></div> // Spinner
        ) : (
          <img src={googleLogo} alt="Iniciar sesión con Google" className="google-logo" />
        )}
      </div>
    </div>
  );
}

export default LoginPage;

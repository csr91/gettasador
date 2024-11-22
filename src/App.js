// App.js
import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate, useLocation } from 'react-router-dom';
import { GoogleOAuthProvider } from '@react-oauth/google'; // Importa GoogleOAuthProvider
import VerticalNavbar from './components/VerticalNavbar';
import MainComponent from './components/MainComponent';
import Dash from './components/Dash';
import CalcSplit from './components/Calculadora';
import Crear from './components/Crear';
import LoginPage from './pages/LoginPage';
import HeroSection from './pages/HeroSection';
import useSessionStatus from './hooks/useSessionCookie';
import LoadingSpinner from './components/LoadingSpinner';
import './App.css';

function App() {
  const sessionStatus = useSessionStatus(); // Verificar el estado de la sesión
  const location = useLocation();

  return (
    <div className='App'>
      <VerticalNavbar sessionStatus={sessionStatus} /> {/* Pasar sessionStatus */}
      <div className='main'>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<LoginPage />} />
          <Route path="/" element={<Navigate to="/dash" />} />
          <Route path="/home" element={<Dash />} />
          <Route path="/main" element={<MainComponent />} />
          <Route path="/dash" element={<Dash />} />
          <Route path="/calc" element={<CalcSplit />} />
          <Route path="/crear" element={<Crear />} />
        </Routes>
      </div>
    </div>
  );
}

const styles = {
  app: {
    display: 'flex',
    height: '100vh',
  },
};

// Envuelve App con GoogleOAuthProvider y pasa el clientId
const AppWithRouter = () => (
  <GoogleOAuthProvider clientId="287020706596-hu46b8tf65fpma6ai15ik281nb6bdgkp.apps.googleusercontent.com">
    <Router>
      <App />
    </Router>
  </GoogleOAuthProvider>
);

export default AppWithRouter;
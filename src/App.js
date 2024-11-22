import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import { GoogleOAuthProvider } from '@react-oauth/google';
import VerticalNavbar from './components/VerticalNavbar';
import MainComponent from './components/MainComponent';
import Dash from './components/Dash';
import Calculadora from './components/Calculadora';
import Crear from './components/Crear';
import LoginPage from './pages/LoginPage';
import { SessionProvider, useSession } from './hooks/SessionContext'; // Importa el contexto y el hook
import './App.css';

// Componente para manejar la redirección
const ProtectedRoute = ({ children }) => {
  const { sessionStatus } = useSession(); // Obtén el estado de la sesión

  // Si el usuario está autenticado, redirige a /dash
  if (sessionStatus === "OK") {
    return <Navigate to="/dash" />;
  }

  return children; // Si no está autenticado, renderiza los hijos (login/signup)
};

function App() {
  return (
    <div className="App">
      <VerticalNavbar />
      <div className="main">
        <Routes>
          {/* Redirigir a /dash si el usuario ya está autenticado */}
          <Route 
            path="/login" 
            element={
              <ProtectedRoute>
                <LoginPage />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/signup" 
            element={
              <ProtectedRoute>
                <LoginPage />
              </ProtectedRoute>
            } 
          />
          <Route path="/" element={<Navigate to="/dash" />} />
          <Route path="/home" element={<Dash />} />
          <Route path="/main" element={<MainComponent />} />
          <Route path="/dash" element={<Dash />} />
          <Route path="/calc" element={<Calculadora />} />
          <Route path="/crear" element={<Crear />} />
        </Routes>
      </div>
    </div>
  );
}

const AppWithRouter = () => (
  <GoogleOAuthProvider clientId="287020706596-hu46b8tf65fpma6ai15ik281nb6bdgkp.apps.googleusercontent.com">
    <Router>
      <SessionProvider>
        <App />
      </SessionProvider>
    </Router>
  </GoogleOAuthProvider>
);

export default AppWithRouter;

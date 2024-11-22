import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // Para redirigir

function SignupForm() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);  // Estado para el loader
  const [error, setError] = useState(null); // Estado para el mensaje de error
  const [isSubmitted, setIsSubmitted] = useState(false); // Estado para manejar la vista después del registro
  const [confirmationMessage, setConfirmationMessage] = useState(''); // Estado para el mensaje de confirmación
  const navigate = useNavigate(); // Hook para redirigir

  const handleSubmit = async (event) => {
    event.preventDefault(); // Evita el comportamiento predeterminado del formulario

    // Limpiar el mensaje de error antes de cada intento
    setError(null);

    // Verificar si las contraseñas coinciden
    if (password !== confirmPassword) {
      alert("Las contraseñas no coinciden");
      return;
    }

    // Crear el objeto con los datos a enviar
    const data = {
      correo: username,
      contraseña: password
    };

    setLoading(true); // Activar el loader

    try {
      // Realizar la solicitud fetch al endpoint /api/registro
      const response = await fetch('/api/registro', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Registro exitoso:', result);
        // Cambiar el estado para mostrar el mensaje de confirmación
        setIsSubmitted(true);
        setConfirmationMessage(`Gracias! Hemos enviado un correo de confirmación a la casilla ${username} para confirmar tu cuenta.`);
        
        // Esperar 5 segundos antes de recargar la página
        setTimeout(() => {
          window.location.reload(); // Recargar la página
        }, 5000);
      } else {
        const errorData = await response.json();
        if (response.status === 409) {
          // Si el error es 409, mostrar mensaje específico para correo ya registrado
          setError('Correo ya registrado');
        } else {
          setError(errorData.message || 'Hubo un error al registrar'); // Establecer mensaje de error
        }
      }
    } catch (error) {
      console.error('Error de red:', error);
      setError('Error de red: No se pudo conectar al servidor');
    } finally {
      setLoading(false); // Desactivar el loader
    }
  };

  return (
    <div className='full'>
      {/* Si el formulario no ha sido enviado, mostrarlo */}
      {!isSubmitted ? (
        <form onSubmit={handleSubmit}>
          <div className="form-group1">
            <label htmlFor="newUsername">Usuario</label>
            <input
              type="text"
              id="newUsername"
              placeholder="Ingrese su usuario"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>

          <div className="form-group1">
            <label htmlFor="newPassword">Contraseña</label>
            <input
              type="password"
              id="newPassword"
              placeholder="Ingrese su contraseña"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <div className="form-group1">
            <label htmlFor="confirmPassword">Confirmar Contraseña</label>
            <input
              type="password"
              id="confirmPassword"
              placeholder="Confirme su contraseña"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />
          </div>

          <div className="form-group1">
            {/* Mostrar el loader si está cargando */}
            {loading && <div className="spinner2"></div>}

            {/* Mostrar el botón y manejar su visibilidad */}
            <button
              className='login-button'
              type="submit"
              style={{ visibility: loading ? 'hidden' : 'visible' }}
              disabled={loading} // Deshabilitar el botón mientras se carga
            >
              {loading ? 'Cargando...' : 'Crear Cuenta'}
            </button>
            
            {/* Mostrar mensaje de error si existe */}
            {error && <p style={{ color: 'red' }}>{error}</p>}
          </div>
        </form>
      ) : (
        // Si el formulario ha sido enviado, mostrar el mensaje de confirmación
        <p style={{ color: 'green' }}>{confirmationMessage}</p>
      )}
    </div>
  );
}

export default SignupForm;
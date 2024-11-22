import React, { useState } from 'react';

function LoginForm({ toggleForm, onLogin }) {
  const [correo, setCorreo] = useState('');
  const [contraseña, setContraseña] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(''); // Limpiar el error anterior

    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ correo, contraseña }),
      });

      if (response.ok) {
        window.location.reload();
      } else {
        const errorData = await response.json();
        // Ajusta aquí para obtener el mensaje de error correcto
        setError(errorData.error || 'Error en el inicio de sesión');
      }
    } catch (err) {
      setError('Hubo un error con la solicitud');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="form-group1">
        <label>Correo</label>
        <input
          type="email"
          value={correo}
          onChange={(e) => setCorreo(e.target.value)}
          required
        />
      </div>
      <div className="form-group1">
        <label>Contraseña</label>
        <input
          type="password"
          value={contraseña}
          onChange={(e) => setContraseña(e.target.value)}
          required
        />
        {/* Mostrar el loader si está cargando */}
        {loading && <div className="spinner2"></div>}

        {/* Mostrar el error debajo del formulario */}
        {error && <div style={{ color: 'red', marginTop: '10px' }}>{error}</div>}
        
        <button
          className='login-button'
          type="submit"
          style={{ visibility: loading ? 'hidden' : 'visible' }}
        >
          Entrar
        </button>
      </div>
    </form>
  );
}

export default LoginForm;

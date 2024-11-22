// MainComponent.js
import React from 'react';

function MainComponent() {
  return (
    <div style={styles.main}>
      <h1>Componente Principal</h1>
      <p>Este es el contenido principal que se muestra a la derecha de la barra de navegación.</p>
    </div>
  );
}

const styles = {
  main: {
    padding: '20px',
  },
};

export default MainComponent;

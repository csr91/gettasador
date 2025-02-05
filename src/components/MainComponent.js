// MainComponent.js
import React from 'react';

function MainComponent() {
  return (
    <div style={styles.main}>
      <h1>Frame Trasa</h1>
      <iframe title="Tarjetas 2025" width="800" height="636" src="https://app.powerbi.com/view?r=eyJrIjoiNjRmMWY1MjUtOGZiNy00ZjI2LTgwZDgtZjljMmI0NzNiODEzIiwidCI6ImE2ZDNmNWMyLWYyMWYtNGIyYi04MTEwLTMxM2FmZGFhNmY0MiJ9" frameborder="0" allowFullScreen="true"></iframe>
      
    </div>
  );
}

const styles = {
  main: {
    padding: '20px',
  },
};

export default MainComponent;

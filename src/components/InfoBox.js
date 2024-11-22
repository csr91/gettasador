// InfoBox.js
import React from 'react';
import '../styles/InfoBox.css';

function InfoBox({ title, number }) {
  return (
    <div className="box">
      <h2 className="title">{title}</h2>
      <p className="number">{number}</p>
    </div>
  );
}

export default InfoBox;

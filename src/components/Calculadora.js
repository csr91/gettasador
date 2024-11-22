import React from "react";
import Calc from "./Calc";
import "../styles/CalcSplit.css";

const CalcSplit = () => {
  return (
    <div className="split-screen">
      <div className="left-section">
        <Calc />
      </div>
      <div className="right-section">
        <h1>Hola</h1>
      </div>
    </div>
  );
};

export default CalcSplit;
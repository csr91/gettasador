import React, { useState, useEffect } from "react";

function CrearCandidato() {
  const [nombre, setNombre] = useState("");
  const [apellido, setApellido] = useState("");
  const [mail, setMail] = useState("");
  const [telefono, setTelefono] = useState("");
  const [linkedin, setLinkedin] = useState("");
  const [stage, setStage] = useState("");
  const [busquedaAsociada, setBusquedaAsociada] = useState("");
  const [busquedas, setBusquedas] = useState([]);
  const [mensaje, setMensaje] = useState(null); // Estado para mostrar mensajes de éxito o error

  // Obtener las opciones de búsqueda desde la API
  useEffect(() => {
    const fetchBusquedas = async () => {
      try {
        const response = await fetch("/api/busquedalist");
        if (response.ok) {
          const data = await response.json();
          setBusquedas(data);
        } else {
          console.error("Error al obtener las búsquedas");
        }
      } catch (error) {
        console.error("Error en la solicitud:", error);
      }
    };

    fetchBusquedas();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMensaje(null);

    const candidato = {
      Nombre: nombre,
      Apellido: apellido,
      Mail: mail,
      Telefono: telefono,
      Linkedin: linkedin,
      Etapa: stage,
      BusquedaAsociada: busquedaAsociada,
      Skills: [], // Skills vacíos por ahora
    };

    try {
      const response = await fetch("/api/crear_candidato", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(candidato),
      });

      if (response.ok) {
        const data = await response.json();
        setMensaje(`Candidato creado exitosamente: ID ${data.candidato_id}`);
        // Limpiar los campos del formulario
        setNombre("");
        setApellido("");
        setMail("");
        setTelefono("");
        setLinkedin("");
        setStage("");
        setBusquedaAsociada("");
      } else {
        const errorData = await response.json();
        setMensaje(`Error: ${errorData.error}`);
      }
    } catch (error) {
      console.error("Error en la solicitud:", error);
      setMensaje("Error al enviar la solicitud. Por favor, intenta nuevamente.");
    }
  };

  return (
    <form id="crear-form" onSubmit={handleSubmit}>
      <div className="crear-form-header">
        <h3>Crear Candidato</h3>
      </div>
      <div className="form-container">
        <div className="form-left">
          <input
            type="text"
            placeholder="Nombre"
            value={nombre}
            onChange={(e) => setNombre(e.target.value)}
            required
          />
          <input
            type="text"
            placeholder="Apellido"
            value={apellido}
            onChange={(e) => setApellido(e.target.value)}
            required
          />
          <input
            type="text"
            placeholder="Mail"
            value={mail}
            onChange={(e) => setMail(e.target.value)}
            required
          />
          <input
            type="text"
            placeholder="Teléfono"
            value={telefono}
            onChange={(e) => setTelefono(e.target.value)}
            required
          />
          <input
            type="text"
            placeholder="Linkedin"
            value={linkedin}
            onChange={(e) => setLinkedin(e.target.value)}
            required
          />

          {/* Select para búsqueda asociada */}
          <select
            value={busquedaAsociada}
            onChange={(e) => setBusquedaAsociada(e.target.value)}
            required
          >
            <option value="" disabled>
              Búsqueda Asociada
            </option>
            {busquedas.map((busqueda) => (
              <option key={busqueda._id} value={busqueda._id}>
                {busqueda.Employer} - {busqueda.JobTitle}
              </option>
            ))}
          </select>

          {/* Select para etapa */}
          <select
            value={stage}
            onChange={(e) => setStage(e.target.value)}
            required
          >
            <option value="" disabled>
              Etapa
            </option>
            <option value="Hunteado">Hunteado</option>
            <option value="Entrevista Inicial">Entrevista Inicial</option>
            <option value="2da Entrevista">2da Entrevista</option>
            <option value="Ternado">Ternado</option>
            <option value="Cerrado">Cerrado</option>
          </select>
        </div>
      </div>
      <div className="crear-button-container">
        <button id="crear-busqueda-button" type="submit">
          Crear Candidato
        </button>
      </div>
      {/* Mostrar mensaje de éxito o error */}
      {mensaje && <div className="mensaje">{mensaje}</div>}
    </form>
  );
}

export default CrearCandidato;

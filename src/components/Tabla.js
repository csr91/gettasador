import React, { useState, useEffect } from 'react';
import '../styles/Tabla.css';

function Tabla() {
    const [busquedas, setBusquedas] = useState([]);
    const [candidatos, setCandidatos] = useState([]);
    const [activeBusqueda, setActiveBusqueda] = useState(null);
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);

    useEffect(() => {
        fetch(`/api/listas?page=${currentPage}&per_page=10`)
            .then((response) => response.json())
            .then((data) => {
                setBusquedas(data.busquedas || []);
                setTotalPages(data.total_pages || 1);
            })
            .catch((error) => console.error('Error fetching data:', error));
    }, [currentPage]);

    const handleBusquedaClick = (busqueda) => {
        setActiveBusqueda(busqueda._id);
        setCandidatos(busqueda.candidatos || []);
    };

    const handlePageChange = (direction) => {
        if (direction === 'prev' && currentPage > 1) {
            setCurrentPage((prev) => prev - 1);
        } else if (direction === 'next' && currentPage < totalPages) {
            setCurrentPage((prev) => prev + 1);
        }
    };

    return (
        <div className="tabla-container">
            {/* Tabla de Búsquedas */}
            <table className="tabla">
                <thead>
                    <tr>
                        <th>Job Title</th>
                        <th>Employeer</th>
                        <th>Señority</th>
                        <th>Status</th>
                        <th>Fecha Cierre</th>
                    </tr>
                </thead>
                <tbody>
                    {busquedas.length > 0 ? (
                        busquedas.map((busqueda) => (
                            <tr
                                key={busqueda._id}
                                className={activeBusqueda === busqueda._id ? 'active-row' : ''}
                                onClick={() => handleBusquedaClick(busqueda)}
                            >
                                <td>{busqueda.JobTitle}</td>
                                <td>{busqueda.Employer}</td>
                                <td>{busqueda.Señority}</td>
                                <td>{busqueda.Status}</td>
                                <td>{busqueda.FechaCierre}</td>
                            </tr>
                        ))
                    ) : (
                        <tr>
                            <td colSpan="5">No se encontraron resultados</td>
                        </tr>
                    )}
                </tbody>
            </table>

            <div className="paginador">
                <button
                    onClick={() => handlePageChange('prev')}
                    disabled={currentPage === 1}
                >
                    Anterior
                </button>
                <span>Página {currentPage} de {totalPages}</span>
                <button
                    onClick={() => handlePageChange('next')}
                    disabled={currentPage === totalPages}
                >
                    Siguiente
                </button>
            </div>

            {/* Tabla de Candidatos */}
            {activeBusqueda && candidatos.length > 0 && (
                <table className="tabla">
                    <thead>
                        <tr>
                            <th>Nombre</th>
                            <th>Apellido</th>
                            <th>Etapa</th>
                            <th>Email</th>
                            <th>Teléfono</th>
                            <th>LinkedIn</th>
                        </tr>
                    </thead>
                    <tbody>
                        {candidatos.map((candidato) => (
                            <tr key={candidato._id}>
                                <td>{candidato.Nombre}</td>
                                <td>{candidato.Apellido}</td>
                                <td>{candidato.Etapa}</td>
                                <td>{candidato.Mail}</td>
                                <td>{candidato.Telefono}</td>
                                <td>
                                    <a href={candidato.Linkedin} target="_blank" rel="noopener noreferrer">
                                        LinkedIn
                                    </a>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
}

export default Tabla;

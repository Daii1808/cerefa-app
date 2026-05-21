import React, { useState, useEffect } from 'react';
import { guardarEvento, obtenerEventos } from './supabaseService';
import logoCerefa from './assets/logo.jpg';

function App() {
  const diccionarioAnimales = {
    'PATO JERGÓN': { cientifico: 'Anas georgica', categoria: 'Aves', destino: 'Rehabilitación' },
    'GARZA GRANDE': { cientifico: 'Ardea alba', categoria: 'Aves', destino: 'Clínica' },
    'BANDURRIA': { cientifico: 'Theristicus melanopis', categoria: 'Aves', destino: 'Rehabilitación' },
    'PEUCO': { cientifico: 'Parabuteo unicinctus', categoria: 'Rapaces', destino: 'Liberación' },
  };

  const [tipoEvento, setTipoEvento] = useState('Ingreso');
  const [nombreComun, setNombreComun] = useState('');
  const [nombreCientifico, setNombreCientifico] = useState('');
  const [cantidad, setCantidad] = useState(1);
  const [observacion, setObservacion] = useState('');
  const [registros, setRegistros] = useState([]);
  const [estaAutenticado, setEstaAutenticado] = useState(false);

  useEffect(() => {
    async function cargarDatos() {
      try {
        const datos = await obtenerEventos();
        setRegistros(datos || []);
      } catch (error) {
        console.error("Error al cargar eventos:", error);
      }
    }
    cargarDatos();
  }, []);

  useEffect(() => {
    if (nombreComun && diccionarioAnimales[nombreComun]) {
      setNombreCientifico(diccionarioAnimales[nombreComun].cientifico);
    } else {
      setNombreCientifico('');
    }
  }, [nombreComun]);

  const handleGuardar = async (e) => {
    e.preventDefault();
    if (!nombreComun) return alert('Selecciona una especie.');
    const nuevoEvento = {
      tipo: tipoEvento,
      especie: nombreComun,
      cientifico: nombreCientifico,
      cantidad: parseInt(cantidad),
      observacion: observacion || 'Sin observaciones',
      fecha: new Date().toISOString().split('T')[0]
    };
    try {
      await guardarEvento(nuevoEvento);
      const datosActualizados = await obtenerEventos();
      setRegistros(datosActualizados);
      setNombreComun('');
      setObservacion('');
      setCantidad(1);
    } catch (error) {
      alert("Error al guardar en la base de datos.");
    }
  };

  const manejarLogin = (e) => {
    e.preventDefault();
    setEstaAutenticado(true);
  };

  return (
    <div>
      {!estaAutenticado ? (
        <div className="login-container">
          <form onSubmit={manejarLogin} className="panel-oscuro" style={{ width: '400px', textAlign: 'center' }}>
            <div style={{ marginBottom: '25px' }}>
              <h2 style={{ color: '#00875f', fontSize: '24px', marginBottom: '5px' }}>Acceso CEREFA</h2>
              <p style={{ color: '#9ca3af', fontSize: '14px' }}>Ingresa tus credenciales médicas</p>
            </div>
            
            <label style={{ display: 'block', textAlign: 'left', marginBottom: '8px' }}>CORREO ELECTRÓNICO</label>
            <input type="email" placeholder="ejemplo@uss.cl" className="input-cerefa" style={{width: '100%', marginBottom: '15px'}} />
            
            <label style={{ display: 'block', textAlign: 'left', marginBottom: '8px' }}>CONTRASEÑA</label>
            <input type="password" placeholder="********" className="input-cerefa" style={{width: '100%', marginBottom: '20px'}} />
            
            <button type="submit" className="btn-guardar" style={{width: '100%'}}>Iniciar Sesión</button>
          </form>
        </div>
      ) : (
        <main>
          <header className="cabecera-cerefa">
            <img src={logoCerefa} alt="Logo CEREFA" className="marcador-logo" />  
            <h1 className="titulo-plataforma">Plataforma CEREFA</h1>
            <p className="subtitulo-plataforma">Centro de Rehabilitación de Fauna Silvestre</p>
          </header>

          <div className="contenido-principal">
            <form onSubmit={handleGuardar} className="panel-oscuro">
              <h2>Nuevo Evento</h2>
              <div className="fila-formulario">
                <div className="grupo-campo">
                  <label>Tipo de Evento</label>
                  <div className="flex-botones">
                    <button type="button" onClick={() => setTipoEvento('Ingreso')} className={`btn-tipo ${tipoEvento === 'Ingreso' ? 'activo-ingreso' : ''}`}>+ Ingreso</button>
                    <button type="button" onClick={() => setTipoEvento('Egreso')} className={`btn-tipo ${tipoEvento === 'Egreso' ? 'activo-egreso' : ''}`}>- Egreso</button>
                  </div>
                </div>
                <div className="grupo-campo">
                  <label>Nombre Común</label>
                  <select value={nombreComun} onChange={(e) => setNombreComun(e.target.value)} className="select-cerefa">
                    <option value="">-- Selecciona --</option>
                    {Object.keys(diccionarioAnimales).map(animal => <option key={animal} value={animal}>{animal}</option>)}
                  </select>
                </div>
                <div className="grupo-campo">
                  <label>Nombre Científico</label>
                  <input type="text" value={nombreCientifico} disabled className="input-cerefa input-deshabilitado" />
                </div>
                <div className="grupo-campo">
                   <label>Cant.</label>
                   <input type="number" value={cantidad} onChange={(e) => setCantidad(e.target.value)} min="1" className="input-cerefa" />
                </div>
              </div>
              <div className="fila-formulario" style={{ alignItems: 'flex-end' }}>
                <div className="grupo-campo" style={{ gridColumn: 'span 2', display: 'flex', flexDirection: 'row', gap: '15px', alignItems: 'flex-end' }}>
                  <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                    <label>Observación</label>
                    <input type="text" value={observacion} onChange={(e) => setObservacion(e.target.value)} placeholder="Detalles..." className="input-cerefa" />
                  </div>
                  <button type="submit" className="btn-guardar">Guardar</button>
                </div>
              </div>
            </form>

            <div className="panel-oscuro">
              <h2>Últimos Registros ({registros.length})</h2>
              <div className="contenedor-tabla">
                <table className="tabla-cerefa">
                  <thead>
                    <tr>
                      <th>Fecha</th>
                      <th>Tipo</th>
                      <th>Especie</th>
                      <th>Cant.</th>
                      <th>Obs</th>
                    </tr>
                  </thead>
                  <tbody>
                    {registros.map((reg, index) => (
                      <tr key={index}>
                        <td style={{ color: '#9ca3af' }}>{reg.fecha}</td>
                        <td><span className={`badge ${reg.tipo === 'Ingreso' ? 'badge-ingreso' : 'badge-egreso'}`}>{reg.tipo}</span></td>
                        <td><div style={{ fontWeight: 'bold' }}>{reg.especie}</div></td>
                        <td style={{ textAlign: 'center', fontWeight: 'bold' }}>{reg.cantidad}</td>
                        <td style={{ color: '#9ca3af' }}>{reg.observacion}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </main>
      )}
    </div>
  );
}

export default App;
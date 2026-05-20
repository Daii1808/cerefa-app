import React, { useState, useEffect } from 'react';

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
  const [nActa, setNActa] = useState('');
  const [categoria, setCategoria] = useState('');
  const [destino, setDestino] = useState('');
  const [observacion, setObservacion] = useState('');

  const [registros, setRegistros] = useState([
    { ficha: 'F-2026-006', fecha: '2026-05-19', tipo: 'Ingreso', especie: 'PATO JERGÓN', cientifico: 'Anas georgica', cant: 1, saldo: 1, obs: 'Ingresado según lista' },
    { ficha: 'F-2026-005', fecha: '2026-05-19', tipo: 'Ingreso', especie: 'GARZA GRANDE', cientifico: 'Ardea alba', cant: 1, saldo: 1, obs: 'Ingresado según lista' },
    { ficha: 'F-2026-004', fecha: '2026-05-19', tipo: 'Ingreso', especie: 'BANDURRIA', cientifico: 'Theristicus melanopis', cant: 1, saldo: 1, obs: 'Ingresado según lista' },
    { ficha: 'F-2026-003', fecha: '2026-05-19', tipo: 'Ingreso', especie: 'PEUCO', cientifico: 'Parabuteo unicinctus', cant: 1, saldo: 1, obs: 'Ingresado según lista' },
  ]);

  useEffect(() => {
    if (nombreComun && diccionarioAnimales[nombreComun]) {
      setNombreCientifico(diccionarioAnimales[nombreComun].cientifico);
      setCategoria(diccionarioAnimales[nombreComun].categoria);
      setDestino(diccionarioAnimales[nombreComun].destino);
    } else {
      setNombreCientifico('');
      setCategoria('');
      setDestino('');
    }
  }, [nombreComun]);

  const handleGuardar = (e) => {
    e.preventDefault();
    if (!nombreComun) {
      alert('Por favor, selecciona una especie.');
      return;
    }

    const nuevaFicha = `F-2026-00${registros.length + 3}`;
    const fechaActual = new Date().toISOString().split('T')[0];

    const nuevoRegistro = {
      ficha: nuevaFicha,
      fecha: fechaActual,
      tipo: tipoEvento,
      especie: nombreComun,
      cientifico: nombreCientifico,
      cant: parseInt(cantidad) || 1,
      saldo: parseInt(cantidad) || 1,
      obs: observacion || 'Sin observaciones'
    };

    setRegistros([nuevoRegistro, ...registros]);
    setNombreComun('');
    setObservacion('');
    setNActa('');
    setCantidad(1);
  };

  return (
    <div>
      {/* CABECERA INSTITUCIONAL BLANCA */}
      <header className="cabecera-cerefa">
        
        {/* MARCADOR DE POSICIÓN PARA EL LOGO PROVISORIO */}
        <div className="marcador-logo">
          LOGO
        </div>

        <h1 className="titulo-plataforma">Plataforma CEREFA</h1>
        <p className="subtitulo-plataforma">Centro de Rehabilitación de Fauna Silvestre</p>
      </header>

      {/* CUERPO PRINCIPAL */}
      <main className="contenido-principal">
        
        {/* PANEL FORMULARIO OSCURO */}
        <form onSubmit={handleGuardar} className="panel-oscuro">
          <h2>Nuevo Evento</h2>
          
          <div className="fila-formulario">
            <div className="grupo-campo">
              <label>Tipo de Evento</label>
              <div className="flex-botones">
                <button 
                  type="button" 
                  onClick={() => setTipoEvento('Ingreso')}
                  className={`btn-tipo ${tipoEvento === 'Ingreso' ? 'activo-ingreso' : ''}`}
                >
                  + Ingreso
                </button>
                <button 
                  type="button" 
                  onClick={() => setTipoEvento('Egreso')}
                  className={`btn-tipo ${tipoEvento === 'Egreso' ? 'activo-egreso' : ''}`}
                >
                  - Egreso
                </button>
              </div>
            </div>

            <div className="grupo-campo">
              <label>Nombre Común</label>
              <select 
                value={nombreComun} 
                onChange={(e) => setNombreComun(e.target.value)}
                className="select-cerefa"
              >
                <option value="">-- Selecciona --</option>
                {Object.keys(diccionarioAnimales).map(animal => (
                  <option key={animal} value={animal}>{animal}</option>
                ))}
              </select>
            </div>

            <div className="grupo-campo">
              <label>Nombre Científico</label>
              <input 
                type="text" 
                value={nombreCientifico} 
                disabled 
                className="input-cerefa input-deshabilitado" 
                placeholder="Automático..." 
              />
            </div>

            <div className="grupo-campo">
              <div style={{ display: 'flex', gap: '10px' }}>
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                  <label>Cant.</label>
                  <input type="number" value={cantidad} onChange={(e) => setCantidad(e.target.value)} min="1" className="input-cerefa" />
                </div>
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                  <label>N° Acta</label>
                  <input type="text" value={nActa} onChange={(e) => setNActa(e.target.value)} placeholder="Opcional" className="input-cerefa" />
                </div>
              </div>
            </div>
          </div>

          <div className="fila-formulario" style={{ alignItems: 'flex-end' }}>
            <div className="grupo-campo">
              <label>Categoría del Evento</label>
              <input type="text" value={categoria} onChange={(e) => setCategoria(e.target.value)} placeholder="Ej: Aves" className="input-cerefa" />
            </div>

            <div className="grupo-campo">
              <label>Destino</label>
              <input type="text" value={destino} onChange={(e) => setDestino(e.target.value)} placeholder="Ej: Rehabilitación" className="input-cerefa" />
            </div>

            <div className="grupo-campo" style={{ gridColumn: 'span 2', display: 'flex', flexDirection: 'row', gap: '15px', alignItems: 'flex-end' }}>
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                <label>Observación</label>
                <input type="text" value={observacion} onChange={(e) => setObservacion(e.target.value)} placeholder="Detalles..." className="input-cerefa" />
              </div>
              <button type="submit" className="btn-guardar">Guardar</button>
            </div>
          </div>
          <p className="nota-pie">* El sistema calculará el número de ficha y los saldos automáticamente al guardar.</p>
        </form>

        {/* PANEL TABLA OSCURA */}
        <div className="panel-oscuro">
          <h2>Últimos Registros ({registros.length})</h2>
          <div className="contenedor-tabla">
            <table className="tabla-cerefa">
              <thead>
                <tr>
                  <th>Ficha</th>
                  <th>Fecha</th>
                  <th>Tipo</th>
                  <th>Especie</th>
                  <th style={{ textAlign: 'center' }}>Cant.</th>
                  <th style={{ textAlign: 'center' }}>Saldo</th>
                  <th>Obs</th>
                </tr>
              </thead>
              <tbody>
                {registros.map((reg, index) => (
                  <tr key={index}>
                    <td className="ficha-verde">{reg.ficha}</td>
                    <td style={{ color: '#9ca3af' }}>{reg.fecha}</td>
                    <td>
                      <span className={`badge ${reg.tipo === 'Ingreso' ? 'badge-ingreso' : 'badge-egreso'}`}>
                        {reg.tipo}
                      </span>
                    </td>
                    <td>
                      <div style={{ fontWeight: 'bold' }}>{reg.especie}</div>
                      <div style={{ fontSize: '12px', color: '#6b7280', fontStyle: 'italic' }}>{reg.cientifico}</div>
                    </td>
                    <td style={{ textAlign: 'center', fontWeight: 'bold' }}>{reg.cant}</td>
                    <td style={{ textAlign: 'center' }}>
                      <span className="saldo-caja">{reg.saldo}</span>
                    </td>
                    <td style={{ color: '#9ca3af' }}>{reg.obs}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

      </main>
    </div>
  );
}

export default App;
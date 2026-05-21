import React, { useState, useEffect } from 'react';
import { guardarEvento, obtenerEventos, verificarMedico } from './supabaseService';
import logoCerefa from './assets/logo.jpg';

function App() {
  const diccionarioAnimales = {
    'PATO JERGÓN': { cientifico: 'Anas georgica', categoria: 'Aves', destino: 'Rehabilitación' },
    'GARZA GRANDE': { cientifico: 'Ardea alba', categoria: 'Aves', destino: 'Clínica' },
    'BANDURRIA': { cientifico: 'Theristicus melanopis', categoria: 'Aves', destino: 'Rehabilitación' },
    'PEUCO': { cientifico: 'Parabuteo unicinctus', categoria: 'Rapaces', destino: 'Liberación' },
  };

  // Estados de Autenticación
  const [estaAutenticado, setEstaAutenticado] = useState(false);
  const [correoInput, setCorreoInput] = useState('');
  const [passwordInput, setPasswordInput] = useState('');
  const [doctorEmail, setDoctorEmail] = useState('');
  const [authError, setAuthError] = useState('');
  const [cargandoAuth, setCargandoAuth] = useState(false);

  // Estados de la Aplicación
  const [activeTab, setActiveTab] = useState('registro'); // 'registro', 'inventario', 'metricas'
  const [registros, setRegistros] = useState([]);
  const [cargandoDatos, setCargandoDatos] = useState(false);
  
  // Filtro de búsqueda para Inventario
  const [buscarInventario, setBuscarInventario] = useState('');

  // Estados del Formulario de Evento
  const [tipoEvento, setTipoEvento] = useState('Ingreso'); // 'Ingreso' o 'Egreso'
  const [nombreComun, setNombreComun] = useState('');
  const [nombreCientifico, setNombreCientifico] = useState('');
  const [cantidad, setCantidad] = useState(1);
  const [observacion, setObservacion] = useState('');
  const [categoriaEvento, setCategoriaEvento] = useState('SAG'); // 'SAG', 'Particular', 'Rescate', 'Entrega Voluntaria'
  const [destino, setDestino] = useState('Rehabilitación'); // 'Rehabilitación', 'Clínica', 'Liberación', 'Fallecido'
  const [numeroActa, setNumeroActa] = useState('');
  const [numeroFichaSeleccionada, setNumeroFichaSeleccionada] = useState(''); // Para Egresos

  // Cargar registros médicos al iniciar
  const cargarDatos = async () => {
    setCargandoDatos(true);
    try {
      const datos = await obtenerEventos();
      setRegistros(datos || []);
    } catch (error) {
      console.error("Error al cargar eventos:", error);
    } finally {
      setCargandoDatos(false);
    }
  };

  useEffect(() => {
    cargarDatos();
  }, []);

  // Rellenar automáticamente el nombre científico al seleccionar una especie (solo en Ingresos)
  useEffect(() => {
    if (tipoEvento === 'Ingreso') {
      if (nombreComun && diccionarioAnimales[nombreComun]) {
        setNombreCientifico(diccionarioAnimales[nombreComun].cientifico);
        setDestino(diccionarioAnimales[nombreComun].destino);
      } else {
        setNombreCientifico('');
      }
    }
  }, [nombreComun, tipoEvento]);

  // Manejar el cambio de Ficha Seleccionada para Egresos
  useEffect(() => {
    if (tipoEvento === 'Egreso' && numeroFichaSeleccionada) {
      const registroFicha = registros.find(r => r.numero_ficha === numeroFichaSeleccionada);
      if (registroFicha) {
        setNombreComun(registroFicha.nombre_comun || '');
        setNombreCientifico(registroFicha.nombre_cientifico || '');
        setCategoriaEvento(registroFicha.categoria_evento || 'Particular');
        setDestino(registroFicha.destino || 'Clínica');
      }
    }
  }, [numeroFichaSeleccionada, tipoEvento, registros]);

  // Manejar el cambio de Tipo de Evento
  const cambiarTipoEvento = (tipo) => {
    setTipoEvento(tipo);
    setNombreComun('');
    setNombreCientifico('');
    setNumeroFichaSeleccionada('');
    setObservacion('');
    setCantidad(1);
    setNumeroActa('');
  };

  // Manejar Login Médico
  const manejarLogin = async (e) => {
    e.preventDefault();
    setAuthError('');
    if (!correoInput || !passwordInput) {
      setAuthError('Por favor ingresa correo y contraseña.');
      return;
    }
    setCargandoAuth(true);
    try {
      const esValido = await verificarMedico(correoInput, passwordInput);
      if (esValido) {
        setEstaAutenticado(true);
        setDoctorEmail(correoInput.trim().toLowerCase());
        setCorreoInput('');
        setPasswordInput('');
      } else {
        setAuthError('Correo o contraseña incorrectos.');
      }
    } catch (error) {
      setAuthError('Error al conectar con la base de datos de Supabase.');
    } finally {
      setCargandoAuth(false);
    }
  };

  // Manejar Logout
  const manejarLogout = () => {
    setEstaAutenticado(false);
    setDoctorEmail('');
  };

  // Guardar Nuevo Evento
  const handleGuardar = async (e) => {
    e.preventDefault();

    if (tipoEvento === 'Ingreso' && !nombreComun) {
      return alert('Por favor selecciona una especie.');
    }
    if (tipoEvento === 'Egreso' && !numeroFichaSeleccionada) {
      return alert('Por favor selecciona una Ficha existente para realizar el egreso.');
    }
    if (parseInt(cantidad) <= 0) {
      return alert('La cantidad debe ser mayor que 0.');
    }

    // 1. Calcular Número de Ficha
    let fichaParaGuardar = '';
    if (tipoEvento === 'Ingreso') {
      const anioActual = new Date().getFullYear();
      // Filtrar ingresos de este año
      const ingresosAnio = registros.filter(r => 
        r.tipo_evento === 'Ingreso' && 
        r.fecha && r.fecha.startsWith(anioActual.toString())
      );
      const correlativo = ingresosAnio.length + 1;
      fichaParaGuardar = `F-${String(correlativo).padStart(3, '0')}-${anioActual}`;
    } else {
      fichaParaGuardar = numeroFichaSeleccionada;
    }

    // 2. Calcular Saldos (Anterior y Actual)
    // Buscamos el saldo actual más reciente de la especie seleccionada
    const registrosEspecie = registros.filter(r => r.nombre_cientifico === nombreCientifico);
    const saldoAnterior = registrosEspecie.length > 0 ? parseInt(registrosEspecie[0].saldo_actual) || 0 : 0;
    
    let saldoActual = 0;
    if (tipoEvento === 'Ingreso') {
      saldoActual = saldoAnterior + parseInt(cantidad);
    } else {
      saldoActual = Math.max(0, saldoAnterior - parseInt(cantidad));
      if (parseInt(cantidad) > saldoAnterior) {
        const confirmar = window.confirm(`¡Atención! Estás egresando ${cantidad} ejemplares pero el inventario registra solo ${saldoAnterior}. ¿Deseas continuar?`);
        if (!confirmar) return;
      }
    }

    const nuevoEvento = {
      fecha: new Date().toISOString(),
      numero_ficha: fichaParaGuardar,
      numero_acta_movimiento: numeroActa || 'Sin Acta',
      nombre_comun: nombreComun,
      nombre_cientifico: nombreCientifico,
      numero_ejemplar: parseInt(cantidad),
      tipo_evento: tipoEvento,
      categoria_evento: categoriaEvento,
      saldo_anterior: saldoAnterior,
      saldo_actual: saldoActual,
      destino: destino,
      observacion: observacion || 'Sin observaciones',
      doctor_email: doctorEmail
    };

    try {
      await guardarEvento(nuevoEvento);
      alert(`¡Operación Exitosa! Ficha ${fichaParaGuardar} guardada correctamente.`);
      
      // Limpiar Formulario y recargar datos
      setNombreComun('');
      setNombreCientifico('');
      setObservacion('');
      setCantidad(1);
      setNumeroActa('');
      setNumeroFichaSeleccionada('');
      await cargarDatos();
    } catch (error) {
      alert("Hubo un error al guardar el registro en la base de datos.");
    }
  };

  // Calcular el inventario actual agrupando por especie (saldo_actual de su registro más reciente)
  const obtenerInventario = () => {
    const inventario = {};
    
    // Recorremos los registros (que vienen ordenados de más reciente a más antiguo)
    registros.forEach(reg => {
      if (reg.nombre_comun && !inventario[reg.nombre_comun]) {
        inventario[reg.nombre_comun] = {
          nombreComun: reg.nombre_comun,
          nombreCientifico: reg.nombre_cientifico,
          saldo: reg.saldo_actual || 0,
          categoria: reg.categoria_evento || 'Aves',
          destino: reg.destino || 'Clínica'
        };
      }
    });

    // Filtrar los que tengan saldo > 0 y que coincidan con la búsqueda
    return Object.values(inventario)
      .filter(item => item.saldo > 0)
      .filter(item => 
        item.nombreComun.toLowerCase().includes(buscarInventario.toLowerCase()) ||
        item.nombreCientifico.toLowerCase().includes(buscarInventario.toLowerCase())
      );
  };

  // Obtener Fichas Activas para Egresar (fichas que tienen ingresos y saldo > 0 en esa especie)
  const obtenerFichasActivas = () => {
    const fichasMap = new Map();
    // registros ordenados por fecha desc
    registros.forEach(reg => {
      if (reg.numero_ficha && !fichasMap.has(reg.numero_ficha)) {
        fichasMap.set(reg.numero_ficha, reg);
      }
    });

    return Array.from(fichasMap.values())
      .filter(r => r.tipo_evento === 'Ingreso' && r.saldo_actual > 0)
      .map(r => ({
        ficha: r.numero_ficha,
        nombre: r.nombre_comun,
        saldo: r.saldo_actual
      }));
  };

  // Métricas rápidas para las tarjetas del Dashboard
  const totalIngresos = registros.filter(r => r.tipo_evento === 'Ingreso').reduce((acc, curr) => acc + (parseInt(curr.numero_ejemplar) || 0), 0);
  const totalEgresos = registros.filter(r => r.tipo_evento === 'Egreso').reduce((acc, curr) => acc + (parseInt(curr.numero_ejemplar) || 0), 0);
  const pacientesActivos = Math.max(0, totalIngresos - totalEgresos);
  const tasaExito = totalEgresos > 0 
    ? Math.round((registros.filter(r => r.tipo_evento === 'Egreso' && r.destino === 'Liberación').reduce((acc, curr) => acc + (parseInt(curr.numero_ejemplar) || 0), 0) / totalEgresos) * 100) 
    : 0;

  return (
    <div>
      {/* 1. SECCIÓN DE INGRESO (LOGIN) */}
      {!estaAutenticado ? (
        <div className="login-container">
          <div className="login-card">
            <div style={{ marginBottom: '30px' }}>
              <img 
                src={logoCerefa} 
                alt="Logo CEREFA" 
                className="marcador-logo"
              />
              <h2 style={{ color: '#ffffff', fontSize: '26px', fontFamily: 'var(--font-display)', fontWeight: 800, letterSpacing: '-0.5px' }}>
                ACCESO CEREFA
              </h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: '13px', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.5px', marginTop: '5px' }}>
                Centro de Fauna Silvestre
              </p>
            </div>
            
            <form onSubmit={manejarLogin}>
              <div className="grupo-campo" style={{ marginBottom: '20px', textAlign: 'left' }}>
                <label>CORREO ELECTRÓNICO</label>
                <input 
                  type="email" 
                  placeholder="ejemplo@uss.cl" 
                  className="input-cerefa" 
                  value={correoInput}
                  onChange={(e) => setCorreoInput(e.target.value)}
                  required
                />
              </div>
              
              <div className="grupo-campo" style={{ marginBottom: '25px', textAlign: 'left' }}>
                <label>CONTRASEÑA</label>
                <input 
                  type="password" 
                  placeholder="********" 
                  className="input-cerefa" 
                  value={passwordInput}
                  onChange={(e) => setPasswordInput(e.target.value)}
                  required
                />
              </div>

              {authError && (
                <div style={{ color: 'var(--danger)', fontSize: '13px', fontWeight: 600, marginBottom: '20px', backgroundColor: 'rgba(239,68,68,0.1)', padding: '10px', borderRadius: '8px', border: '1px solid rgba(239,68,68,0.15)' }}>
                  ⚠️ {authError}
                </div>
              )}
              
              <button type="submit" className="btn-guardar" style={{ width: '100%', height: '48px' }} disabled={cargandoAuth}>
                {cargandoAuth ? 'Verificando...' : 'Iniciar Sesión'}
              </button>
            </form>
          </div>
        </div>
      ) : (
        /* 2. SECCIÓN PRINCIPAL (DASHBOARD) */
        <main>
          {/* Cabecera Estilizada */}
          <header className="cabecera-cerefa">
            <img src={logoCerefa} alt="Logo CEREFA" className="marcador-logo" />  
            <h1 className="titulo-plataforma">Plataforma CEREFA</h1>
            <p className="subtitulo-plataforma">Centro de Rehabilitación de Fauna Silvestre</p>
          </header>

          <div className="contenido-principal">
            {/* Barra de Perfil Médico */}
            <div className="doctor-profile-strip">
              <div className="doctor-info">
                <div className="doctor-avatar">
                  {doctorEmail.charAt(0).toUpperCase()}
                </div>
                <div>
                  <span>Médico Conectado: </span>
                  <strong style={{ color: 'var(--primary)' }}>{doctorEmail}</strong>
                </div>
              </div>
              <button onClick={manejarLogout} className="btn-logout">
                Cerrar Sesión
              </button>
            </div>

            {/* Pestañas de Navegación del Dashboard */}
            <nav className="tab-navigation">
              <button 
                onClick={() => setActiveTab('registro')} 
                className={`tab-btn ${activeTab === 'registro' ? 'active' : ''}`}
              >
                📝 Registros Médicos
              </button>
              <button 
                onClick={() => setActiveTab('inventario')} 
                className={`tab-btn ${activeTab === 'inventario' ? 'active' : ''}`}
              >
                🦅 Inventario de Fauna
              </button>
              <button 
                onClick={() => setActiveTab('metricas')} 
                className={`tab-btn ${activeTab === 'metricas' ? 'active' : ''}`}
              >
                📊 Panel de Métricas
              </button>
            </nav>

            {/* Métricas Rápidas (Superior) */}
            <section className="metricas-grid">
              <div className="card-metrica primary-border">
                <div className="icon-wrapper icon-primary">📥</div>
                <div className="metrica-info">
                  <h4>Total Ingresos</h4>
                  <div className="metrica-valor">{cargandoDatos ? '...' : totalIngresos}</div>
                </div>
              </div>

              <div className="card-metrica danger-border">
                <div className="icon-wrapper icon-danger">📤</div>
                <div className="metrica-info">
                  <h4>Total Egresos</h4>
                  <div className="metrica-valor">{cargandoDatos ? '...' : totalEgresos}</div>
                </div>
              </div>

              <div className="card-metrica">
                <div className="icon-wrapper icon-info">🐾</div>
                <div className="metrica-info">
                  <h4>Pacientes Activos</h4>
                  <div className="metrica-valor">{cargandoDatos ? '...' : pacientesActivos}</div>
                </div>
              </div>

              <div className="card-metrica">
                <div className="icon-wrapper" style={{ background: 'rgba(245, 158, 11, 0.1)', color: 'var(--warning)', border: '1px solid rgba(245, 158, 11, 0.2)' }}>📈</div>
                <div className="metrica-info">
                  <h4>Tasa de Liberación</h4>
                  <div className="metrica-valor">{cargandoDatos ? '...' : `${tasaExito}%`}</div>
                </div>
              </div>
            </section>

            {/* PESTAÑA 1: REGISTRO DE EVENTOS */}
            {activeTab === 'registro' && (
              <div className="animate-fade">
                {/* Formulario de Registro */}
                <form onSubmit={handleGuardar} className="panel-oscuro">
                  <h2>Nuevo Registro Médico</h2>
                  
                  <div className="fila-formulario">
                    {/* Tipo de Evento */}
                    <div className="grupo-campo">
                      <label>Tipo de Evento</label>
                      <div className="flex-botones">
                        <button 
                          type="button" 
                          onClick={() => cambiarTipoEvento('Ingreso')} 
                          className={`btn-tipo ${tipoEvento === 'Ingreso' ? 'activo-ingreso' : ''}`}
                        >
                          📥 Ingreso
                        </button>
                        <button 
                          type="button" 
                          onClick={() => cambiarTipoEvento('Egreso')} 
                          className={`btn-tipo ${tipoEvento === 'Egreso' ? 'activo-egreso' : ''}`}
                        >
                          📤 Egreso
                        </button>
                      </div>
                    </div>

                    {/* Ficha Relacionada (Solo para Egresos) */}
                    {tipoEvento === 'Egreso' && (
                      <div className="grupo-campo">
                        <label>Ficha de Ingreso Activa</label>
                        <select 
                          value={numeroFichaSeleccionada} 
                          onChange={(e) => setNumeroFichaSeleccionada(e.target.value)} 
                          className="select-cerefa"
                          required
                        >
                          <option value="">-- Selecciona una Ficha --</option>
                          {obtenerFichasActivas().map(item => (
                            <option key={item.ficha} value={item.ficha}>
                              {item.ficha} - {item.nombre} (Saldo: {item.saldo})
                            </option>
                          ))}
                        </select>
                      </div>
                    )}

                    {/* Nombre Común */}
                    <div className="grupo-campo">
                      <label>Especie (Nombre Común)</label>
                      {tipoEvento === 'Ingreso' ? (
                        <select 
                          value={nombreComun} 
                          onChange={(e) => setNombreComun(e.target.value)} 
                          className="select-cerefa"
                          required
                        >
                          <option value="">-- Selecciona --</option>
                          {Object.keys(diccionarioAnimales).map(animal => (
                            <option key={animal} value={animal}>{animal}</option>
                          ))}
                        </select>
                      ) : (
                        <input 
                          type="text" 
                          value={nombreComun} 
                          disabled 
                          className="input-cerefa input-deshabilitado" 
                        />
                      )}
                    </div>

                    {/* Nombre Científico */}
                    <div className="grupo-campo">
                      <label>Nombre Científico</label>
                      <input 
                        type="text" 
                        value={nombreCientifico} 
                        disabled 
                        className="input-cerefa input-deshabilitado" 
                      />
                    </div>
                  </div>

                  <div className="fila-formulario">
                    {/* Cantidad */}
                    <div className="grupo-campo">
                      <label>Cantidad de Ejemplares</label>
                      <input 
                        type="number" 
                        value={cantidad} 
                        onChange={(e) => setCantidad(Math.max(1, parseInt(e.target.value) || 1))} 
                        min="1" 
                        className="input-cerefa" 
                        required
                      />
                    </div>

                    {/* Categoría Evento */}
                    <div className="grupo-campo">
                      <label>Categoría del Evento</label>
                      {tipoEvento === 'Ingreso' ? (
                        <select 
                          value={categoriaEvento} 
                          onChange={(e) => setCategoriaEvento(e.target.value)} 
                          className="select-cerefa"
                        >
                          <option value="SAG">SAG</option>
                          <option value="Particular">Particular</option>
                          <option value="Rescate">Rescate CEREFA</option>
                          <option value="Entrega Voluntaria">Entrega Voluntaria</option>
                        </select>
                      ) : (
                        <input 
                          type="text" 
                          value={categoriaEvento} 
                          disabled 
                          className="input-cerefa input-deshabilitado" 
                        />
                      )}
                    </div>

                    {/* Destino */}
                    <div className="grupo-campo">
                      <label>Destino o Estado</label>
                      {tipoEvento === 'Ingreso' ? (
                        <select 
                          value={destino} 
                          onChange={(e) => setDestino(e.target.value)} 
                          className="select-cerefa"
                        >
                          <option value="Rehabilitación">Rehabilitación</option>
                          <option value="Clínica">Clínica</option>
                        </select>
                      ) : (
                        <select 
                          value={destino} 
                          onChange={(e) => setDestino(e.target.value)} 
                          className="select-cerefa"
                        >
                          <option value="Liberación">Liberación (Éxito)</option>
                          <option value="Clínica">Clínica de Apoyo</option>
                          <option value="Fallecido">Fallecido / Eutanasia</option>
                        </select>
                      )}
                    </div>

                    {/* Número de Acta */}
                    <div className="grupo-campo">
                      <label>Nº Acta de Movimiento</label>
                      <input 
                        type="text" 
                        placeholder="Ej. ACTA-8492" 
                        value={numeroActa} 
                        onChange={(e) => setNumeroActa(e.target.value)} 
                        className="input-cerefa" 
                      />
                    </div>
                  </div>

                  {/* Observación y Envío */}
                  <div className="fila-formulario" style={{ alignItems: 'flex-end', marginBottom: '0px' }}>
                    <div className="grupo-campo" style={{ gridColumn: 'span 2', display: 'flex', flexDirection: 'row', gap: '15px', alignItems: 'flex-end' }}>
                      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                        <label>Observaciones Clínicas / Diagnóstico</label>
                        <input 
                          type="text" 
                          value={observacion} 
                          onChange={(e) => setObservacion(e.target.value)} 
                          placeholder="Síntomas, procedencia, estado corporal..." 
                          className="input-cerefa" 
                        />
                      </div>
                      <button type="submit" className="btn-guardar">
                        💾 Guardar Ficha
                      </button>
                    </div>
                  </div>
                </form>

                {/* Tabla de Últimos Registros */}
                <div className="panel-oscuro">
                  <h2>Últimos Eventos Registrados en Supabase ({registros.length})</h2>
                  <div className="contenedor-tabla">
                    <table className="tabla-cerefa">
                      <thead>
                        <tr>
                          <th>Ficha</th>
                          <th>Fecha</th>
                          <th>Tipo</th>
                          <th>Especie / Científico</th>
                          <th style={{ textAlign: 'center' }}>Cant.</th>
                          <th>Categoría/Destino</th>
                          <th>Médico</th>
                          <th>Observación</th>
                        </tr>
                      </thead>
                      <tbody>
                        {cargandoDatos ? (
                          <tr>
                            <td colSpan="8" style={{ textAlign: 'center', padding: '30px', color: 'var(--text-muted)' }}>
                              Cargando registros médicos desde Supabase...
                            </td>
                          </tr>
                        ) : registros.length === 0 ? (
                          <tr>
                            <td colSpan="8" style={{ textAlign: 'center', padding: '30px', color: 'var(--text-muted)' }}>
                              No hay registros cargados.
                            </td>
                          </tr>
                        ) : (
                          registros.map((reg, index) => (
                            <tr key={reg.id || index}>
                              <td>
                                <span className="table-ficha">
                                  {reg.numero_ficha || 'F-000-0000'}
                                </span>
                              </td>
                              <td style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
                                {reg.fecha ? new Date(reg.fecha).toLocaleDateString('es-CL') : 'Sin fecha'}
                              </td>
                              <td>
                                <span className={`badge ${reg.tipo_evento === 'Ingreso' ? 'badge-ingreso' : 'badge-egreso'}`}>
                                  {reg.tipo_evento === 'Ingreso' ? '📥 Ingreso' : '📤 Egreso'}
                                </span>
                              </td>
                              <td>
                                <div className="table-especie">{reg.nombre_comun}</div>
                                <div className="table-cientifico">{reg.nombre_cientifico}</div>
                              </td>
                              <td style={{ textAlign: 'center', fontWeight: '800', color: '#ffffff', fontSize: '15px' }}>
                                {reg.numero_ejemplar}
                              </td>
                              <td>
                                <div style={{ fontWeight: '600', fontSize: '13px' }}>{reg.categoria_evento}</div>
                                <div style={{ color: 'var(--primary)', fontSize: '12px' }}>{reg.destino}</div>
                              </td>
                              <td className="table-doctor">
                                {reg.doctor_email ? reg.doctor_email.split('@')[0] : 'S/I'}
                              </td>
                              <td style={{ color: 'var(--text-secondary)', fontSize: '13px', maxWidth: '250px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={reg.observacion}>
                                {reg.observacion}
                              </td>
                            </tr>
                          ))
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}

            {/* PESTAÑA 2: INVENTARIO DE FAUNA ACTIVA */}
            {activeTab === 'inventario' && (
              <div className="animate-fade">
                <div className="panel-oscuro">
                  <h2>Inventario Clínico Activo</h2>
                  <p style={{ color: 'var(--text-secondary)', marginBottom: '20px', fontSize: '14px' }}>
                    Esta lista muestra el conteo neto y actualizado de ejemplares de fauna silvestre que se encuentran actualmente internados en rehabilitación en el CEREFA.
                  </p>

                  {/* Buscador */}
                  <div className="buscador-wrapper">
                    <span className="buscador-icon">🔍</span>
                    <input 
                      type="text" 
                      placeholder="Buscar especie por nombre común o científico..." 
                      className="input-cerefa"
                      value={buscarInventario}
                      onChange={(e) => setBuscarInventario(e.target.value)}
                    />
                  </div>

                  {/* Grid de Fichas de Inventario */}
                  {cargandoDatos ? (
                    <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
                      Calculando inventario activo...
                    </div>
                  ) : obtenerInventario().length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
                      No se encontraron ejemplares activos en el inventario que coincidan con la búsqueda.
                    </div>
                  ) : (
                    <div className="inventario-grid">
                      {obtenerInventario().map(item => (
                        <div key={item.nombreComun} className="ficha-inventario">
                          <div className="ficha-header">
                            <div>
                              <div className="ficha-especie">{item.nombreComun}</div>
                              <div className="ficha-cientifico">{item.nombreCientifico}</div>
                            </div>
                            <div className="ficha-saldo-wrapper">
                              <div className="ficha-saldo-label">En Centro</div>
                              <div className="ficha-saldo">{item.saldo}</div>
                            </div>
                          </div>

                          <div className="ficha-footer">
                            <span className="ficha-categoria">{item.categoria}</span>
                            <span className="ficha-destino">Último Destino: <strong>{item.destino}</strong></span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* PESTAÑA 3: PANEL DE MÉTRICAS */}
            {activeTab === 'metricas' && (
              <div className="animate-fade">
                <div className="panel-oscuro">
                  <h2>Métricas Clínicas e Indicadores CEREFA</h2>
                  <p style={{ color: 'var(--text-secondary)', marginBottom: '30px', fontSize: '14px' }}>
                    Visualiza la tasa de éxito clínico y la distribución de destinos y categorías de la fauna ingresada.
                  </p>

                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '30px' }}>
                    {/* Gráfico 1: Tasa de Éxito y Destino de Egresos */}
                    <div>
                      <h3 style={{ fontSize: '16px', color: '#ffffff', marginBottom: '15px', fontWeight: '600' }}>Destinos de Egresos (%)</h3>
                      <div className="bar-chart-container">
                        <div className="chart-bar-item">
                          <div className="chart-bar-header">
                            <span>Liberación (Éxito Clínico)</span>
                            <span>{tasaExito}%</span>
                          </div>
                          <div className="chart-bar-bg">
                            <div className="chart-bar-fill primary" style={{ width: `${tasaExito}%` }}></div>
                          </div>
                        </div>

                        <div className="chart-bar-item">
                          <div className="chart-bar-header">
                            <span>Clínica de Apoyo / Traspaso</span>
                            <span>
                              {totalEgresos > 0 
                                ? Math.round((registros.filter(r => r.tipo_evento === 'Egreso' && r.destino === 'Clínica').reduce((acc, curr) => acc + (parseInt(curr.numero_ejemplar) || 0), 0) / totalEgresos) * 100) 
                                : 0}%
                            </span>
                          </div>
                          <div className="chart-bar-bg">
                            <div className="chart-bar-fill info" style={{ width: `${totalEgresos > 0 ? (registros.filter(r => r.tipo_evento === 'Egreso' && r.destino === 'Clínica').reduce((acc, curr) => acc + (parseInt(curr.numero_ejemplar) || 0), 0) / totalEgresos) * 100 : 0}%` }}></div>
                          </div>
                        </div>

                        <div className="chart-bar-item">
                          <div className="chart-bar-header">
                            <span>Fallecido / Deceso / Eutanasia</span>
                            <span>
                              {totalEgresos > 0 
                                ? Math.round((registros.filter(r => r.tipo_evento === 'Egreso' && r.destino === 'Fallecido').reduce((acc, curr) => acc + (parseInt(curr.numero_ejemplar) || 0), 0) / totalEgresos) * 100) 
                                : 0}%
                            </span>
                          </div>
                          <div className="chart-bar-bg">
                            <div className="chart-bar-fill warning" style={{ width: `${totalEgresos > 0 ? (registros.filter(r => r.tipo_evento === 'Egreso' && r.destino === 'Fallecido').reduce((acc, curr) => acc + (parseInt(curr.numero_ejemplar) || 0), 0) / totalEgresos) * 100 : 0}%` }}></div>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Gráfico 2: Origen / Categoría de Eventos */}
                    <div>
                      <h3 style={{ fontSize: '16px', color: '#ffffff', marginBottom: '15px', fontWeight: '600' }}>Categorías de Ingreso (%)</h3>
                      <div className="bar-chart-container">
                        <div className="chart-bar-item">
                          <div className="chart-bar-header">
                            <span>Entregados por SAG</span>
                            <span>
                              {totalIngresos > 0 
                                ? Math.round((registros.filter(r => r.tipo_evento === 'Ingreso' && r.categoria_evento === 'SAG').reduce((acc, curr) => acc + (parseInt(curr.numero_ejemplar) || 0), 0) / totalIngresos) * 100) 
                                : 0}%
                            </span>
                          </div>
                          <div className="chart-bar-bg">
                            <div className="chart-bar-fill primary" style={{ width: `${totalIngresos > 0 ? (registros.filter(r => r.tipo_evento === 'Ingreso' && r.categoria_evento === 'SAG').reduce((acc, curr) => acc + (parseInt(curr.numero_ejemplar) || 0), 0) / totalIngresos) * 100 : 0}%` }}></div>
                          </div>
                        </div>

                        <div className="chart-bar-item">
                          <div className="chart-bar-header">
                            <span>Particulares / Entregas Directas</span>
                            <span>
                              {totalIngresos > 0 
                                ? Math.round((registros.filter(r => r.tipo_evento === 'Ingreso' && r.categoria_evento === 'Particular').reduce((acc, curr) => acc + (parseInt(curr.numero_ejemplar) || 0), 0) / totalIngresos) * 100) 
                                : 0}%
                            </span>
                          </div>
                          <div className="chart-bar-bg">
                            <div className="chart-bar-fill info" style={{ width: `${totalIngresos > 0 ? (registros.filter(r => r.tipo_evento === 'Ingreso' && r.categoria_evento === 'Particular').reduce((acc, curr) => acc + (parseInt(curr.numero_ejemplar) || 0), 0) / totalIngresos) * 100 : 0}%` }}></div>
                          </div>
                        </div>

                        <div className="chart-bar-item">
                          <div className="chart-bar-header">
                            <span>Rescates Propios CEREFA</span>
                            <span>
                              {totalIngresos > 0 
                                ? Math.round((registros.filter(r => r.tipo_evento === 'Ingreso' && r.categoria_evento === 'Rescate').reduce((acc, curr) => acc + (parseInt(curr.numero_ejemplar) || 0), 0) / totalIngresos) * 100) 
                                : 0}%
                            </span>
                          </div>
                          <div className="chart-bar-bg">
                            <div className="chart-bar-fill warning" style={{ width: `${totalIngresos > 0 ? (registros.filter(r => r.tipo_evento === 'Ingreso' && r.categoria_evento === 'Rescate').reduce((acc, curr) => acc + (parseInt(curr.numero_ejemplar) || 0), 0) / totalIngresos) * 100 : 0}%` }}></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </main>
      )}
    </div>
  );
}

export default App;
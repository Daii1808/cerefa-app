import React, { useState, useEffect } from 'react';
import { guardarEvento, obtenerEventos, verificarMedico, actualizarEvento } from './supabaseService';
import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';
import logoCerefa from './assets/logo.jpg';

function App() {
  const [diccionarioAnimales, setDiccionarioAnimales] = useState({
    'PATO JERGÓN': { cientifico: 'Anas georgica', categoria: 'Aves', destino: 'Rehabilitación' },
    'GARZA GRANDE': { cientifico: 'Ardea alba', categoria: 'Aves', destino: 'Clínica' },
    'BANDURRIA': { cientifico: 'Theristicus melanopis', categoria: 'Aves', destino: 'Rehabilitación' },
    'PEUCO': { cientifico: 'Parabuteo unicinctus', categoria: 'Rapaces', destino: 'Liberado' },
    'LORO CHOROY': { cientifico: 'Enicognathus leptorhynchus', categoria: 'Aves', destino: 'Rehabilitación' },
    'ZORRO CHILLA': { cientifico: 'Lycalopex griseus', categoria: 'Mamíferos', destino: 'Rehabilitación' },
    'QUELTEHUE': { cientifico: 'Vanellus chilensis', categoria: 'Aves', destino: 'Rehabilitación' },
    'MONITO DEL MONTE': { cientifico: 'Dromiciops gliroides', categoria: 'Mamíferos', destino: 'Rehabilitación' },
    'CACHAÑA': { cientifico: 'Enicognathus ferrugineus', categoria: 'Aves', destino: 'Rehabilitación' },
    'LECHUZA': { cientifico: 'Tyto alba', categoria: 'Rapaces', destino: 'Rehabilitación' },
    'PETREL PLATEADO': { cientifico: 'Fulmarus glacialoides', categoria: 'Aves', destino: 'Rehabilitación' },
    'CHUNCHO': { cientifico: 'Glaucidium nana', categoria: 'Rapaces', destino: 'Rehabilitación' },
    'ZORZAL': { cientifico: 'Turdus falcklandii', categoria: 'Aves', destino: 'Rehabilitación' },
    'GUIÑA': { cientifico: 'Leopardus guigna', categoria: 'Mamíferos', destino: 'Rehabilitación' },
    'JOTE': { cientifico: 'Coragyps atratus', categoria: 'Aves', destino: 'Rehabilitación' },
    'PUDÚ': { cientifico: 'Pudu puda', categoria: 'Mamíferos', destino: 'Rehabilitación' },
    'TIUQUE': { cientifico: 'Milvago chimango', categoria: 'Rapaces', destino: 'Rehabilitación' },
    'CORMORAN': { cientifico: 'Phalacrocorax', categoria: 'Aves', destino: 'Rehabilitación' },
    'CONCON': { cientifico: 'Strix rufipes', categoria: 'Rapaces', destino: 'Rehabilitación' },
    'CERNICALO': { cientifico: 'Falco sparverius', categoria: 'Rapaces', destino: 'Rehabilitación' }
  });

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

  // Filtros Avanzados para Historial (Pestaña Registro)
  const [filtroSemestre, setFiltroSemestre] = useState('');
  const [filtroGeneral, setFiltroGeneral] = useState('');
  const [filtroFecha, setFiltroFecha] = useState('');
  const [filtroEspecie, setFiltroEspecie] = useState('');
  const [filtroTipo, setFiltroTipo] = useState('');

  // Estados del Modal de Edición
  const [modalAbierto, setModalAbierto] = useState(false);
  const [registroSeleccionado, setRegistroSeleccionado] = useState(null);
  const [modoEdicion, setModoEdicion] = useState(false);

  // Estados del Formulario de Evento
  const [tipoEvento, setTipoEvento] = useState('Ingreso'); // 'Ingreso' o 'Egreso'
  
  // Estados Modal Inventario Activo
  const [modalActivosAbierto, setModalActivosAbierto] = useState(false);
  const [especieModalActivos, setEspecieModalActivos] = useState('');
  
  // Filtros para Métricas
  const [metricaFiltroTiempo, setMetricaFiltroTiempo] = useState('Todos');
  const [metricaFiltroEspecie, setMetricaFiltroEspecie] = useState('Todas');
  const [nombreComun, setNombreComun] = useState('');
  const [nombreCientifico, setNombreCientifico] = useState('');
  const [cantidad, setCantidad] = useState(1);
  const [observacion, setObservacion] = useState('');
  const [categoriaEvento, setCategoriaEvento] = useState(''); // ej. 'SAG Puerto Montt'
  const [destino, setDestino] = useState('Rehabilitación'); // 'Rehabilitación', 'Clínica', 'Liberación', 'Fallecido'
  const [numeroActa, setNumeroActa] = useState('');
  const [numeroFichaSeleccionada, setNumeroFichaSeleccionada] = useState(''); // Para Egresos

  // Cargar registros médicos al iniciar
  const cargarDatos = async () => {
    setCargandoDatos(true);
    try {
      const datos = await obtenerEventos();
      setRegistros(datos || []);
      
      // Enriquecer el diccionario con especies dinámicas guardadas
      if (datos && datos.length > 0) {
        setDiccionarioAnimales(prevDict => {
          const nuevoDict = { ...prevDict };
          datos.forEach(r => {
            if (r.nombre_comun && r.nombre_cientifico) {
              const especieKey = r.nombre_comun.toUpperCase();
              if (!nuevoDict[especieKey]) {
                nuevoDict[especieKey] = {
                  cientifico: r.nombre_cientifico,
                  categoria: r.categoria_evento || 'Otra',
                  destino: r.destino || 'Rehabilitación'
                };
              }
            }
          });
          return nuevoDict;
        });
      }
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
      const especieUpper = nombreComun ? nombreComun.toUpperCase() : '';
      if (especieUpper && diccionarioAnimales[especieUpper]) {
        setNombreCientifico(diccionarioAnimales[especieUpper].cientifico);
        setDestino(diccionarioAnimales[especieUpper].destino);
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

  // Obtener Fichas Específicas para Modal
  const getFichasPorEspecie = (especie) => {
    const fichasMap = new Map();
    registros.forEach(reg => {
      if (reg.numero_ficha && reg.nombre_comun === especie && !fichasMap.has(reg.numero_ficha)) {
        fichasMap.set(reg.numero_ficha, reg);
      }
    });
    return Array.from(fichasMap.values()).filter(r => r.saldo_actual > 0);
  };

  const abrirModalActivos = (especie) => {
    setEspecieModalActivos(especie);
    setModalActivosAbierto(true);
  };

  // Lógica de Filtrado de Registros
  const registrosFiltrados = registros.filter(reg => {
    const fecha = reg.fecha ? reg.fecha.substring(0, 10) : '-';
    const tipo = reg.tipo_evento || '';
    const especie = reg.nombre_comun || '';
    const resp = reg.doctor_email || '';
    const ficha = reg.numero_ficha || '';
    
    const textoFila = `${ficha} ${fecha} ${tipo} ${especie} ${resp} ${reg.nombre_cientifico || ''}`.toLowerCase();
    
    const coincideGeneral = filtroGeneral === '' || textoFila.includes(filtroGeneral.toLowerCase());
    const coincideFecha = filtroFecha === '' || fecha.includes(filtroFecha);
    const coincideEspecie = filtroEspecie === '' || especie.toLowerCase().includes(filtroEspecie.toLowerCase());
    const coincideTipo = filtroTipo === '' || tipo.toLowerCase().includes(filtroTipo.toLowerCase());
    
    let coincideSemestre = true;
    if (filtroSemestre !== '' && fecha !== '-') {
      const mes = parseInt(fecha.split('-')[1], 10);
      if (filtroSemestre === 'S1') coincideSemestre = (mes >= 1 && mes <= 6);
      if (filtroSemestre === 'S2') coincideSemestre = (mes >= 7 && mes <= 12);
    }
    
    return coincideGeneral && coincideFecha && coincideEspecie && coincideTipo && coincideSemestre;
  });

  const descargarPDF = () => {
    try {
      console.log("Iniciando descargarPDF...");
      const doc = new jsPDF('l', 'pt', 'a4');
      const añoActual = new Date().getFullYear();
      let tituloPDF = "Reporte de Registros CEREFAS";
      if (filtroSemestre === 'S1') tituloPDF += ` - 1° Semestre ${añoActual}`;
      if (filtroSemestre === 'S2') tituloPDF += ` - 2° Semestre ${añoActual}`;

      doc.setFontSize(16);
      doc.text(tituloPDF, 40, 40);

      const columnas = [
        "FECHA", "Nº ficha", "Nombre comun", "Nombre científico", 
        "Nº Acta", "Cant.", "Tipo de evento", "Categoría", 
        "Saldo anterior", "Saldo actual", "Destino", "Observaciones"
      ];

      const datosImprimir = registrosFiltrados.map(r => {
        const fechaCorta = r.fecha ? r.fecha.substring(0, 10) : '';
        return [
          fechaCorta,
          r.numero_ficha || '',
          r.nombre_comun || '',
          r.nombre_cientifico || '',
          r.numero_acta_movimiento || '',
          r.numero_ejemplar || '1',
          r.tipo_evento || '',
          r.categoria_evento || '',
          r.saldo_anterior !== null ? r.saldo_anterior : '',
          r.saldo_actual !== null ? r.saldo_actual : '',
          r.destino || '',
          r.observacion || ''
        ];
      });

      if (datosImprimir.length === 0) {
        alert("No hay registros para exportar con los filtros actuales.");
        return;
      }

      const makeTable = typeof autoTable === 'function' ? autoTable : (autoTable && autoTable.default ? autoTable.default : null);
      if (makeTable) {
        makeTable(doc, {
          head: [columnas],
          body: datosImprimir,
          startY: 60,
          styles: { fontSize: 8, cellPadding: 3 },
          headStyles: { fillColor: [6, 78, 59] },
          theme: 'grid'
        });
      } else if (typeof doc.autoTable === 'function') {
        doc.autoTable({
          head: [columnas],
          body: datosImprimir,
          startY: 60,
          styles: { fontSize: 8, cellPadding: 3 },
          headStyles: { fillColor: [6, 78, 59] },
          theme: 'grid'
        });
      } else {
        throw new Error("autoTable module is an object but doesn't have a default function: " + JSON.stringify(autoTable));
      }

      // Calcular Estadísticas de los Registros Filtrados
      const totalIngresosPDF = registrosFiltrados.filter(r => r.tipo_evento === 'Ingreso').reduce((acc, curr) => acc + (parseInt(curr.numero_ejemplar) || 0), 0);
      const totalEgresosPDF = registrosFiltrados.filter(r => r.tipo_evento === 'Egreso').reduce((acc, curr) => acc + (parseInt(curr.numero_ejemplar) || 0), 0);
      
      const libPCT = totalEgresosPDF > 0 ? Math.round((registrosFiltrados.filter(r => r.tipo_evento === 'Egreso' && (r.destino === 'Liberado' || r.destino === 'Liberación')).reduce((acc, curr) => acc + (parseInt(curr.numero_ejemplar) || 0), 0) / totalEgresosPDF) * 100) : 0;
      const cliPCT = totalEgresosPDF > 0 ? Math.round((registrosFiltrados.filter(r => r.tipo_evento === 'Egreso' && (r.destino === 'Clínica' || r.destino === 'Clínica de Apoyo' || r.destino === 'Clinica')).reduce((acc, curr) => acc + (parseInt(curr.numero_ejemplar) || 0), 0) / totalEgresosPDF) * 100) : 0;
      const fallPCT = totalEgresosPDF > 0 ? Math.round((registrosFiltrados.filter(r => r.tipo_evento === 'Egreso' && (r.destino === 'Fallece' || r.destino === 'Eutanasia' || r.destino === 'Fallecido')).reduce((acc, curr) => acc + (parseInt(curr.numero_ejemplar) || 0), 0) / totalEgresosPDF) * 100) : 0;

      const sagPCT = totalIngresosPDF > 0 ? Math.round((registrosFiltrados.filter(r => r.tipo_evento === 'Ingreso' && r.categoria_evento === 'SAG').reduce((acc, curr) => acc + (parseInt(curr.numero_ejemplar) || 0), 0) / totalIngresosPDF) * 100) : 0;
      const partPCT = totalIngresosPDF > 0 ? Math.round((registrosFiltrados.filter(r => r.tipo_evento === 'Ingreso' && r.categoria_evento === 'Particular').reduce((acc, curr) => acc + (parseInt(curr.numero_ejemplar) || 0), 0) / totalIngresosPDF) * 100) : 0;
      const rescPCT = totalIngresosPDF > 0 ? Math.round((registrosFiltrados.filter(r => r.tipo_evento === 'Ingreso' && r.categoria_evento === 'Rescate').reduce((acc, curr) => acc + (parseInt(curr.numero_ejemplar) || 0), 0) / totalIngresosPDF) * 100) : 0;

      let currentY = doc.lastAutoTable ? doc.lastAutoTable.finalY + 30 : 150;
      
      doc.setFontSize(14);
      doc.setFont('helvetica', 'bold');
      doc.text("Resumen Estadístico del Reporte", 40, currentY);
      
      currentY += 20;
      doc.setFontSize(10);
      doc.setFont('helvetica', 'normal');
      doc.text(`Total Ingresos: ${totalIngresosPDF} ejemplares`, 40, currentY);
      doc.text(`Total Egresos: ${totalEgresosPDF} ejemplares`, 200, currentY);
      doc.text(`Pacientes Activos (Neto): ${Math.max(0, totalIngresosPDF - totalEgresosPDF)}`, 360, currentY);
      
      currentY += 30;
      const barWidth = 320;
      const barHeight = 8;
      
      const drawBar = (x, y, label, pct, r, g, b) => {
        doc.setFontSize(9);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(50, 50, 50);
        doc.text(label, x, y);
        doc.text(`${pct}%`, x + barWidth - doc.getTextWidth(`${pct}%`), y);
        
        doc.setFillColor(230, 230, 230);
        doc.rect(x, y + 4, barWidth, barHeight, 'F');
        
        if (pct > 0) {
            doc.setFillColor(r, g, b);
            doc.rect(x, y + 4, barWidth * (pct / 100), barHeight, 'F');
        }
      };

      doc.setFontSize(11);
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(0, 0, 0);
      doc.text("Destinos de Egresos (%)", 40, currentY);
      doc.text("Categorías de Ingreso (%)", 420, currentY);

      currentY += 20;
      drawBar(40, currentY, "Liberación (Éxito Clínico)", libPCT, 16, 185, 129);
      drawBar(420, currentY, "Entregados por SAG", sagPCT, 59, 130, 246);
      
      currentY += 25;
      drawBar(40, currentY, "Clínica de Apoyo / Traspaso", cliPCT, 56, 189, 248);
      drawBar(420, currentY, "Particulares / Entregas Directas", partPCT, 56, 189, 248);
      
      currentY += 25;
      drawBar(40, currentY, "Fallecido / Deceso / Eutanasia", fallPCT, 245, 158, 11);
      drawBar(420, currentY, "Rescates Propios CEREFAS", rescPCT, 245, 158, 11);
      
      // Agregar espacio para firma digital
      currentY += 60;
      doc.setFontSize(10);
      doc.setTextColor(0, 0, 0);
      doc.text("Firma: ___________________________", 40, currentY);
      doc.text("Responsable CEREFAS", 40, currentY + 15);

      const nombreArchivo = `CEREFAS_Reporte_${filtroSemestre ? filtroSemestre + '_' : ''}${añoActual}.pdf`;
      doc.save(nombreArchivo);
      console.log("PDF generado con éxito:", nombreArchivo);
    } catch (error) {
      console.error("Error al generar el PDF:", error);
      alert("Error al generar el PDF: " + error.message);
    }
  };

  const abrirModal = (registro) => {
    setRegistroSeleccionado({...registro});
    setModoEdicion(false);
    setModalAbierto(true);
  };

  const cerrarModal = () => {
    setModalAbierto(false);
    setRegistroSeleccionado(null);
    setModoEdicion(false);
  };

  const guardarCambiosModal = async () => {
    try {
      await actualizarEvento(registroSeleccionado.id, {
        fecha: registroSeleccionado.fecha,
        numero_acta_movimiento: registroSeleccionado.numero_acta_movimiento,
        destino: registroSeleccionado.destino,
        observacion: registroSeleccionado.observacion
      });
      alert('Cambios guardados con éxito.');
      cerrarModal();
      await cargarDatos();
    } catch (err) {
      alert('Error al guardar: ' + err.message);
    }
  };

  // Métricas rápidas y filtros para Gráficos
  let registrosMetricas = [...registros];
  if (metricaFiltroTiempo !== 'Todos') {
    const ahora = new Date();
    registrosMetricas = registrosMetricas.filter(r => {
      if (!r.fecha) return false;
      const fechaReg = new Date(r.fecha);
      const diffDias = (ahora - fechaReg) / (1000 * 60 * 60 * 24);
      if (metricaFiltroTiempo === 'Semanal') return diffDias <= 7;
      if (metricaFiltroTiempo === 'Mensual') return diffDias <= 30;
      if (metricaFiltroTiempo === 'Anual') return diffDias <= 365;
      return true;
    });
  }
  if (metricaFiltroEspecie !== 'Todas') {
    registrosMetricas = registrosMetricas.filter(r => r.nombre_comun && r.nombre_comun.toUpperCase() === metricaFiltroEspecie);
  }

  const totalIngresos = registrosMetricas.filter(r => r.tipo_evento === 'Ingreso').reduce((acc, curr) => acc + (parseInt(curr.numero_ejemplar) || 0), 0);
  const totalEgresos = registrosMetricas.filter(r => r.tipo_evento === 'Egreso').reduce((acc, curr) => acc + (parseInt(curr.numero_ejemplar) || 0), 0);
  const pacientesActivos = Math.max(0, totalIngresos - totalEgresos);
  const tasaExito = totalEgresos > 0 
    ? Math.round((registrosMetricas.filter(r => r.tipo_evento === 'Egreso' && (r.destino === 'Liberado' || r.destino === 'Liberación')).reduce((acc, curr) => acc + (parseInt(curr.numero_ejemplar) || 0), 0) / totalEgresos) * 100) 
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
                ACCESO CEREFAS
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
            <h1 className="titulo-plataforma">Plataforma CEREFAS</h1>
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
            {activeTab === 'metricas' && (
              <section className="metricas-grid animate-fade" style={{ marginBottom: '20px' }}>
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
            )}

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
                        <>
                          <input 
                            list="lista_especies"
                            value={nombreComun} 
                            onChange={(e) => setNombreComun(e.target.value.toUpperCase())} 
                            className="input-cerefa"
                            placeholder="Selecciona o escribe..."
                            required
                          />
                          <datalist id="lista_especies">
                            {Object.keys(diccionarioAnimales).map(animal => (
                              <option key={animal} value={animal} />
                            ))}
                          </datalist>
                        </>
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
                        onChange={(e) => setNombreCientifico(e.target.value)}
                        disabled={tipoEvento === 'Egreso'}
                        className={`input-cerefa ${tipoEvento === 'Egreso' ? 'input-deshabilitado' : ''}`}
                        placeholder="Autocompletado o escribe..."
                        required
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
                        <>
                          <input 
                            list="lista_categorias"
                            value={categoriaEvento} 
                            onChange={(e) => setCategoriaEvento(e.target.value)} 
                            className="input-cerefa"
                            placeholder="Ej: SAG Río Negro"
                            required
                          />
                          <datalist id="lista_categorias">
                            <option value="SAG Puerto Montt" />
                            <option value="SAG Puerto Varas" />
                            <option value="SAG Osorno" />
                            <option value="SAG Río Negro" />
                            <option value="Particular" />
                            <option value="Rescate CEREFAS" />
                            <option value="Entrega Voluntaria" />
                          </datalist>
                        </>
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
                      <input 
                        list="lista_destinos"
                        value={destino} 
                        onChange={(e) => setDestino(e.target.value)} 
                        className="input-cerefa"
                        placeholder="Ej: Rehabilitación / Liberado / Fallece"
                        required
                      />
                      <datalist id="lista_destinos">
                        <option value="Rehabilitación" />
                        <option value="Clínica" />
                        <option value="Ingreso" />
                        <option value="Liberado" />
                        <option value="Fallece" />
                        <option value="Eutanasia" />
                      </datalist>
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
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '15px', marginBottom: '20px', paddingBottom: '15px', borderBottom: '1px solid var(--border-color)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
                      <h2 style={{ marginBottom: 0 }}>Últimos Eventos Registrados ({registrosFiltrados.length})</h2>
                      <button type="button" onClick={descargarPDF} style={{ backgroundColor: '#1d4ed8', color: 'white', border: '1px solid #3b82f6', padding: '6px 16px', borderRadius: '20px', fontSize: '13px', fontWeight: 'bold', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        📄 Descargar PDF
                      </button>
                    </div>
                    
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', alignItems: 'center' }}>
                      <select value={filtroSemestre} onChange={(e) => setFiltroSemestre(e.target.value)} className="select-cerefa" style={{ padding: '6px 12px', fontSize: '13px', borderRadius: '20px', width: 'auto', backgroundColor: '#09090b' }}>
                        <option value="">Todos los Semestres</option>
                        <option value="S1">1° Semestre (Ene - Jun)</option>
                        <option value="S2">2° Semestre (Jul - Dic)</option>
                      </select>
                      
                      <div className="buscador-wrapper" style={{ margin: 0, flex: 1, minWidth: '150px', maxWidth: '200px' }}>
                        <input type="text" placeholder="Busca..." value={filtroGeneral} onChange={(e) => setFiltroGeneral(e.target.value)} className="input-cerefa" style={{ padding: '6px 12px', fontSize: '13px', borderRadius: '20px', backgroundColor: 'rgba(39, 39, 42, 0.5)' }} />
                      </div>
                      
                      <input type="text" placeholder="Fecha (rango)" value={filtroFecha} onChange={(e) => setFiltroFecha(e.target.value)} className="input-cerefa" style={{ padding: '6px 12px', fontSize: '13px', borderRadius: '20px', width: 'auto', backgroundColor: '#09090b' }} />
                      
                      <select value={filtroEspecie} onChange={(e) => setFiltroEspecie(e.target.value)} className="select-cerefa" style={{ padding: '6px 12px', fontSize: '13px', borderRadius: '20px', width: 'auto', backgroundColor: '#09090b' }}>
                        <option value="">Filtro por Especie</option>
                        {Object.keys(diccionarioAnimales).map(animal => <option key={animal} value={animal}>{animal}</option>)}
                      </select>
                      
                      <select value={filtroTipo} onChange={(e) => setFiltroTipo(e.target.value)} className="select-cerefa" style={{ padding: '6px 12px', fontSize: '13px', borderRadius: '20px', width: 'auto', backgroundColor: '#09090b' }}>
                        <option value="">Filtro por Tipo</option>
                        <option value="Ingreso">Ingreso</option>
                        <option value="Egreso">Egreso</option>
                      </select>
                    </div>
                  </div>
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
                        ) : registrosFiltrados.length === 0 ? (
                          <tr>
                            <td colSpan="8" style={{ textAlign: 'center', padding: '30px', color: 'var(--text-muted)' }}>
                              No hay registros que coincidan con la búsqueda.
                            </td>
                          </tr>
                        ) : (
                          registrosFiltrados.map((reg, index) => (
                            <tr key={reg.id || index} onClick={() => abrirModal(reg)} style={{ cursor: 'pointer' }} className="hover:bg-zinc-800 transition-colors">
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

                {/* MODAL FICHA DE EDICIÓN */}
                {modalAbierto && registroSeleccionado && (
                  <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 50, padding: '15px' }} onClick={cerrarModal}>
                    <div style={{ backgroundColor: '#18181b', border: '1px solid #27272a', borderRadius: '12px', width: '100%', maxWidth: '400px', display: 'flex', flexDirection: 'column', boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)', position: 'relative' }} onClick={e => e.stopPropagation()}>
                      <button type="button" onClick={cerrarModal} style={{ position: 'absolute', top: '8px', right: '8px', zIndex: 10, color: '#71717a', background: 'none', border: 'none', fontSize: '18px', cursor: 'pointer' }}>✕</button>

                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '16px', borderBottom: '1px solid #27272a' }}>
                        <div style={{ backgroundColor: 'rgba(6, 78, 59, 0.5)', padding: '6px', borderRadius: '50%', border: '1px solid rgba(4, 120, 87, 0.5)', fontSize: '16px' }}>📋</div>
                        <div>
                          <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 'bold', color: 'white' }}>{registroSeleccionado.numero_ficha || 'F-XXX'}</h3>
                          <p style={{ margin: 0, fontSize: '12px', fontFamily: 'monospace', color: registroSeleccionado.tipo_evento === 'Ingreso' ? '#34d399' : '#fb923c' }}>{registroSeleccionado.tipo_evento}</p>
                        </div>
                      </div>

                      <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '12px' }}>
                        <div style={{ backgroundColor: '#09090b', padding: '6px 8px', borderRadius: '6px', border: '1px solid #27272a' }}>
                          <span style={{ color: '#71717a', fontSize: '10px', textTransform: 'uppercase' }}>Paciente</span>
                          <strong style={{ display: 'block', color: 'white', fontSize: '14px' }}>{registroSeleccionado.nombre_comun || '-'}</strong>
                          <p style={{ margin: 0, fontSize: '11px', fontStyle: 'italic', color: '#a1a1aa' }}>{registroSeleccionado.nombre_cientifico || '-'}</p>
                        </div>

                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                          <div style={{ backgroundColor: '#09090b', padding: '6px 8px', borderRadius: '6px', border: '1px solid #27272a' }}>
                            <span style={{ color: '#71717a', fontSize: '10px', textTransform: 'uppercase' }}>Fecha</span>
                            <input type="text" value={registroSeleccionado.fecha || ''} onChange={(e) => setRegistroSeleccionado({...registroSeleccionado, fecha: e.target.value})} disabled={!modoEdicion} style={{ width: '100%', background: 'transparent', border: modoEdicion ? '1px solid #059669' : 'none', color: 'white', fontSize: '12px', outline: 'none' }} />
                          </div>
                          <div style={{ backgroundColor: '#09090b', padding: '6px 8px', borderRadius: '6px', border: '1px solid #27272a' }}>
                            <span style={{ color: '#71717a', fontSize: '10px', textTransform: 'uppercase' }}>N° Acta</span>
                            <input type="text" value={registroSeleccionado.numero_acta_movimiento || ''} onChange={(e) => setRegistroSeleccionado({...registroSeleccionado, numero_acta_movimiento: e.target.value})} disabled={!modoEdicion} style={{ width: '100%', background: 'transparent', border: modoEdicion ? '1px solid #059669' : 'none', color: 'white', fontSize: '12px', outline: 'none' }} />
                          </div>
                        </div>

                        <div style={{ backgroundColor: '#09090b', padding: '6px 8px', borderRadius: '6px', border: '1px solid #27272a' }}>
                          <span style={{ color: '#71717a', fontSize: '10px', textTransform: 'uppercase' }}>Destino</span>
                          <input type="text" value={registroSeleccionado.destino || ''} onChange={(e) => setRegistroSeleccionado({...registroSeleccionado, destino: e.target.value})} disabled={!modoEdicion} style={{ width: '100%', background: 'transparent', border: modoEdicion ? '1px solid #059669' : 'none', color: 'white', fontSize: '12px', outline: 'none' }} />
                        </div>

                        <div style={{ backgroundColor: '#09090b', padding: '6px 8px', borderRadius: '6px', border: '1px solid #27272a' }}>
                          <span style={{ color: '#71717a', fontSize: '10px', textTransform: 'uppercase' }}>Observaciones</span>
                          <textarea value={registroSeleccionado.observacion || ''} onChange={(e) => setRegistroSeleccionado({...registroSeleccionado, observacion: e.target.value})} disabled={!modoEdicion} rows="2" style={{ width: '100%', background: 'transparent', border: modoEdicion ? '1px solid #059669' : 'none', color: 'white', fontSize: '12px', outline: 'none', resize: 'none' }} />
                        </div>
                      </div>

                      <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '6px', borderTop: '1px solid #27272a' }}>
                        {!modoEdicion ? (
                          <button onClick={() => setModoEdicion(true)} style={{ width: '100%', backgroundColor: '#b45309', color: 'white', border: 'none', padding: '8px', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer' }}>Modificar</button>
                        ) : (
                          <button onClick={guardarCambiosModal} style={{ width: '100%', backgroundColor: '#047857', color: 'white', border: 'none', padding: '8px', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer' }}>Guardar cambios</button>
                        )}
                        <button onClick={cerrarModal} style={{ width: '100%', backgroundColor: '#27272a', color: 'white', border: 'none', padding: '8px', borderRadius: '6px', cursor: 'pointer' }}>Cerrar</button>
                      </div>
                    </div>
                  </div>
                )}
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
                        <div key={item.nombreComun} className="ficha-inventario cursor-pointer" onClick={() => abrirModalActivos(item.nombreComun)}>
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

                  {/* MODAL FICHAS ACTIVAS */}
                  {modalActivosAbierto && (
                    <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 60, padding: '16px' }} onClick={() => setModalActivosAbierto(false)}>
                      <div style={{ backgroundColor: '#18181b', border: '1px solid #3f3f46', borderRadius: '16px', padding: '24px', width: '100%', maxWidth: '600px', maxHeight: '80vh', display: 'flex', flexDirection: 'column' }} onClick={e => e.stopPropagation()}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid #27272a', paddingBottom: '16px', marginBottom: '16px' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                            <div style={{ backgroundColor: 'rgba(6, 78, 59, 0.5)', padding: '12px', borderRadius: '50%', border: '1px solid rgba(4, 120, 87, 0.5)', fontSize: '24px' }}>🩺</div>
                            <div>
                              <h3 style={{ margin: 0, fontSize: '24px', fontWeight: 'bold', color: 'white' }}>{especieModalActivos}</h3>
                              <p style={{ margin: 0, fontSize: '14px', fontFamily: 'monospace', color: '#34d399' }}>Pacientes actualmente en el centro</p>
                            </div>
                          </div>
                          <button onClick={() => setModalActivosAbierto(false)} style={{ color: '#71717a', background: 'none', border: 'none', fontSize: '20px', cursor: 'pointer' }}>✕</button>
                        </div>
                        
                        <div style={{ overflowY: 'auto', paddingRight: '8px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                          {getFichasPorEspecie(especieModalActivos).length === 0 ? (
                            <p style={{ color: '#71717a', textAlign: 'center', fontStyle: 'italic', padding: '16px 0' }}>No se encontraron detalles de las fichas para esta especie.</p>
                          ) : (
                            getFichasPorEspecie(especieModalActivos).map(p => (
                              <div key={p.numero_ficha} style={{ backgroundColor: '#09090b', padding: '16px', borderRadius: '8px', border: '1px solid #27272a', transition: 'border-color 0.2s' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px', borderBottom: '1px solid #27272a', paddingBottom: '8px' }}>
                                  <span style={{ color: '#34d399', fontWeight: 'bold', fontFamily: 'monospace', fontSize: '18px' }}>{p.numero_ficha}</span>
                                  <span style={{ backgroundColor: '#27272a', color: '#d4d4d8', fontSize: '12px', padding: '4px 8px', borderRadius: '4px', textTransform: 'uppercase', letterSpacing: '1px' }}>Saldo: {p.saldo_actual}</span>
                                </div>
                                <div>
                                  <span style={{ color: '#71717a', display: 'block', fontSize: '12px', textTransform: 'uppercase', marginBottom: '4px' }}>Observación Actual</span>
                                  <p style={{ color: 'white', fontSize: '14px', margin: 0 }}>{p.observacion}</p>
                                </div>
                              </div>
                            ))
                          )}
                        </div>

                        <button onClick={() => setModalActivosAbierto(false)} style={{ marginTop: '24px', width: '100%', backgroundColor: '#27272a', color: 'white', fontWeight: 'bold', padding: '12px', borderRadius: '8px', border: 'none', cursor: 'pointer' }}>Cerrar</button>
                      </div>
                    </div>
                  )}

                </div>
              </div>
            )}

            {/* PESTAÑA 3: PANEL DE MÉTRICAS */}
            {activeTab === 'metricas' && (
              <div className="animate-fade">
                <div className="panel-oscuro">
                  <h2>Métricas Clínicas e Indicadores CEREFAS</h2>
                  <p style={{ color: 'var(--text-secondary)', marginBottom: '15px', fontSize: '14px' }}>
                    Visualiza la tasa de éxito clínico y la distribución de destinos y categorías de la fauna ingresada.
                  </p>
                  
                  {/* Filtros de Métricas */}
                  <div style={{ display: 'flex', gap: '15px', marginBottom: '30px' }}>
                    <div style={{ flex: 1, maxWidth: '200px' }}>
                      <label style={{ fontSize: '11px', color: 'var(--text-secondary)', textTransform: 'uppercase', fontWeight: 700, marginBottom: '5px', display: 'block' }}>Rango de Tiempo</label>
                      <select value={metricaFiltroTiempo} onChange={e => setMetricaFiltroTiempo(e.target.value)} className="select-cerefa" style={{ width: '100%' }}>
                        <option value="Todos">Histórico Completo</option>
                        <option value="Semanal">Última Semana</option>
                        <option value="Mensual">Último Mes</option>
                        <option value="Anual">Último Año</option>
                      </select>
                    </div>
                    <div style={{ flex: 1, maxWidth: '300px' }}>
                      <label style={{ fontSize: '11px', color: 'var(--text-secondary)', textTransform: 'uppercase', fontWeight: 700, marginBottom: '5px', display: 'block' }}>Filtrar por Especie</label>
                      <select value={metricaFiltroEspecie} onChange={e => setMetricaFiltroEspecie(e.target.value)} className="select-cerefa" style={{ width: '100%' }}>
                        <option value="Todas">Todas las Especies</option>
                        {Object.keys(diccionarioAnimales).sort().map(esp => (
                          <option key={esp} value={esp}>{esp}</option>
                        ))}
                      </select>
                    </div>
                  </div>

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
                                ? Math.round((registrosMetricas.filter(r => r.tipo_evento === 'Egreso' && (r.destino === 'Clínica' || r.destino === 'Clínica de Apoyo' || r.destino === 'Clinica')).reduce((acc, curr) => acc + (parseInt(curr.numero_ejemplar) || 0), 0) / totalEgresos) * 100) 
                                : 0}%
                            </span>
                          </div>
                          <div className="chart-bar-bg">
                            <div className="chart-bar-fill info" style={{ width: `${totalEgresos > 0 ? (registrosMetricas.filter(r => r.tipo_evento === 'Egreso' && (r.destino === 'Clínica' || r.destino === 'Clínica de Apoyo' || r.destino === 'Clinica')).reduce((acc, curr) => acc + (parseInt(curr.numero_ejemplar) || 0), 0) / totalEgresos) * 100 : 0}%` }}></div>
                          </div>
                        </div>

                        <div className="chart-bar-item">
                          <div className="chart-bar-header">
                            <span>Fallecido / Deceso / Eutanasia</span>
                            <span>
                              {totalEgresos > 0 
                                ? Math.round((registrosMetricas.filter(r => r.tipo_evento === 'Egreso' && (r.destino === 'Fallece' || r.destino === 'Eutanasia' || r.destino === 'Fallecido')).reduce((acc, curr) => acc + (parseInt(curr.numero_ejemplar) || 0), 0) / totalEgresos) * 100) 
                                : 0}%
                            </span>
                          </div>
                          <div className="chart-bar-bg">
                            <div className="chart-bar-fill warning" style={{ width: `${totalEgresos > 0 ? (registrosMetricas.filter(r => r.tipo_evento === 'Egreso' && (r.destino === 'Fallece' || r.destino === 'Eutanasia' || r.destino === 'Fallecido')).reduce((acc, curr) => acc + (parseInt(curr.numero_ejemplar) || 0), 0) / totalEgresos) * 100 : 0}%` }}></div>
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
                                ? Math.round((registrosMetricas.filter(r => r.tipo_evento === 'Ingreso' && r.categoria_evento === 'SAG').reduce((acc, curr) => acc + (parseInt(curr.numero_ejemplar) || 0), 0) / totalIngresos) * 100) 
                                : 0}%
                            </span>
                          </div>
                          <div className="chart-bar-bg">
                            <div className="chart-bar-fill primary" style={{ width: `${totalIngresos > 0 ? (registrosMetricas.filter(r => r.tipo_evento === 'Ingreso' && r.categoria_evento === 'SAG').reduce((acc, curr) => acc + (parseInt(curr.numero_ejemplar) || 0), 0) / totalIngresos) * 100 : 0}%` }}></div>
                          </div>
                        </div>

                        <div className="chart-bar-item">
                          <div className="chart-bar-header">
                            <span>Particulares / Entregas Directas</span>
                            <span>
                              {totalIngresos > 0 
                                ? Math.round((registrosMetricas.filter(r => r.tipo_evento === 'Ingreso' && r.categoria_evento === 'Particular').reduce((acc, curr) => acc + (parseInt(curr.numero_ejemplar) || 0), 0) / totalIngresos) * 100) 
                                : 0}%
                            </span>
                          </div>
                          <div className="chart-bar-bg">
                            <div className="chart-bar-fill info" style={{ width: `${totalIngresos > 0 ? (registrosMetricas.filter(r => r.tipo_evento === 'Ingreso' && r.categoria_evento === 'Particular').reduce((acc, curr) => acc + (parseInt(curr.numero_ejemplar) || 0), 0) / totalIngresos) * 100 : 0}%` }}></div>
                          </div>
                        </div>

                        <div className="chart-bar-item">
                          <div className="chart-bar-header">
                            <span>Rescates Propios CEREFAS</span>
                            <span>
                              {totalIngresos > 0 
                                ? Math.round((registrosMetricas.filter(r => r.tipo_evento === 'Ingreso' && r.categoria_evento === 'Rescate').reduce((acc, curr) => acc + (parseInt(curr.numero_ejemplar) || 0), 0) / totalIngresos) * 100) 
                                : 0}%
                            </span>
                          </div>
                          <div className="chart-bar-bg">
                            <div className="chart-bar-fill warning" style={{ width: `${totalIngresos > 0 ? (registrosMetricas.filter(r => r.tipo_evento === 'Ingreso' && r.categoria_evento === 'Rescate').reduce((acc, curr) => acc + (parseInt(curr.numero_ejemplar) || 0), 0) / totalIngresos) * 100 : 0}%` }}></div>
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
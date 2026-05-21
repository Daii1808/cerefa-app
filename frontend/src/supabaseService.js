import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://yyxvwcnnfhqbrobmhqjy.supabase.co';
const supabaseAnonKey = 'sb_publishable_Nk6sOhgqW9CH-Y4qoU7HEQ_9pTSh4ZI';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// Guardar un nuevo evento de registro médico
export const guardarEvento = async (nuevoEvento) => {
  const { data, error } = await supabase
    .from('registro_evento')
    .insert([
      {
        fecha: nuevoEvento.fecha,
        numero_ficha: nuevoEvento.numero_ficha,
        numero_acta_movimiento: nuevoEvento.numero_acta_movimiento,
        nombre_comun: nuevoEvento.nombre_comun,
        nombre_cientifico: nuevoEvento.nombre_cientifico,
        numero_ejemplar: parseInt(nuevoEvento.numero_ejemplar) || 1,
        tipo_evento: nuevoEvento.tipo_evento,
        categoria_evento: nuevoEvento.categoria_evento,
        saldo_anterior: parseInt(nuevoEvento.saldo_anterior) || 0,
        saldo_actual: parseInt(nuevoEvento.saldo_actual) || 0,
        destino: nuevoEvento.destino,
        observacion: nuevoEvento.observacion || 'Sin observaciones',
        doctor_email: nuevoEvento.doctor_email
      }
    ])
    .select();
  
  if (error) {
    console.error("Error al guardar en registro_evento:", error);
    throw error;
  }
  return data;
};

// Obtener todos los eventos ordenados por fecha de creación descendente
export const obtenerEventos = async () => {
  const { data, error } = await supabase
    .from('registro_evento')
    .select('*')
    .order('fecha', { ascending: false });
    
  if (error) {
    console.error("Error al obtener eventos de registro_evento:", error);
    throw error;
  }
  return data;
};

// Verificar las credenciales de un médico
export const verificarMedico = async (correo, password) => {
  const { data, error } = await supabase
    .from('usuarios')
    .select('correo')
    .eq('correo', correo.trim().toLowerCase())
    .eq('password', password.trim());
    
  if (error) {
    console.error("Error al verificar médico en Supabase:", error);
    throw error;
  }
  return data && data.length > 0;
};
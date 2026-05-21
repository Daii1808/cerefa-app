import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://yyxvwcnnfhqbrobmhqjy.supabase.co';
const supabaseAnonKey = 'sb_publishable_Nk6sOhgqW9CH-Y4qoU7HEQ_9pTSh4ZI';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// Asegúrate de que esta función exista y diga 'export'
export const guardarEvento = async (nuevoEvento) => {
  const { data, error } = await supabase.from('eventos').insert([nuevoEvento]);
  if (error) throw error;
  return data;
};

// Asegúrate de que esta función también diga 'export'
export const obtenerEventos = async () => {
  const { data, error } = await supabase.from('eventos').select('*');
  if (error) throw error;
  return data;
};
import AsyncStorage from '@react-native-async-storage/async-storage';
import { MAX_MENSAJE, TIMEOUT_MS, WEBHOOK_TOKEN, WEBHOOK_URL } from './config';

export type RespuestaAgente = {
  texto: string;
  fuentes: string[];
  bloqueado: boolean;
  motivo: string | null;
  sesionId: string | null;
};

export class ErrorApi extends Error {}

const claveSesion = (codigo: string) => `ibanu:sesion:${codigo}`;
const CLAVE_CODIGO = 'ibanu:codigo';

export async function leerSesion(codigo: string): Promise<string | null> {
  try {
    return await AsyncStorage.getItem(claveSesion(codigo));
  } catch {
    return null;
  }
}

export async function guardarSesion(codigo: string, sesionId: string) {
  try {
    await AsyncStorage.setItem(claveSesion(codigo), sesionId);
  } catch {}
}

export async function borrarSesion(codigo: string) {
  try {
    await AsyncStorage.removeItem(claveSesion(codigo));
  } catch {}
}

export async function leerCodigoGuardado(): Promise<string | null> {
  try {
    return await AsyncStorage.getItem(CLAVE_CODIGO);
  } catch {
    return null;
  }
}

export async function guardarCodigo(codigo: string | null) {
  try {
    if (codigo) await AsyncStorage.setItem(CLAVE_CODIGO, codigo);
    else await AsyncStorage.removeItem(CLAVE_CODIGO);
  } catch {}
}

export async function consultarAgente(
  codigo: string,
  mensaje: string,
  sesionId: string | null,
): Promise<RespuestaAgente> {
  const cuerpo: Record<string, string> = {
    codigo_estudiante: codigo,
    mensaje: mensaje.slice(0, MAX_MENSAJE),
  };
  if (sesionId) cuerpo.sesion_id = sesionId;

  const control = new AbortController();
  const temporizador = setTimeout(() => control.abort(), TIMEOUT_MS);

  let respuesta: Response;
  try {
    respuesta = await fetch(WEBHOOK_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Ibanu-Token': WEBHOOK_TOKEN,
      },
      body: JSON.stringify(cuerpo),
      signal: control.signal,
    });
  } catch (e) {
    if (e instanceof Error && e.name === 'AbortError') {
      throw new ErrorApi(
        'La respuesta está tardando demasiado. Intenta de nuevo en unos segundos.',
      );
    }
    throw new ErrorApi(
      'No pude conectarme con iBanú. Revisa tu conexión a internet e intenta de nuevo.',
    );
  } finally {
    clearTimeout(temporizador);
  }

  let datos: any = null;
  try {
    datos = await respuesta.json();
  } catch {}

  if (respuesta.status === 401) {
    throw new ErrorApi('Acceso no autorizado: el token de la aplicación no es válido.');
  }
  if (respuesta.status === 400) {
    const detalle = datos?.error ? ` (${datos.error})` : '';
    throw new ErrorApi(
      `La consulta no es válida${detalle}. Revisa tu código de estudiante y el mensaje.`,
    );
  }
  if (respuesta.status === 404) {
    throw new ErrorApi('El asistente todavía no está disponible (el flujo de n8n no está activo).');
  }
  if (!respuesta.ok) {
    throw new ErrorApi(
      `El servicio respondió con un error (${respuesta.status}). Intenta más tarde.`,
    );
  }
  if (!datos || datos.ok === false) {
    throw new ErrorApi(datos?.error || 'El servicio devolvió una respuesta inesperada.');
  }

  return {
    texto: datos.respuesta || 'No recibí una respuesta del asistente.',
    fuentes: Array.isArray(datos.fuentes) ? datos.fuentes.map(String) : [],
    bloqueado: datos.bloqueado === true,
    motivo: datos.motivo ?? null,
    sesionId: datos.sesion_id ?? null,
  };
}

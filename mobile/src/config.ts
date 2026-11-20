// Configuración única del cliente. Cada valor se puede sobrescribir
// con una variable EXPO_PUBLIC_* (archivo .env o entorno al iniciar Expo).
export const WEBHOOK_URL: string =
  process.env.EXPO_PUBLIC_WEBHOOK_URL ||
  'https://ksaavedra363.app.n8n.cloud/webhook/ibanu/orientador';

export const WEBHOOK_TOKEN: string =
  process.env.EXPO_PUBLIC_WEBHOOK_TOKEN || 'ibk_7f3c9a1e5d2b48c6a0e4f9b1d3c7a5e2';

// El agente puede tardar hasta ~30 s; se deja margen.
export const TIMEOUT_MS: number = Number(process.env.EXPO_PUBLIC_TIMEOUT_MS) || 60000;

export const MAX_MENSAJE = 1000;

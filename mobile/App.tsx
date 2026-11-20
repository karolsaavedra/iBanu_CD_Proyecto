import React, { useEffect, useRef, useState } from 'react';
import {
  SafeAreaView,
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import Markdown from 'react-native-markdown-display';
import {
  ErrorApi,
  borrarSesion,
  consultarAgente,
  guardarCodigo,
  guardarSesion,
  leerCodigoGuardado,
  leerSesion,
} from './src/api';
import { CONSULTAS } from './src/consultas';
import { MAX_MENSAJE } from './src/config';

type Mensaje = {
  id: number;
  texto: string;
  usuario: boolean;
  fuentes?: string[];
  bloqueado?: boolean;
  motivo?: string | null;
  error?: boolean;
};

const reglasMarkdown = StyleSheet.create({
  body: { color: '#334E68', fontSize: 14, lineHeight: 21 },
  strong: { fontWeight: '800', color: '#102A43' },
  heading1: { color: '#102A43', fontSize: 18, fontWeight: '800', marginVertical: 6 },
  heading2: { color: '#102A43', fontSize: 16, fontWeight: '800', marginVertical: 6 },
  heading3: { color: '#102A43', fontSize: 15, fontWeight: '700', marginVertical: 4 },
  bullet_list: { marginVertical: 4 },
  ordered_list: { marginVertical: 4 },
  code_inline: { backgroundColor: '#E2F3F1', color: '#102A43', borderRadius: 4 },
  fence: { backgroundColor: '#F4F7FA', color: '#102A43', borderRadius: 8, padding: 8 },
  table: { borderColor: '#D9E2EC' },
  th: { padding: 4, fontWeight: '700' },
  td: { padding: 4 },
  link: { color: '#168C83' },
  paragraph: { marginTop: 0, marginBottom: 8 },
});

export default function App() {
  const [codigo, setCodigo] = useState('');
  const [sesion, setSesion] = useState(false);
  const [sesionId, setSesionId] = useState<string | null>(null);
  const [mensaje, setMensaje] = useState('');
  const [mensajes, setMensajes] = useState<Mensaje[]>([]);
  const [cargando, setCargando] = useState(false);
  const [iniciando, setIniciando] = useState(true);
  const scrollRef = useRef<React.ComponentRef<typeof ScrollView>>(null);

  useEffect(() => {
    (async () => {
      const guardado = await leerCodigoGuardado();
      if (guardado) {
        setCodigo(guardado);
        setSesionId(await leerSesion(guardado));
        setSesion(true);
      }
      setIniciando(false);
    })();
  }, []);

  const iniciarSesion = async () => {
    const limpio = codigo.trim().toUpperCase();
    if (!/^[A-Z0-9]{4,20}$/.test(limpio)) {
      Alert.alert('Código no válido', 'Ingresa tu código de estudiante. Ejemplo: U00112048');
      return;
    }
    setCodigo(limpio);
    setSesionId(await leerSesion(limpio));
    await guardarCodigo(limpio);
    setSesion(true);
  };

  const salir = async () => {
    await guardarCodigo(null);
    setSesion(false);
    setMensajes([]);
    setCodigo('');
    setSesionId(null);
  };

  const nuevaConversacion = async () => {
    await borrarSesion(codigo);
    setSesionId(null);
    setMensajes([]);
  };

  const enviarMensaje = async (texto: string) => {
    const consulta = texto.trim();
    if (!consulta || cargando) return;

    setMensajes((prev) => [...prev, { id: Date.now(), texto: consulta, usuario: true }]);
    setMensaje('');
    setCargando(true);

    try {
      const r = await consultarAgente(codigo, consulta, sesionId);
      if (r.sesionId) {
        setSesionId(r.sesionId);
        await guardarSesion(codigo, r.sesionId);
      }
      setMensajes((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          texto: r.texto,
          usuario: false,
          fuentes: r.fuentes,
          bloqueado: r.bloqueado,
          motivo: r.motivo,
        },
      ]);
    } catch (error) {
      setMensajes((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          texto:
            error instanceof ErrorApi ? error.message : 'Ocurrió un error inesperado. Intenta de nuevo.',
          usuario: false,
          error: true,
        },
      ]);
    } finally {
      setCargando(false);
    }
  };

  if (iniciando) {
    return (
      <SafeAreaView style={[styles.fondo, { justifyContent: 'center' }]}>
        <StatusBar style="light" />
        <ActivityIndicator color="#FFFFFF" />
      </SafeAreaView>
    );
  }

  if (!sesion) {
    return (
      <SafeAreaView style={styles.fondo}>
        <StatusBar style="light" />
        <View style={styles.loginContainer}>
          <View style={styles.logo}>
            <Text style={styles.logoTexto}>iB</Text>
          </View>
          <Text style={styles.nombre}>iBanú</Text>
          <Text style={styles.subtitulo}>Tu orientación académica, más cerca.</Text>

          <View style={styles.loginCard}>
            <Text style={styles.tituloLogin}>¡Hola!</Text>
            <Text style={styles.descripcion}>
              Ingresa tu código de estudiante para comenzar.
            </Text>
            <Text style={styles.label}>Código de estudiante</Text>
            <TextInput
              style={styles.inputCodigo}
              placeholder="Ej. U00112048"
              placeholderTextColor="#8795A5"
              value={codigo}
              onChangeText={setCodigo}
              autoCapitalize="characters"
              autoCorrect={false}
              maxLength={20}
              onSubmitEditing={iniciarSesion}
            />
            <TouchableOpacity style={styles.botonPrincipal} onPress={iniciarSesion}>
              <Text style={styles.textoBoton}>Continuar</Text>
              <Text style={styles.flecha}>→</Text>
            </TouchableOpacity>
          </View>
          <Text style={styles.pieLogin}>Asistente académico | Ingeniería de Sistemas</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.fondoClaro}>
      <StatusBar style="light" />
      <View style={styles.header}>
        <View style={styles.headerMarca}>
          <View style={styles.logoPequeno}>
            <Text style={styles.logoPequenoTexto}>iB</Text>
          </View>
          <View>
            <Text style={styles.headerNombre}>iBanú</Text>
            <Text style={styles.estado}>● {codigo}</Text>
          </View>
        </View>
        <View style={{ flexDirection: 'row' }}>
          <TouchableOpacity onPress={nuevaConversacion}>
            <Text style={styles.cerrarSesion}>Nueva</Text>
          </TouchableOpacity>
          <TouchableOpacity onPress={salir}>
            <Text style={styles.cerrarSesion}>Salir</Text>
          </TouchableOpacity>
        </View>
      </View>

      <KeyboardAvoidingView
        style={styles.contenido}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        keyboardVerticalOffset={10}
      >
        <ScrollView
          ref={scrollRef}
          style={styles.scroll}
          contentContainerStyle={styles.scrollContenido}
          keyboardShouldPersistTaps="handled"
          onContentSizeChange={() => scrollRef.current?.scrollToEnd({ animated: true })}
        >
          {mensajes.length === 0 && (
            <View style={styles.bienvenida}>
              <Text style={styles.saludo}>Hola, estudiante 👋</Text>
              <Text style={styles.bienvenidaTexto}>
                Soy iBanú. Elige una consulta o escríbeme tu pregunta.
              </Text>
            </View>
          )}

          <View style={styles.frecuentes}>
            <Text style={styles.seccionTitulo}>Consultas rápidas</Text>
            <View style={styles.rejilla}>
              {CONSULTAS.map((c) => (
                <TouchableOpacity
                  key={c.clave}
                  style={[styles.tarjeta, cargando && styles.botonDesactivado]}
                  onPress={() => enviarMensaje(c.pregunta)}
                  disabled={cargando}
                >
                  <Text style={styles.preguntaIcono}>{c.icono}</Text>
                  <Text style={styles.preguntaTexto}>{c.titulo}</Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          {mensajes.map((item) => (
            <View
              key={item.id}
              style={[styles.filaMensaje, item.usuario ? styles.filaUsuario : styles.filaBot]}
            >
              {!item.usuario && (
                <View style={styles.avatarBot}>
                  <Text style={styles.avatarTexto}>iB</Text>
                </View>
              )}
              <View
                style={[
                  styles.burbuja,
                  item.usuario ? styles.burbujaUsuario : styles.burbujaBot,
                  item.error && styles.burbujaError,
                  item.bloqueado && styles.burbujaBloqueada,
                ]}
              >
                {item.usuario ? (
                  <Text style={[styles.textoMensaje, styles.textoUsuario]}>{item.texto}</Text>
                ) : item.error ? (
                  <Text style={[styles.textoMensaje, styles.textoError]}>{item.texto}</Text>
                ) : (
                  <>
                    {item.bloqueado && (
                      <Text style={styles.avisoBloqueo}>
                        Consulta no permitida{item.motivo ? `: ${item.motivo}` : ''}
                      </Text>
                    )}
                    <Markdown style={reglasMarkdown}>{item.texto}</Markdown>
                    {!!item.fuentes?.length && (
                      <View style={styles.fuentes}>
                        <Text style={styles.fuentesTitulo}>Fuentes</Text>
                        {item.fuentes.map((f, i) => (
                          <Text key={i} style={styles.fuenteItem}>
                            • {f}
                          </Text>
                        ))}
                      </View>
                    )}
                  </>
                )}
              </View>
            </View>
          ))}

          {cargando && (
            <View style={styles.cargando}>
              <ActivityIndicator color="#168C83" />
              <Text style={styles.textoCargando}>
                iBanú está analizando tu información, puede tardar hasta 30 segundos...
              </Text>
            </View>
          )}
        </ScrollView>

        <View style={styles.compositor}>
          <TextInput
            style={styles.inputMensaje}
            placeholder="Escribe tu pregunta..."
            placeholderTextColor="#8795A5"
            value={mensaje}
            onChangeText={setMensaje}
            multiline
            maxLength={MAX_MENSAJE}
          />
          <TouchableOpacity
            style={[styles.botonEnviar, (!mensaje.trim() || cargando) && styles.botonDesactivado]}
            onPress={() => enviarMensaje(mensaje)}
            disabled={!mensaje.trim() || cargando}
          >
            <Text style={styles.enviarIcono}>↑</Text>
          </TouchableOpacity>
        </View>
        <Text style={styles.notaDatos}>Información académica de demostración | Datos sintéticos</Text>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const extraEstilos = {
  rejilla: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between', marginTop: 12 },
  tarjeta: {
    width: '48.5%', backgroundColor: '#FFFFFF', borderRadius: 13, paddingVertical: 14,
    alignItems: 'center', marginBottom: 9, borderWidth: 1, borderColor: '#E5EBF0',
  },
  burbujaError: { backgroundColor: '#FDECEA' },
  burbujaBloqueada: { backgroundColor: '#FFF6E5' },
  textoError: { color: '#9B2C2C' },
  avisoBloqueo: { color: '#B7791F', fontWeight: '800', fontSize: 12, marginBottom: 6 },
  fuentes: { borderTopWidth: 1, borderTopColor: '#E5EBF0', marginTop: 6, paddingTop: 8 },
  fuentesTitulo: { color: '#168C83', fontSize: 11, fontWeight: '800', marginBottom: 3 },
  fuenteItem: { color: '#627D98', fontSize: 11, lineHeight: 16 },
} as const;

const styles = StyleSheet.create({
  ...extraEstilos,
  fondo: { flex: 1, backgroundColor: '#102A43' },
  fondoClaro: { flex: 1, backgroundColor: '#F4F7FA' },
  loginContainer: { flex: 1, justifyContent: 'center', paddingHorizontal: 28 },
  logo: {
    width: 76, height: 76, borderRadius: 24, backgroundColor: '#20A69A',
    alignItems: 'center', justifyContent: 'center', alignSelf: 'center',
    marginBottom: 14,
  },
  logoTexto: { color: '#FFFFFF', fontSize: 30, fontWeight: '800' },
  nombre: { color: '#FFFFFF', fontSize: 34, fontWeight: '800', textAlign: 'center' },
  subtitulo: { color: '#C4D4E3', fontSize: 14, textAlign: 'center', marginTop: 8, marginBottom: 38 },
  loginCard: { backgroundColor: '#FFFFFF', borderRadius: 22, padding: 24 },
  tituloLogin: { color: '#102A43', fontSize: 25, fontWeight: '800', marginBottom: 8 },
  descripcion: { color: '#627D98', fontSize: 14, lineHeight: 21, marginBottom: 25 },
  label: { color: '#334E68', fontSize: 13, fontWeight: '700', marginBottom: 9 },
  inputCodigo: {
    height: 52, borderWidth: 1, borderColor: '#D9E2EC', borderRadius: 12,
    paddingHorizontal: 15, color: '#102A43', fontSize: 16, marginBottom: 18,
  },
  botonPrincipal: {
    height: 52, backgroundColor: '#168C83', borderRadius: 12,
    alignItems: 'center', justifyContent: 'center', flexDirection: 'row',
  },
  textoBoton: { color: '#FFFFFF', fontWeight: '700', fontSize: 16 },
  flecha: { color: '#FFFFFF', fontSize: 21, marginLeft: 10 },
  pieLogin: { color: '#A9BDCE', textAlign: 'center', fontSize: 11, marginTop: 28 },
  header: {
    backgroundColor: '#102A43', paddingHorizontal: 20, paddingVertical: 15,
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
  },
  headerMarca: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  logoPequeno: {
    width: 42, height: 42, borderRadius: 14, backgroundColor: '#20A69A',
    alignItems: 'center', justifyContent: 'center',
  },
  logoPequenoTexto: { color: '#FFFFFF', fontSize: 17, fontWeight: '800' },
  headerNombre: { color: '#FFFFFF', fontSize: 18, fontWeight: '800' },
  estado: { color: '#9DD9D2', fontSize: 11, marginTop: 2 },
  cerrarSesion: { color: '#C4D4E3', fontSize: 13, padding: 8 },
  contenido: { flex: 1 },
  scroll: { flex: 1 },
  scrollContenido: { padding: 18, paddingBottom: 25 },
  bienvenida: {
    backgroundColor: '#E2F3F1', borderRadius: 18, padding: 18, marginBottom: 23,
  },
  saludo: { color: '#102A43', fontSize: 21, fontWeight: '800', marginBottom: 7 },
  bienvenidaTexto: { color: '#486581', fontSize: 13, lineHeight: 20 },
  codigoActivo: { color: '#168C83', fontSize: 11, fontWeight: '700', marginTop: 12 },
  frecuentes: { marginBottom: 15 },
  seccionTitulo: { color: '#102A43', fontSize: 17, fontWeight: '800' },
  seccionDescripcion: { color: '#627D98', fontSize: 12, marginTop: 5, marginBottom: 14 },
  pregunta: {
    flexDirection: 'row', alignItems: 'center', backgroundColor: '#FFFFFF',
    padding: 14, borderRadius: 13, marginBottom: 9, borderWidth: 1, borderColor: '#E5EBF0',
  },
  preguntaIcono: { fontSize: 19, marginRight: 12 },
  preguntaTexto: { color: '#334E68', fontSize: 13, fontWeight: '600', lineHeight: 19 },
  preguntaFlecha: { color: '#168C83', fontSize: 23, marginLeft: 8 },
  filaMensaje: { flexDirection: 'row', marginBottom: 14, alignItems: 'flex-end' },
  filaUsuario: { justifyContent: 'flex-end' },
  filaBot: { justifyContent: 'flex-start' },
  avatarBot: {
    width: 30, height: 30, borderRadius: 11, backgroundColor: '#168C83',
    alignItems: 'center', justifyContent: 'center', marginRight: 8,
  },
  avatarTexto: { color: '#FFFFFF', fontSize: 11, fontWeight: '800' },
  burbuja: { maxWidth: '88%', padding: 13, borderRadius: 16 },
  burbujaUsuario: { backgroundColor: '#168C83', borderBottomRightRadius: 4 },
  burbujaBot: { backgroundColor: '#FFFFFF', borderBottomLeftRadius: 4 },
  textoMensaje: { fontSize: 14, lineHeight: 21 },
  textoUsuario: { color: '#FFFFFF' },
  textoBot: { color: '#334E68' },
  cargando: { flexDirection: 'row', alignItems: 'center', gap: 9, padding: 10 },
  textoCargando: { color: '#627D98', fontSize: 12 },
  compositor: {
    flexDirection: 'row', alignItems: 'center', backgroundColor: '#FFFFFF',
    marginHorizontal: 14, marginTop: 8, padding: 8, borderRadius: 17,
    borderWidth: 1, borderColor: '#D9E2EC',
  },
  inputMensaje: { flex: 1, color: '#102A43', fontSize: 14, paddingHorizontal: 10, maxHeight: 100 },
  botonEnviar: {
    width: 42, height: 42, borderRadius: 13, backgroundColor: '#168C83',
    alignItems: 'center', justifyContent: 'center',
  },
  botonDesactivado: { opacity: 0.4 },
  enviarIcono: { color: '#FFFFFF', fontSize: 24, fontWeight: '700' },
  notaDatos: { color: '#829AB1', fontSize: 10, textAlign: 'center', paddingVertical: 8 },
});

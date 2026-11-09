# Diagnóstico

- **403 del proxy**: es una restricción de destino. Habilitar los dominios indicados en INSTALLATION.md, guardar los ajustes y volver a probar con una conexión nueva. No desactivar TLS ni extraer credenciales.
- **Navegador de Remotion**: `browser ensure` no pudo descargar remotion.media. El MP4 y PNG se verificaron con `CHROME_PATH=/usr/bin/chromium`. Tras habilitar el navegador recomendado, repetir render sin esa variable. No se usan APIs Canvas dependientes del navegador especial.
- **faster-whisper**: importaciones y VAD pasaron; `WhisperModel('tiny')` devolvió `ProxyError: 403 Forbidden`. No es un error de instalación. Habilitar Hugging Face o usar un directorio de modelo local. No se descargó un modelo enorme.
- **Tipos de dependencias**: Remotion 4.0.541 declara `Timer` sin proporcionar ese global. TypeScript 5.9 también chocó con WebCodecs. Se fijó TypeScript 6.0.3 y se usa `skipLibCheck` para declaraciones externas; el código propio mantiene strict. No se modificó node_modules.
- **Caché npm no escribible**: el home está restringido; usar `npm --cache /workspace/.cache/npm ...`. El instalador ya lo hace.
- **Output existente**: elegir otra ruta. Los scripts no sobrescriben medios; las exportaciones ASR derivadas se regeneran dentro del mismo job con checkpoint compatible.
- **Falta de recursos**: reducir RENDER_CONCURRENCY/FFMPEG_THREADS a 1, usar chunks de 60–300 segundos, elegir tiny/base y revisar el disco. No eliminar originales para obtener espacio.
- **Checkpoint incompatible**: no editar a mano su hash para forzarlo. Usar otro job y mantener el anterior para recuperación.
- **Sin modelo**: los tests con ASR simulado solo verifican recuperación y exportación, no calidad de español argentino.
- **Publicación**: si leer/guardar el borrador falla, el runtime puede seguir funcionando pero la configuración no está persistida por esa vía. El JSON local permite incorporarla a los ajustes. Publicar en la interfaz y validar después en una tarea nueva.

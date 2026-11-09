# Auditoría del entorno

Sesión solicitada el 8 de noviembre de 2026 (fecha del cliente). Las herramientas registraron ejecución desde 2026-11-09 02:55 UTC. Todos los resultados siguientes proceden de comandos reales; no se procesó material del proyecto futuro.

## Infraestructura

| Componente | Evidencia observada |
|---|---|
| Ejecutor | Cloud conectado y en ejecución; environment_status con observations_current=true y política enforced |
| OS / arquitectura | Debian GNU/Linux 13.6, Linux x86_64 |
| CPU | nproc=5; cgroup cpu.max=400000/100000, cuota efectiva de 4 CPU |
| Memoria | cgroup memory.max=34359738368 (32 GiB); sin swap |
| Disco | inicialmente ~60 GiB libres; tras instalación ~58 GiB |
| Usuario/permisos | usuario agent; escritura permitida en /workspace y /tmp; sin necesidad de elevación |
| GPU | CTranslate2 detectó 0 dispositivos CUDA; CPU soporta int8/int16/float32 |
| Node / npm | 24.22.1 / 11.9.0 |
| Python | 3.12.14; venv local .venv |
| Git | operativo; repositorio origin calderondante/Video-Studio-AI; rama inicial work sin commits, remoto sin refs |
| FFmpeg / FFprobe | 7.1.5-0+deb13u1; libx264/AAC, libass, subtitles, ass, loudnorm y afftdn |
| Chromium | /usr/bin/chromium, probado en renderizado real |

La autenticación de lectura Git existente funcionó (`git ls-remote origin`, sin refs en este repositorio vacío). No se solicitó token. Se inspeccionaron nombres/presencia de variables relevantes, sin valores: GH_TOKEN presente; ninguna variable de Hugging Face o TRANSCRIPTION_API_KEY observada. El estado cloud no declara secretos ni runtime_variables.

## Instalación

- npm install de dependencias exactas y generación de package-lock.json; posterior reinstalación real mediante npm ci.
- Remotion y CLI 4.0.541, React/React DOM 19.2.0; TypeScript 6.0.3. skipLibCheck evita declaraciones externas incompatibles de Remotion (Timer); strict se aplica al código propio.
- faster-whisper 1.2.1, CTranslate2 4.8.5, ONNX Runtime 1.31.1 y pysubs2 1.8.0. Todas las dependencias resueltas están fijadas en requirements.lock.
- 13 skills oficiales instaladas con `npx skills add remotion-dev/skills --yes --agent codex`; conservadas en .agents/skills junto con skills-lock.json. El README oficial se consultó desde raw.githubusercontent.com.
- npm/PyPI/GitHub funcionaron. La documentación en www.remotion.dev, el navegador de remotion.media y Hugging Face quedaron bloqueados. No se desactivó TLS ni se alteraron verificaciones.

## Validación real

| Componente | Estado | Prueba |
|---|---|---|
| Remotion horizontal | VERIFICADO | output/demo.mp4, H.264, 1920×1080, 30 FPS, 90 frames / 3 s; decodificación completa |
| Remotion vertical | VERIFICADO | output/vertical.mp4, H.264, 1080×1920, 30 FPS / 3 s; decodificación completa |
| PNG | VERIFICADO | output/cover.png 1920×1080, inspeccionado visualmente |
| Studio | VERIFICADO | servidor compiló; respuesta HTTP local correcta; también se ejercitó el wrapper de arranque |
| FFmpeg | VERIFICADO | sintético 3 s H.264/AAC; extracción WAV 16 kHz; normalize/afftdn/loudnorm; resize/FPS; concat compatible; PNG; integridad |
| Subtítulos | VERIFICADO | SRT y ASS; MP4 con subtítulos quemados; inspección visual y comparación de fotogramas dentro/fuera del intervalo |
| faster-whisper / VAD | PARCIAL | importación, capacidades CPU, VAD ONNX de silencio; inferencia de Whisper tiny bloqueada por ProxyError 403 |
| Reanudación ASR | VERIFICADO | test con modelo simulado, checkpoint reutilizado sin llamada adicional y rechazo de configuración incompatible; no acredita inferencia |
| API ASR opcional | PARCIAL | adaptador preparado, sin clave ni llamada externa, no probado contra proveedor |
| Instalación repetible | VERIFICADO | bash scripts/install.sh ejecutado tras instalación inicial, npm ci y pip desde locks, doctor y VAD correctos |
| Tipos/tests | VERIFICADO | npm run typecheck; 4 tests ejecutados y aprobados, incluidos procesamiento multimedia y reanudación |
| Proyecto Malvinas | VERIFICADO | projects/malvinas.json preparado; no se accedió a Drive |
| Guardado del borrador Cloud | BLOQUEADO | lectura falló dos veces: current environment draft could not be verified; guardado respondió INVALID_ARGUMENT: saving the draft could not be confirmed |
| Publicación/restauración | PARCIAL | no realizadas; requieren interfaz y posterior validación en tarea nueva |

Logs locales: work/install-validation.log, work/test-validation.log, work/vertical-render.log y work/studio*.log. Outputs y logs están excluidos de Git. Las pruebas multimedia usan material sintético, no privados. El mínimo de espacio del script es una protección básica, no una reserva para el tamaño completo de un video extenso.

## Pendientes externos

1. Incorporar install_script/start_skill de config/cloud-environment.json en ajustes de Codex Cloud: el guardado por herramienta no pudo confirmarse, no es un rechazo de autorización del agente.
2. Agregar dominios descritos en INSTALLATION.md preservando reglas existentes. Guardar y reintentar descarga tiny/inferencia con audio español autorizado; probar navegador recomendado.
3. Publicar desde la interfaz cuando los ajustes estén guardados. Verificar en una nueva tarea la restauración, las dependencias y arranque; no se presupone persistencia de procesos o temporales.

La plataforma audiovisual funciona para gráficos y procesamiento local, pero no se declara completada toda la misión mientras falten inferencia ASR y persistencia/publicación cloud confirmadas.

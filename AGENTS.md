# Instrucciones para agentes

Trabajar en el checkout existente `/workspace/Video-Studio-AI`. Cada tarea cloud ya está aislada: no crear worktrees salvo pedido explícito.

1. Leer README.md, ENVIRONMENT_AUDIT.md e INSTALLATION.md y revisar `git status`.
2. No descargar ni editar los tres MP4 del proyecto Malvinas sin autorización posterior. No sobrescribir originales ni registrar multimedia, modelos, transcripciones privadas o secretos en Git.
3. Reutilizar `.venv`, `node_modules` y `.cache`; ejecutar `bash scripts/install.sh` si falta o cambió una dependencia. Mantener versiones exactas y lockfiles.
4. `npm run typecheck`, `npm test`, `.venv/bin/python scripts/transcribe.py --check` son comprobaciones mínimas. Para cambios visuales renderizar a un destino nuevo e inspeccionar PNG/MP4. Usar las skills oficiales en `.agents/skills` según la tarea.
5. Por defecto usar 2 procesos de render, 2 hilos FFmpeg/ASR y chunks ASR de 300 segundos. Vigilar memoria y disco. No descargar modelos grandes sin evaluar recursos. Los cortes rígidos requieren revisión humana de palabras en fronteras.
6. Usar FFmpeg para subtítulos y procesamiento de videos extensos; Remotion para gráficos. Los scripts FFmpeg validan salida temporal antes de publicarla. No borrar checkpoints o intermedios recuperables hasta validar los resultados definitivos.
7. La red usa proxy y CA heredados. No desactivar TLS, checksums o firmas. No imprimir credenciales ni volcar el entorno.
8. El navegador recomendado por Remotion aún no se descarga por red. Chromium del sistema fue verificado con `CHROME_PATH=/usr/bin/chromium`. Las tareas nuevas deben revalidar las dependencias: procesos y temporales no son persistencia garantizada.
9. Diferenciar pruebas ASR simuladas de inferencia real. No afirmar que la transcripción o la publicación están verificadas sin evidencia.

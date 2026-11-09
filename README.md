# Video Studio AI

Estudio audiovisual modular para Linux y Codex Cloud. Remotion crea gráficos; FFmpeg procesa material extenso; Python transcribe y valida. No se descargaron ni editaron originales.

## Inicio

```bash
cd /workspace/Video-Studio-AI
bash scripts/install.sh
npm test
CHROME_PATH=/usr/bin/chromium npm run studio
```

El navegador del sistema permite trabajar en esta instancia; la descarga del navegador recomendado por Remotion está bloqueada por la red. Para usar el navegador recomendado, habilitar los dominios indicados en INSTALLATION.md, ejecutar `node node_modules/@remotion/cli/remotion-cli.js browser ensure` y omitir CHROME_PATH.

## Ejemplos verificados

```bash
CHROME_PATH=/usr/bin/chromium node scripts/render.mjs video Documental output/nuevo.mp4 templates/title.json
CHROME_PATH=/usr/bin/chromium node scripts/render.mjs still Documental output/nueva-portada.png
.venv/bin/python scripts/media.py synthetic unused output/nuevo-sintetico.mp4
.venv/bin/python scripts/media.py burn output/synthetic.mp4 output/nuevo-subtitulado.mp4 --subtitles output/sample.srt
.venv/bin/python scripts/media.py verify output/subtitled.mp4
.venv/bin/python scripts/transcribe.py --check
```

Los scripts rechazan destinos existentes. Usar nombres nuevos. Los outputs de prueba disponibles se excluyen de Git.

## Organización

- `src/`: composiciones 16:9 y 9:16, títulos, créditos y lower thirds.
- `scripts/`: render, FFmpeg, subtítulos, ASR, diagnóstico e instalación.
- `templates/`, `config/`: parámetros de gráficos y preset Documental.
- `tests/`: pruebas funcionales multimedia y unitarias de sincronización/reanudación.
- `projects/malvinas.json`: proyecto futuro, sin descargar su contenido.
- `input/`, `work/`, `output/`, `.cache/`: material privado, checkpoints y outputs; excluidos de Git.

Consultar [auditoría](ENVIRONMENT_AUDIT.md), [instalación](INSTALLATION.md), [flujo](VIDEO_WORKFLOW.md) y [problemas](TROUBLESHOOTING.md).

## Límites actuales

Faster-whisper y VAD están verificados; la inferencia real no se ejecutó porque Hugging Face devuelve 403 del proxy. La prueba de reanudación usa un modelo simulado y no acredita calidad de reconocimiento. La API opcional no se invocó. Las transcripciones requieren revisión humana, especialmente nombres propios y límites de fragmentos. No hay diarización automática.

React y herramientas usan sus respectivas licencias; revisar las condiciones vigentes de Remotion para el uso previsto. Las skills oficiales se instalaron con el procedimiento publicado por remotion-dev/skills.

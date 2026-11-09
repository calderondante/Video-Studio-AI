# Instalación y persistencia

## Instancia preparada

Debian 13 x86_64, Node 24.22.1, npm 11.9.0, Python 3.12.14, FFmpeg/FFprobe 7.1.5 y Chromium preinstalados. No se requirió sudo. Los paquetes npm están fijados en package-lock.json; Python en requirements.lock.

```bash
cd /workspace/Video-Studio-AI
bash scripts/install.sh
npm test
```

El instalador usa cachés escribibles bajo `/workspace/.cache` y una venv local. Usa `npm ci`; no regenera locks. Verifica herramientas, tipos, encoders, filtros, importaciones ASR y VAD. No descarga modelos ni procesa originales. En otra imagen, instalar primero Node 24, Python 3.12 con venv, FFmpeg con libass/libx264/AAC, fuentes DejaVu y Chromium mediante el instalador de paquetes aprobado del entorno. La imagen actual ya los contiene.

## Codex Cloud

El borrador y la máquina son estados diferentes. Guardar y publicar son operaciones de la interfaz; no se puede dar por publicado un cambio porque funcione aquí.

Campos reproducibles preparados en `config/cloud-environment.json`:

- `install_script`: ejecuta `bash scripts/install.sh` desde el checkout.
- `start_skill`: reutiliza el checkout, comprueba dependencias e indica cómo arrancar Studio y validar outputs.

Si la herramienta de borrador no puede guardar, copiar estos campos en los ajustes del entorno. Revisar y guardar, luego publicar. No suponer restauración en nuevas tareas sin comprobarla. Mantener código en Git; multimedia y cachés se excluyen. Las claves se configuran exclusivamente en ajustes seguros.

## Dominios adicionales necesarios

No se reemplazó la lista de red desconocida. Agregar conservando los dominios existentes:

- `www.remotion.dev`: documentación oficial.
- `remotion.media`: navegador recomendado por Remotion (su descarga actual falló).
- `huggingface.co`: metadatos/modelos Whisper.
- `cdn-lfs.huggingface.co`, `cdn-lfs-us-1.hf.co`, `cas-bridge.xethub.hf.co`, `cas-server.xethub.hf.co`, `transfer.xethub.hf.co`: posibles destinos de modelos; confirmar redirecciones concretas al habilitar Hugging Face.

npm, PyPI y GitHub ya funcionan para las operaciones verificadas. No se necesita una API ni clave para instalar o usar ASR local una vez disponible el modelo. No se probó Drive ni se requiere habilitarlo para esta etapa.

## Reanudar la validación ASR

Tras habilitar red, probar primero tiny (~75 MB de pesos), no un modelo enorme:

```bash
.venv/bin/python scripts/transcribe.py audio_autorizado.wav --model tiny --output work/prueba-asr
```

El script usa CPU/int8 aquí; base es el valor normal para CPU y small para GPU detectada. Un modelo local ya descargado también puede pasarse mediante `--model /ruta/al/modelo`. Revisar exactitud y tiempos con audio español autorizado; ni la prueba simulada ni VAD silencioso sustituyen esta comprobación.

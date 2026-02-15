# 🚀 Despliegue de OmniGrab Media Downloader

Esta guía te ayudará a poner tu aplicación en internet para que cualquiera pueda usarla.

La opción más recomendada y fácil (y gratuita) es **Render**.

## 📦 Prerrequisitos (Ya Configurados)
El proyecto ya tiene los archivos necesarios:
- `Dockerfile`: Configura el entorno con Python y **FFmpeg** (necesario para unir video/audio).
- `requirements.txt`: Lista de dependencias.
- `app.py`: Servidor configurado para producción.

---

## ☁️ Opción 1: Render (Gratis y Recomendado)

1.  **Sube tu código a GitHub**
    - Crea un repositorio en GitHub.
    - Sube todos los archivos del proyecto.

2.  **Crea una cuenta en [Render.com](https://render.com/)**

3.  **Nuevo Web Service**
    - Click en "New +" -> "Web Service".
    - Conecta tu cuenta de GitHub y selecciona el repositorio de OmniGrab.

4.  **Configuración**
    - **Name**: `omnigrab-downloader` (o el que quieras)
    - **Region**: La más cercana a ti (ej. Ohio, Frankfurt).
    - **Branch**: `main` (o master).
    - **Runtime**: **Docker** (Importante: NO elijas Python, elige Docker para tener FFmpeg).
    - **Plans**: Free.

5.  **Desplegar**
    - Render detectará el `Dockerfile` automáticamente.
    - Click en "Create Web Service".
    - Espera unos minutos a que termine (verás logs de construcción).

¡Listo! Te darán una URL como `https://omnigrab.onrender.com`.

---

## 🚂 Opción 2: Railway (Alternativa)

1.  Crea cuenta en [Railway.app](https://railway.app/).
2.  "New Project" -> "Deploy from GitHub repo".
3.  Railway detectará el `Dockerfile` y desplegará automáticamente.
4.  Genera un dominio en la configuración del servicio.

---

## 🐳 Opción 3: Ejecutar Localmente con Docker

Si tienes Docker instalado, puedes probar la versión de producción en tu PC:

```bash
# Construir la imagen
docker build -t omnigrab .

# Correr el contenedor
docker run -p 8080:8080 omnigrab
```

La app estará en `http://localhost:8080`.

---

## ⚠️ Consideraciones Importantes

- **Servicios Gratuitos**: En el plan gratuito de Render, el servicio "duerme" después de 15 minutos de inactividad. La primera vez que entres tardará unos 30-50 segundos en arrancar ("Cold Start").
- **Archivos Temporales**: Como usamos Docker y sistemas de archivos efímeros, cualquier archivo que no se borre se perderá al reiniciar. ¡Perfecto para nuestra app que borra los videos después de descargar!

# 🎬 Universal Media Downloader

Una aplicación web moderna para descargar videos y audio de múltiples plataformas con una interfaz elegante en dark mode.

## ✨ Características

- 🎥 **YouTube**: Descarga videos en múltiples calidades o extrae audio en MP3
- 📸 **Instagram**: Descarga posts y reels
- 🎵 **TikTok**: Descarga videos (sin marca de agua cuando es posible)
- 📘 **Facebook**: Descarga videos públicos
- 🎨 **Interfaz moderna**: Dark mode con Tailwind CSS y animaciones suaves
- 📊 **Barra de progreso**: Seguimiento en tiempo real de las descargas
- 🛡️ **Anti-bloqueo**: User-Agents aleatorios para evitar restricciones
- ⚡ **Rápido y eficiente**: Procesamiento en segundo plano con Flask

## 📋 Requisitos Previos

### 1. Python 3.8 o superior
```bash
python3 --version
```

### 2. FFmpeg (requerido para procesamiento de video/audio)

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**macOS (con Homebrew):**
```bash
brew install ffmpeg
```

**Windows:**
Descarga desde [ffmpeg.org](https://ffmpeg.org/download.html) y añade al PATH

## 🚀 Instalación

### 1. Clonar o descargar el proyecto
```bash
cd /home/pac/Documentos/Proyectos/universal-media-downloader
```

### 2. Crear entorno virtual
```bash
python3 -m venv venv
```

### 3. Activar entorno virtual

**Linux/macOS:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 4. Instalar dependencias
```bash
pip install -r requirements.txt
```

## 🎯 Uso

### 1. Iniciar el servidor
```bash
python app.py
```

Verás un mensaje como:
```
============================================================
🎬 Universal Media Downloader
============================================================
🌐 Servidor iniciado en: http://localhost:5000
📥 Plataformas soportadas:
   • YouTube (Video/Audio)
   • Instagram (Posts/Reels)
   • TikTok (Videos)
   • Facebook (Videos)
============================================================
⚠️  Presiona Ctrl+C para detener el servidor
============================================================
```

### 2. Abrir en el navegador
Abre tu navegador favorito y ve a:
```
http://localhost:5000
```

### 3. Descargar contenido
1. Pega la URL del video/post en el campo de entrada
2. Haz clic en **"Analizar"**
3. Selecciona el formato y calidad deseados
4. Haz clic en **"Descargar"**
5. Espera a que se complete la descarga
6. Haz clic en **"Guardar archivo"** para descargar a tu computadora

## 📁 Estructura del Proyecto

```
universal-media-downloader/
├── app.py                      # Servidor Flask y API endpoints
├── downloader.py               # Clase MediaEngine con lógica de yt-dlp
├── templates/
│   └── index.html             # Interfaz web con Tailwind CSS
├── static/
│   └── downloads/             # Archivos descargados (creado automáticamente)
├── requirements.txt           # Dependencias de Python
└── README.md                  # Este archivo
```

## 🔧 Configuración Avanzada

### Cambiar puerto del servidor
Edita `app.py` línea final:
```python
app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
```

### Cambiar directorio de descargas
Edita `app.py` línea 13:
```python
media_engine = MediaEngine(download_path='static/downloads')
```

## 🐛 Solución de Problemas

### Error: "ffmpeg not found"
- Asegúrate de tener ffmpeg instalado y en el PATH del sistema
- Verifica con: `ffmpeg -version`

### Error: "Private video" o "Content not available"
- El contenido es privado o requiere autenticación
- Verifica que el enlace sea público

### Error: "Unsupported URL"
- La plataforma no está soportada
- Verifica que sea YouTube, Instagram, TikTok o Facebook

### Descarga muy lenta
- Puede ser limitación de la plataforma
- Intenta con una calidad menor

### Error de conexión
- Verifica tu conexión a internet
- Algunas plataformas pueden bloquear descargas masivas

## 📝 Notas Importantes

- ⚠️ **Uso responsable**: Respeta los derechos de autor y términos de servicio de cada plataforma
- 🔒 **Contenido privado**: Solo funciona con contenido público
- 🌐 **Conexión requerida**: Necesitas internet para descargar
- 💾 **Espacio en disco**: Asegúrate de tener suficiente espacio para las descargas

## 🛠️ Tecnologías Utilizadas

- **Backend**: Python 3, Flask
- **Descargador**: yt-dlp
- **Frontend**: HTML5, Tailwind CSS, JavaScript (Vanilla)
- **Procesamiento**: FFmpeg

## 📄 Licencia

Este proyecto es de código abierto y está disponible para uso educativo.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Haz fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📧 Soporte

Si encuentras algún problema o tienes sugerencias, por favor abre un issue en el repositorio.

---

Desarrollado con ❤️ usando Python, Flask y yt-dlp

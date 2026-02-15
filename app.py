"""
Universal Media Downloader - Flask Application
Web interface for downloading media from multiple platforms
"""

from flask import Flask, render_template, request, jsonify, send_from_directory, Response
from downloader import MediaEngine
import threading
import uuid
import json
import time
from pathlib import Path

app = Flask(__name__)
app.config['SECRET_KEY'] = 'universal-media-downloader-secret-key'

# Initialize MediaEngine
media_engine = MediaEngine(download_path='static/downloads')

# Store download progress for each task
download_progress = {}
download_lock = threading.Lock()


@app.route('/')
def index():
    """Serve the main interface"""
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Analyze URL and return available formats
    
    Expected JSON: {"url": "https://..."}
    Returns: {"success": bool, "info": {...}, "formats": [...]} or {"success": false, "error": "..."}
    """
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({
                'success': False,
                'error': 'Por favor ingresa una URL válida'
            }), 400
        
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            return jsonify({
                'success': False,
                'error': 'La URL debe comenzar con http:// o https://'
            }), 400
        
        # Analyze URL
        result = media_engine.analyze_url(url)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error del servidor: {str(e)}'
        }), 500


@app.route('/api/download', methods=['POST'])
def download():
    """
    Stream download directly to browser without saving on server
    
    Expected JSON: {"url": "https://...", "format": "video_best"}
    Returns: Streaming file response
    """
    try:
        # Try to get data from JSON or Form (fallback)
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
            
        url = data.get('url', '').strip()
        format_choice = data.get('format', 'video_best')
        
        if not url:
            return jsonify({
                'success': False,
                'error': 'URL no proporcionada'
            }), 400
        
        # Get video info first to determine filename
        info_result = media_engine.analyze_url(url)
        if not info_result['success']:
            return jsonify({
                'success': False,
                'error': 'No se pudo analizar la URL'
            }), 400
        
        # Generate filename
        title = info_result['info']['title']
        # Sanitize filename
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title[:100]  # Limit length
        
        if format_choice.startswith('audio_'):
            filename = f"{safe_title}.mp3"
            mimetype = 'audio/mpeg'
        else:
            filename = f"{safe_title}.mp4"
            mimetype = 'video/mp4'
        
        # Stream download directly
        def generate():
            """Generator function to stream file data"""
            try:
                for chunk in media_engine.stream_download(url, format_choice):
                    yield chunk
            except Exception as e:
                print(f"Streaming error: {e}")
                # Can't send error to client mid-stream
                pass
        
        response = Response(generate(), mimetype=mimetype)
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.headers['Cache-Control'] = 'no-cache'
        
        return response
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al iniciar descarga: {str(e)}'
        }), 500


def download_worker(task_id, url, format_choice):
    """
    Background worker for downloading media
    
    Args:
        task_id (str): Unique task identifier
        url (str): Media URL
        format_choice (str): Selected format
    """
    def progress_callback(progress_info):
        """Update progress information"""
        with download_lock:
            if progress_info['status'] == 'downloading':
                download_progress[task_id] = {
                    'status': 'downloading',
                    'percentage': round(progress_info['percentage'], 1),
                    'message': f"Descargando... {round(progress_info['percentage'], 1)}%"
                }
            elif progress_info['status'] == 'finished':
                download_progress[task_id]['status'] = 'processing'
                download_progress[task_id]['message'] = 'Procesando archivo...'
    
    try:
        # Update status
        with download_lock:
            download_progress[task_id] = {
                'status': 'downloading',
                'percentage': 0,
                'message': 'Conectando...'
            }
        
        # Download media
        result = media_engine.download_media(
            url=url,
            format_choice=format_choice,
            progress_callback=progress_callback
        )
        
        if result['success']:
            with download_lock:
                download_progress[task_id] = {
                    'status': 'completed',
                    'percentage': 100,
                    'message': 'Descarga completada',
                    'filename': result['filename'],
                    'download_url': f"/downloads/{result['filename']}"
                }
        else:
            with download_lock:
                download_progress[task_id] = {
                    'status': 'error',
                    'percentage': 0,
                    'message': result.get('error', 'Error desconocido')
                }
    
    except Exception as e:
        with download_lock:
            download_progress[task_id] = {
                'status': 'error',
                'percentage': 0,
                'message': f'Error: {str(e)}'
            }


@app.route('/api/progress/<task_id>')
def get_progress(task_id):
    """
    Get download progress for a task (Server-Sent Events)
    
    Args:
        task_id (str): Task identifier
        
    Returns:
        Server-Sent Events stream with progress updates
    """
    def generate():
        """Generate SSE events"""
        last_status = None
        
        while True:
            with download_lock:
                if task_id in download_progress:
                    current_progress = download_progress[task_id].copy()
                else:
                    current_progress = {
                        'status': 'not_found',
                        'percentage': 0,
                        'message': 'Tarea no encontrada'
                    }
            
            # Send update if status changed
            if current_progress != last_status:
                yield f"data: {json.dumps(current_progress)}\n\n"
                last_status = current_progress.copy()
            
            # Stop streaming if completed or error
            if current_progress['status'] in ['completed', 'error', 'not_found']:
                break
            
            time.sleep(0.5)  # Update every 500ms
    
    return Response(generate(), mimetype='text/event-stream')


@app.route('/downloads/<filename>')
def download_file(filename):
    """
    Serve downloaded files
    
    Args:
        filename (str): Name of the file to download
        
    Returns:
        File download response
    """
    try:
        downloads_dir = Path('static/downloads')
        return send_from_directory(
            downloads_dir,
            filename,
            as_attachment=True
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Archivo no encontrado: {str(e)}'
        }), 404


@app.route('/api/cleanup/<task_id>', methods=['DELETE'])
def cleanup_task(task_id):
    """
    Clean up task progress data
    
    Args:
        task_id (str): Task identifier
        
    Returns:
        Success response
    """
    with download_lock:
        if task_id in download_progress:
            del download_progress[task_id]
    
    return jsonify({
        'success': True,
        'message': 'Tarea limpiada'
    }), 200


if __name__ == '__main__':
    print("=" * 60)
    print("🎬 Universal Media Downloader")
    print("=" * 60)
    print("🌐 Servidor iniciado en: http://localhost:5000")
    print("📥 Plataformas soportadas:")
    print("   • YouTube (Video/Audio)")
    print("   • Instagram (Posts/Reels)")
    print("   • TikTok (Videos)")
    print("   • Facebook (Videos)")
    print("=" * 60)
    print("⚠️  Presiona Ctrl+C para detener el servidor")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)

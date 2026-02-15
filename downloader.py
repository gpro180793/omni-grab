"""
Universal Media Downloader - MediaEngine Class
Handles media downloading from multiple platforms using yt-dlp
"""

import yt_dlp
import random
import os
import subprocess
from pathlib import Path


class MediaEngine:
    """
    Encapsulates yt-dlp functionality for downloading media from various platforms
    Supports: YouTube, Instagram, TikTok, Facebook
    """
    
    # User-Agent rotation to avoid blocking
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    ]
    
    def __init__(self, download_path='static/downloads'):
        """
        Initialize MediaEngine with download path
        
        Args:
            download_path (str): Directory where files will be saved
        """
        self.download_path = Path(download_path)
        self.download_path.mkdir(parents=True, exist_ok=True)
        
    def _get_random_user_agent(self):
        """Return a random User-Agent to avoid blocking"""
        return random.choice(self.USER_AGENTS)
    
    def _get_base_options(self):
        """
        Get base yt-dlp options with anti-blocking measures
        
        Returns:
            dict: Base configuration options
        """
        return {
            'user_agent': self._get_random_user_agent(),
            'nocheckcertificate': True,
            'no_warnings': False,
            'quiet': False,
            'no_color': True,
            'extract_flat': False,
            'socket_timeout': 30,
            'retries': 3,
            'fragment_retries': 3,
            # Cookies and headers for better compatibility
            'cookiefile': None,
            'http_headers': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            }
        }
    
    def analyze_url(self, url):
        """
        Analyze URL and extract metadata without downloading
        
        Args:
            url (str): Media URL to analyze
            
        Returns:
            dict: Contains 'success', 'info', 'formats', or 'error'
        """
        try:
            ydl_opts = self._get_base_options()
            ydl_opts.update({
                'skip_download': True,
                'no_warnings': True,
            })
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if info is None:
                    return {
                        'success': False,
                        'error': 'No se pudo obtener información del enlace'
                    }
                
                # Get available formats
                formats = self.get_available_formats(info)
                
                return {
                    'success': True,
                    'info': {
                        'title': info.get('title', 'Sin título'),
                        'duration': info.get('duration', 0),
                        'thumbnail': info.get('thumbnail', ''),
                        'uploader': info.get('uploader', 'Desconocido'),
                        'platform': info.get('extractor_key', 'Unknown'),
                    },
                    'formats': formats
                }
                
        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            if 'Private video' in error_msg or 'not available' in error_msg:
                return {
                    'success': False,
                    'error': 'El contenido es privado o no está disponible'
                }
            elif 'Unsupported URL' in error_msg:
                return {
                    'success': False,
                    'error': 'URL no soportada. Verifica que sea de YouTube, Instagram, TikTok o Facebook'
                }
            else:
                return {
                    'success': False,
                    'error': f'Error al analizar: {error_msg}'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error inesperado: {str(e)}'
            }
    
    def get_available_formats(self, info):
        """
        Extract and organize available formats from video info
        
        Args:
            info (dict): Video information from yt-dlp
            
        Returns:
            list: List of format options with id, label, and type
        """
        formats = []
        
        # Add audio-only option (MP3)
        formats.append({
            'id': 'audio_mp3',
            'label': 'Audio MP3 (mejor calidad)',
            'type': 'audio',
            'ext': 'mp3'
        })
        
        # Get video formats
        if 'formats' in info and info['formats']:
            # Collect all video formats (including those that need audio merging)
            video_formats = []
            
            for f in info['formats']:
                # Skip audio-only formats
                if f.get('vcodec') == 'none':
                    continue
                
                # Get video height
                height = f.get('height')
                if height and height >= 144:  # Minimum quality threshold
                    video_formats.append({
                        'height': height,
                        'format_id': f['format_id'],
                        'ext': f.get('ext', 'mp4'),
                        'filesize': f.get('filesize', 0),
                        'has_audio': f.get('acodec') != 'none'
                    })
            
            # Sort by quality (height) descending
            video_formats.sort(key=lambda x: x['height'], reverse=True)
            
            # Add quality options (deduplicate by height)
            seen_heights = set()
            for vf in video_formats:
                height = vf['height']
                if height not in seen_heights:
                    seen_heights.add(height)
                    
                    # Create label with quality indicator
                    if height >= 2160:
                        quality_label = f'Video {height}p (4K) MP4'
                    elif height >= 1440:
                        quality_label = f'Video {height}p (2K) MP4'
                    elif height >= 1080:
                        quality_label = f'Video {height}p (Full HD) MP4'
                    elif height >= 720:
                        quality_label = f'Video {height}p (HD) MP4'
                    else:
                        quality_label = f'Video {height}p MP4'
                    
                    formats.append({
                        'id': f"video_{height}p",
                        'label': quality_label,
                        'type': 'video',
                        'ext': 'mp4',
                        'height': height
                    })
        
        # If no specific formats found, add best quality option
        if len(formats) == 1:  # Only audio option
            formats.append({
                'id': 'video_best',
                'label': 'Video (mejor calidad disponible)',
                'type': 'video',
                'ext': 'mp4'
            })
        
        return formats
    
    def download_media(self, url, format_choice='video_best', progress_callback=None):
        """
        Download media with specified format
        
        Args:
            url (str): Media URL to download
            format_choice (str): Format ID from get_available_formats
            progress_callback (callable): Function to call with progress updates
            
        Returns:
            dict: Contains 'success', 'filename', 'path', or 'error'
        """
        try:
            ydl_opts = self._get_base_options()
            
            # Configure output template
            output_template = str(self.download_path / '%(title)s.%(ext)s')
            
            ydl_opts.update({
                'outtmpl': output_template,
                'progress_hooks': [self._create_progress_hook(progress_callback)] if progress_callback else [],
            })
            
            # Configure format based on choice
            if format_choice.startswith('audio_'):
                # Audio extraction
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                })
            elif format_choice.startswith('video_'):
                # Video download
                if format_choice == 'video_best':
                    # Best quality available
                    ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                else:
                    # Extract height from choice (e.g., "video_1080p" -> "1080")
                    height_str = format_choice.replace('video_', '').replace('p', '')
                    
                    try:
                        height = int(height_str)
                        # Select best video at this height + best audio, with fallbacks
                        ydl_opts['format'] = (
                            f'bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/'
                            f'bestvideo[height<={height}]+bestaudio/'
                            f'best[height<={height}]/'
                            'best'
                        )
                    except ValueError:
                        # Fallback to best if parsing fails
                        ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                
                # Ensure MP4 output
                ydl_opts['merge_output_format'] = 'mp4'
            
            # Download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                if info is None:
                    return {
                        'success': False,
                        'error': 'No se pudo descargar el archivo'
                    }
                
                # Get the actual filename
                if format_choice.startswith('audio_'):
                    filename = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
                else:
                    filename = ydl.prepare_filename(info)
                
                # Ensure it's just the basename
                filename = os.path.basename(filename)
                
                return {
                    'success': True,
                    'filename': filename,
                    'path': str(self.download_path / filename),
                    'title': info.get('title', 'Sin título')
                }
                
        except yt_dlp.utils.DownloadError as e:
            return {
                'success': False,
                'error': f'Error de descarga: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error inesperado: {str(e)}'
            }
    
    def stream_download(self, url, format_choice='video_best'):
        """
        Download to temp file, stream it, and delete it afterwards
        
        Args:
            url (str): Media URL to download
            format_choice (str): Format ID from get_available_formats
            
        Yields:
            bytes: Chunks of file data
        """
        import tempfile
        import time
        
        temp_dir = tempfile.mkdtemp()
        temp_path = Path(temp_dir)
        
        try:
            ydl_opts = self._get_base_options()
            
            # Use temp path for output
            output_template = str(temp_path / '%(title)s.%(ext)s')
            
            ydl_opts.update({
                'outtmpl': output_template,
                'quiet': True,
                'no_warnings': True,
            })
            
            # Configure format based on choice
            if format_choice.startswith('audio_'):
                # Audio extraction
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                })
            elif format_choice.startswith('video_'):
                # Video download logic
                if format_choice == 'video_best':
                    ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                else:
                    height_str = format_choice.replace('video_', '').replace('p', '')
                    try:
                        height = int(height_str)
                        ydl_opts['format'] = (
                            f'bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/'
                            f'bestvideo[height<={height}]+bestaudio/'
                            f'best[height<={height}]/'
                            'best'
                        )
                    except ValueError:
                        ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                
                ydl_opts['merge_output_format'] = 'mp4'
            
            # Download to temp file
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                if format_choice.startswith('audio_'):
                    filename = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
                else:
                    filename = ydl.prepare_filename(info)
                
                # Handle case where filename might be different due to merging
                if not os.path.exists(filename):
                     # Try to find the file in the temp dir
                    files = list(temp_path.glob('*'))
                    if files:
                        filename = str(files[0])
            
            # Stream the file
            if os.path.exists(filename):
                with open(filename, 'rb') as f:
                    while True:
                        chunk = f.read(8192)
                        if not chunk:
                            break
                        yield chunk
            
        except Exception as e:
            print(f"Temp download error: {e}")
            raise
            
        finally:
            # Cleanup temp directory and files
            try:
                import shutil
                shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"Error cleaning up temp dir: {e}")
    
    def _create_progress_hook(self, callback):
        """
        Create a progress hook function for yt-dlp
        
        Args:
            callback (callable): Function to call with progress info
            
        Returns:
            callable: Progress hook function
        """
        def hook(d):
            if callback:
                if d['status'] == 'downloading':
                    # Calculate percentage
                    total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                    downloaded = d.get('downloaded_bytes', 0)
                    
                    if total > 0:
                        percentage = (downloaded / total) * 100
                        callback({
                            'status': 'downloading',
                            'percentage': percentage,
                            'downloaded': downloaded,
                            'total': total,
                            'speed': d.get('speed', 0),
                            'eta': d.get('eta', 0)
                        })
                elif d['status'] == 'finished':
                    callback({
                        'status': 'finished',
                        'percentage': 100
                    })
                elif d['status'] == 'error':
                    callback({
                        'status': 'error',
                        'percentage': 0
                    })
        
        return hook

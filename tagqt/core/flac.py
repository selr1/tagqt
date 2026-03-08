import subprocess
import shutil
import os
import sys
import tempfile

def _resolve_encoder() -> tuple[str, str]:
    """
    Resolve which encoder binary to use and which mode.

    Returns a tuple of (binary_path, mode) where mode is either
    'flac' or 'ffmpeg'.

    Priority:
    1. System ffmpeg (full 48kHz/32-bit conversion, preferred)
    2. System flac (re-compression only)
    3. Bundled flac inside PyInstaller sys._MEIPASS (re-compression only, last resort)
    4. Returns (None, None) if nothing is available
    """
    # 1. System ffmpeg — preferred, full 48kHz/32-bit conversion capability
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg, "ffmpeg"

    # 2. System flac — re-compression only
    system_flac = shutil.which("flac")
    if system_flac:
        return system_flac, "flac"

    # 3. Bundled flac (PyInstaller frozen binary) — last resort, re-compression only
    if getattr(sys, "frozen", False):
        name = "flac.exe" if sys.platform == "win32" else "flac"
        bundled = os.path.join(sys._MEIPASS, name)
        if os.path.isfile(bundled):
            return bundled, "flac"

    # 4. Nothing available
    return None, None

class FlacEncoder:
    """Handles FLAC re-encoding to 24-bit 48kHz using ffmpeg."""
    
    @staticmethod
    def is_flac_available():
        return shutil.which('flac') is not None
    
    @staticmethod
    def is_ffmpeg_available():
        return shutil.which('ffmpeg') is not None
    
    @staticmethod
    def get_available_encoder():
        if FlacEncoder.is_flac_available():
            return 'flac'
        elif FlacEncoder.is_ffmpeg_available():
            return 'ffmpeg'
        return None
    
    @staticmethod
    def reencode_flac(filepath):
        if not filepath.lower().endswith('.flac'):
            return False, "Not a FLAC file"
        
        # Capture metadata before encoding
        tags_to_preserve = {}
        cover_data = None
        try:
            from tagqt.core.tags import MetadataHandler
            original_meta = MetadataHandler(filepath)
            
            # Store all tags in a dict
            for attr in ['title', 'artist', 'album', 'year', 'genre', 
                         'track_number', 'disc_number', 'album_artist', 'comment', 'lyrics',
                         'bpm', 'initial_key', 'isrc', 'publisher']:
                val = getattr(original_meta, attr)
                if val:
                    tags_to_preserve[attr] = val
            
            cover_data = original_meta.get_cover()
            
        except Exception as e:
            print(f"Warning: Could not read original metadata: {e}")

        # Force 24-bit 48kHz
        # ffmpeg flac encoder uses s32 for 24-bit
        
        temp_fd, temp_path = tempfile.mkstemp(suffix='.flac')
        os.close(temp_fd)
        os.remove(temp_path)
        
        try:
            binary, mode = _resolve_encoder()

            if binary is None:
                from PySide6.QtWidgets import QApplication
                from PySide6.QtCore import QMetaObject, Qt, Q_ARG
                win = QApplication.activeWindow()
                if win and hasattr(win, 'show_toast'):
                    QMetaObject.invokeMethod(win, "show_toast", Qt.QueuedConnection, 
                        Q_ARG(str, "FLAC encoder not found. Please install FLAC or ffmpeg and ensure it is in your system PATH to use re-encoding."))
                return False, "FLAC encoder not found"

            if mode == "flac":
                # Xiph flac native CLI syntax — re-compression only
                # Cannot change sample rate or bit depth, preserves source format
                cmd = [
                    binary,
                    "--best",
                    "--force",
                    "--silent",
                    "-o", temp_path,
                    filepath
                ]
            elif mode == "ffmpeg":
                # ffmpeg — full conversion to 24-bit 48kHz
                cmd = [
                    binary, '-y', '-i', filepath,
                    '-map_metadata', '0',
                    '-c:a', 'flac',
                    '-compression_level', '5',
                    '-sample_fmt', 's32',
                    '-ar', '48000',
                    '-c:v', 'copy', temp_path
                ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                check=True
            )
            
            # Restore metadata to temp file
            try:
                from tagqt.core.tags import MetadataHandler
                new_meta = MetadataHandler(temp_path)
                
                for key, value in tags_to_preserve.items():
                    setattr(new_meta, key, value)
                
                if cover_data:
                    new_meta.set_cover(cover_data)
                    
                new_meta.save()
                
            except Exception as e:
                print(f"Warning: Could not restore metadata: {e}")
            
            shutil.move(temp_path, filepath)
            return True, None
            
        except subprocess.CalledProcessError as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return False, f"Encoding failed: {e.stderr.decode() if e.stderr else str(e)}"
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return False, str(e)


class DependencyChecker:
    """Checks availability of optional external dependencies."""
    
    @staticmethod
    def check_koroman():
        try:
            import koroman
            return True, None
        except ImportError:
            return False, "koroman library is not installed. Install with: pip install koroman"
    
    @staticmethod
    def check_flac_tools():
        encoder = FlacEncoder.get_available_encoder()
        if encoder:
            return True, encoder
        return False, "Neither flac nor ffmpeg is installed. Please install one of them."
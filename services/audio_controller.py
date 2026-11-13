"""
UZHAVAR AI – Kannada Voice Bridge
Server-Side Audio Processing & Validation Controller
"""

import os
import uuid
import logging
from werkzeug.utils import secure_filename
from typing import Tuple, Optional

logger = logging.getLogger("uzhavar.audio")

class AudioController:
    ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'webm', 'm4a', 'flac', 'aac', 'opus'}
    MAX_FILE_SIZE = 32 * 1024 * 1024  # 32 MB

    @classmethod
    def validate_audio_file(cls, file_obj) -> Tuple[bool, Optional[str]]:
        """Validate uploaded audio file format and size."""
        if not file_obj or file_obj.filename == '':
            return False, "No audio file provided"

        filename = file_obj.filename.lower()
        ext = filename.rsplit('.', 1)[-1] if '.' in filename else ''
        if ext and ext not in cls.ALLOWED_EXTENSIONS:
            return False, f"Unsupported audio extension: .{ext}. Supported formats: {', '.join(cls.ALLOWED_EXTENSIONS)}"

        return True, None

    @classmethod
    def save_temp_audio(cls, file_obj, upload_dir: str) -> Tuple[Optional[str], Optional[bytes]]:
        """Safely saves temporary audio and returns (file_path, bytes)."""
        os.makedirs(upload_dir, exist_ok=True)
        ext = file_obj.filename.rsplit('.', 1)[-1] if '.' in file_obj.filename else 'wav'
        temp_name = f"rec_{uuid.uuid4().hex[:12]}.{ext}"
        save_path = os.path.join(upload_dir, temp_name)

        audio_bytes = file_obj.read()
        if len(audio_bytes) > cls.MAX_FILE_SIZE:
            return None, None

        with open(save_path, 'wb') as f:
            f.write(audio_bytes)

        return save_path, audio_bytes

    @classmethod
    def cleanup_temp_file(cls, file_path: str):
        """Immediately clean up temporary audio files to prevent disk usage leaks."""
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                logger.warning(f"Could not remove temp audio file {file_path}: {e}")


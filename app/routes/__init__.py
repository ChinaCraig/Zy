# Routes package initialization
from .routes import main
from .llm_routes import llm_bp
from .vision_routes import vision_bp
from .speech_routes import speech_bp

__all__ = ['main', 'llm_bp', 'vision_bp', 'speech_bp'] 
"""
AIxWord Backend Package.

An AI-powered interactive crossword puzzle application with multi-agent system
using LangGraph, FastAPI, and OpenAI.
"""

__version__ = "0.1.0"
__author__ = "AIxWord Team"
__description__ = "AI-powered interactive crossword puzzle application"

# Export key configuration (lazy import to avoid dependency issues in tests)
__all__ = [
    "__version__",
    "__author__",
    "__description__",
]


def get_settings():
    """Get application settings (lazy import)."""
    from .config import get_settings as _get_settings
    return _get_settings()


# Make settings available but don't import at module level
def __getattr__(name):
    """Lazy attribute access for settings."""
    if name == "settings":
        from .config import settings
        return settings
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

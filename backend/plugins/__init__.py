"""Domain plugins mounted on the HTTP shell."""
from .kalpavriksha import setup_kalpavriksha_routes

__all__ = ["setup_kalpavriksha_routes"]

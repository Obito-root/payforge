"""
auth package for PayForge.

Keep the package init minimal to avoid circular imports on package import.
Provide a small helper to lazily load the ElectronAuth class when needed.
"""

__all__ = ["get_electron_auth_class", "__version__"]

__version__ = "0.1.0"

def get_electron_auth_class():
    """
    Lazily import and return the ElectronAuth class.

    Usage:
        ElectronAuth = get_electron_auth_class()
        auth = ElectronAuth(...)
    """
    from .electron_auth import ElectronAuth  # imported on demand
    return ElectronAuth

import pytest
import sys
import os

def test_python_version():
    """Verifica que se esté usando Python 3.12 o superior."""
    assert sys.version_info.major == 3
    assert sys.version_info.minor >= 12

def test_project_structure():
    """Verifica que las carpetas base existan."""
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    required_dirs = ["src", "docs", "tests", ".agent"]
    for directory in required_dirs:
        assert os.path.exists(os.path.join(base_path, directory)), f"Falta el directorio: {directory}"

def test_requirements_installed():
    """Prueba básica de que las librerías principales son importables."""
    import pandas
    import numpy
    import skforecast
    assert pandas.__version__ is not None
    assert numpy.__version__ is not None
    assert skforecast.__version__ is not None

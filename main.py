"""
SISTEMA DE VENTAS PRO — 100% PYTHON (CUSTOMTKINTER & SQLITE3)
---------------------------------------------------------------
Para ejecutar la aplicación:
    python main.py

Credenciales de prueba preconfiguradas:
  1. Administrador (acceso completo):
     Usuario: admin@lozano.com
     Clave:   123456

  2. Consultor (solo resumen / dashboard informativo):
     Usuario: lucia@edu.com
     Clave:   lucia2177$

  3. Vendedor (operaciones comerciales):
     Usuario: vendedor@lozano.com
     Clave:   123456
"""

import sys
import os

# Asegurar que el directorio raíz esté en sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sistema_ventas_python.app import run_app

if __name__ == "__main__":
    run_app()

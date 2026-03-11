"""Entry point da GUI. Execute: python app.py"""
import sys
import os

# Garante que imports relativos funcionem tanto no dev quanto no .exe
sys.path.insert(0, os.path.dirname(__file__))

from gui.app_window import AppWindow

if __name__ == "__main__":
    app = AppWindow()
    app.mainloop()

"""Entry point da GUI. Execute: python app.py"""
import sys
import os
import traceback

# Garante que imports relativos funcionem tanto no dev quanto no .exe
sys.path.insert(0, os.path.dirname(__file__))


def _log_fatal(exc: Exception):
    try:
        base = os.path.dirname(os.path.abspath(sys.argv[0]))
        with open(os.path.join(base, "erro_scraper.log"), "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
    except Exception:
        pass


if __name__ == "__main__":
    try:
        from gui.app_window import AppWindow
        app = AppWindow()
        app.mainloop()
    except Exception as e:
        _log_fatal(e)
        raise

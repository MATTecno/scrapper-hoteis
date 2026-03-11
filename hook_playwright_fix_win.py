# Runtime hook Windows — executado pelo PyInstaller antes de qualquer import.
# Aponta o Playwright para os browsers instalados no sistema pelo usuário.
import os
import sys
import stat

if getattr(sys, "frozen", False):
    base = sys._MEIPASS

    # Node.js driver — garante permissão de execução
    node = os.path.join(base, "playwright", "driver", "node.exe")
    if os.path.isfile(node):
        try:
            os.chmod(node, os.stat(node).st_mode | stat.S_IXUSR)
        except Exception:
            pass

    # Browsers instalados no Windows ficam em %LOCALAPPDATA%\ms-playwright
    localappdata = os.environ.get("LOCALAPPDATA", "")
    cache_win = os.path.join(localappdata, "ms-playwright")
    if os.path.isdir(cache_win):
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = cache_win

# Runtime hook — executado pelo PyInstaller antes de qualquer import do app.
# Garante que o driver Node.js do Playwright tenha permissão de execução
# e aponta para os browsers instalados no sistema (não empacotados).
import os
import sys
import stat

if getattr(sys, "frozen", False):
    base = sys._MEIPASS

    # Node.js driver — precisa de permissão de execução após extração
    node = os.path.join(base, "playwright", "driver", "node")
    if os.path.isfile(node):
        os.chmod(node, os.stat(node).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    # Usa os browsers JÁ instalados no sistema pelo playwright install
    # Evita problemas de libs faltando no ambiente isolado do PyInstaller
    cache_default = os.path.expanduser("~/.cache/ms-playwright")
    if os.path.isdir(cache_default):
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = cache_default

"""
Módulo de system tray (bandeja do sistema).
Funciona em Windows e Linux (requer pystray + pillow).
"""
import threading
import sys
import os

# No Linux, força o backend gtk (não precisa de libayatana-appindicator3)
if sys.platform != "win32":
    os.environ.setdefault("PYSTRAY_BACKEND", "gtk")

from PIL import Image, ImageDraw


def _criar_icone_imagem() -> Image.Image:
    """Cria um ícone simples com a letra H sobre fundo azul."""
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Círculo azul
    draw.ellipse([2, 2, size - 2, size - 2], fill="#1a56a0")
    # Letra H branca
    draw.rectangle([16, 16, 24, 48], fill="white")
    draw.rectangle([40, 16, 48, 48], fill="white")
    draw.rectangle([16, 28, 48, 36], fill="white")
    return img


class TrayIcon:
    """
    Gerencia o ícone na bandeja do sistema.

    Uso:
        tray = TrayIcon(app_window)
        tray.start()
    """

    def __init__(self, app):
        self._app = app
        self._icon = None
        self._started = False

    def start(self):
        """Inicia o ícone da bandeja em thread separada."""
        try:
            import pystray
        except ImportError:
            return  # pystray não instalado, ignora silenciosamente

        import pystray

        menu = pystray.Menu(
            pystray.MenuItem("Abrir", self._mostrar, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Sair", self._sair),
        )

        self._icon = pystray.Icon(
            name="scrapper_hoteis",
            icon=_criar_icone_imagem(),
            title="Scrapper Hotéis",
            menu=menu,
        )

        t = threading.Thread(target=self._icon.run, daemon=True)
        t.start()
        self._started = True

    def stop(self):
        if self._icon and self._started:
            try:
                self._icon.stop()
            except Exception:
                pass

    def _mostrar(self, icon=None, item=None):
        self._app.after(0, self._app.deiconify)
        self._app.after(0, self._app.lift)
        self._app.after(0, self._app.focus_force)

    def _sair(self, icon=None, item=None):
        self.stop()
        self._app.after(0, self._app._sair_definitivo)

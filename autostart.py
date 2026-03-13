"""
Módulo de inicialização automática com o sistema operacional.

Suporta Windows (registro) e Linux (arquivo .desktop no autostart do XDG).
"""
import os
import sys

APP_NAME = "ScrapperHoteis"


def _exe_path() -> str:
    """Retorna o caminho absoluto do executável atual."""
    if getattr(sys, "frozen", False):
        return os.path.abspath(sys.executable)
    return os.path.abspath(sys.argv[0])


# ─────────────────────────────────────────────────────────────────────────────
# Windows
# ─────────────────────────────────────────────────────────────────────────────

def _win_ativar():
    import winreg
    chave = r"Software\Microsoft\Windows\CurrentVersion\Run"
    exe = _exe_path()
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, chave, 0, winreg.KEY_SET_VALUE) as k:
        winreg.SetValueEx(k, APP_NAME, 0, winreg.REG_SZ, f'"{exe}" --minimized')


def _win_desativar():
    import winreg
    chave = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, chave, 0, winreg.KEY_SET_VALUE) as k:
            winreg.DeleteValue(k, APP_NAME)
    except FileNotFoundError:
        pass


def _win_esta_ativo() -> bool:
    import winreg
    chave = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, chave) as k:
            winreg.QueryValueEx(k, APP_NAME)
            return True
    except FileNotFoundError:
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Linux (XDG autostart)
# ─────────────────────────────────────────────────────────────────────────────

def _linux_desktop_path() -> str:
    xdg = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
    return os.path.join(xdg, "autostart", f"{APP_NAME}.desktop")


def _linux_ativar():
    path = _linux_desktop_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    exe = _exe_path()
    conteudo = (
        "[Desktop Entry]\n"
        "Type=Application\n"
        f"Name={APP_NAME}\n"
        f"Exec={exe} --minimized\n"
        "Hidden=false\n"
        "NoDisplay=false\n"
        "X-GNOME-Autostart-enabled=true\n"
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(conteudo)


def _linux_desativar():
    path = _linux_desktop_path()
    try:
        os.remove(path)
    except FileNotFoundError:
        pass


def _linux_esta_ativo() -> bool:
    return os.path.isfile(_linux_desktop_path())


# ─────────────────────────────────────────────────────────────────────────────
# API pública
# ─────────────────────────────────────────────────────────────────────────────

def esta_ativo() -> bool:
    if sys.platform == "win32":
        return _win_esta_ativo()
    return _linux_esta_ativo()


def ativar():
    if sys.platform == "win32":
        _win_ativar()
    else:
        _linux_ativar()


def desativar():
    if sys.platform == "win32":
        _win_desativar()
    else:
        _linux_desativar()


def alternar() -> bool:
    """Liga/desliga. Retorna True se ficou ativo, False se ficou inativo."""
    if esta_ativo():
        desativar()
        return False
    else:
        ativar()
        return True

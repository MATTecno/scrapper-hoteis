"""
Tela de configuração inicial: verifica e instala o Chromium via Playwright.

Aparece automaticamente quando o Chromium não é encontrado no cache local.
É uma janela modal (CTkToplevel) que bloqueia a janela principal enquanto aberta.
"""
import glob
import os
import subprocess
import sys
import threading
import tkinter as tk

import customtkinter as ctk

# ── Paleta (mesma do app principal) ──────────────────────────────────────────
AZUL       = "#1a56a0"
AZUL_HOVER = "#154a8a"
VERDE      = "#2d8a4e"
VERD_HOVER = "#246e3e"
VERMELHO   = "#dc2626"
VERM_HOVER = "#b91c1c"
CINZA_BG   = "#f0f2f5"
BRANCO     = "#ffffff"
TEXTO      = "#1a1a2e"
SUBTEXTO   = "#6b7280"


# ─────────────────────────────────────────────────────────────────────────────
# Detecção de Chromium
# ─────────────────────────────────────────────────────────────────────────────

def _chromium_instalado() -> bool:
    """Retorna True se o Chromium do Playwright já está no cache local."""
    if sys.platform == "win32":
        base = os.path.join(
            os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
            "ms-playwright",
        )
        padrao = os.path.join(base, "chromium-*", "chrome-win", "chrome.exe")
    else:
        base   = os.path.expanduser("~/.cache/ms-playwright")
        padrao = os.path.join(base, "chromium-*", "chrome-linux", "chrome")

    matches = glob.glob(padrao)
    return any(os.path.isfile(p) for p in matches)


def verificar_setup(parent) -> bool:
    """
    Verifica se o Chromium está instalado.
    Se não estiver, abre a SetupScreen modal e aguarda.
    Retorna True se o Chromium estiver disponível ao término.
    """
    if _chromium_instalado():
        return True

    tela = SetupScreen(parent)
    parent.wait_window(tela)
    return _chromium_instalado()


# ─────────────────────────────────────────────────────────────────────────────
# Janela de setup
# ─────────────────────────────────────────────────────────────────────────────

class SetupScreen(ctk.CTkToplevel):
    """Modal de instalação do Chromium via Playwright."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Configuração — Scrapper Hotéis")
        self.geometry("640x480")
        self.minsize(540, 400)
        self.resizable(True, True)
        self.configure(fg_color=CINZA_BG)

        # Torna modal
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._fechar)
        self.transient(parent)

        self._instalando = False
        self._build_ui()

        # No .exe inicia a instalação automaticamente sem precisar clicar
        if getattr(sys, "frozen", False):
            self.after(500, self._iniciar_instalacao)

        # Centraliza sobre o pai
        self.update_idletasks()
        px = parent.winfo_rootx() + (parent.winfo_width()  - self.winfo_width())  // 2
        py = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{px}+{py}")

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Cabeçalho azul
        hdr = ctk.CTkFrame(self, fg_color=AZUL, corner_radius=0, height=56)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_propagate(False)
        ctk.CTkLabel(
            hdr,
            text="  Configuração inicial — Chromium",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=BRANCO,
        ).pack(side="left", padx=16, pady=14)

        # Corpo
        corpo = ctk.CTkFrame(self, fg_color=BRANCO, corner_radius=8)
        corpo.grid(row=1, column=0, sticky="nsew", padx=16, pady=12)
        corpo.grid_rowconfigure(1, weight=1)
        corpo.grid_columnconfigure(0, weight=1)

        # Descrição
        ctk.CTkLabel(
            corpo,
            text=(
                "O Scrapper Hotéis precisa do Chromium (via Playwright) para funcionar.\n"
                "Ele não foi encontrado neste computador. Clique em 'Instalar Chromium'\n"
                "para baixar e instalar automaticamente (~170 MB)."
            ),
            font=ctk.CTkFont(size=13),
            text_color=TEXTO,
            justify="left",
        ).grid(row=0, column=0, padx=16, pady=(16, 8), sticky="w")

        # Área de log / progresso
        log_frame = tk.Frame(corpo, bg="#111827")
        log_frame.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 8))
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        self._log_text = tk.Text(
            log_frame,
            wrap="word",
            font=("Courier", 10),
            bg="#111827",
            fg="#d1d5db",
            relief="flat",
            borderwidth=0,
            padx=10,
            pady=8,
            state="disabled",
            cursor="arrow",
        )
        self._log_text.grid(row=0, column=0, sticky="nsew")

        vsb = tk.Scrollbar(log_frame, command=self._log_text.yview, bg="#374151")
        vsb.grid(row=0, column=1, sticky="ns")
        self._log_text.configure(yscrollcommand=vsb.set)

        # Tags de cor para o log
        self._log_text.tag_configure("normal",  foreground="#d1d5db")
        self._log_text.tag_configure("ok",      foreground="#4ade80")
        self._log_text.tag_configure("erro",    foreground="#f87171")
        self._log_text.tag_configure("info",    foreground="#93c5fd")
        self._log_text.tag_configure("aviso",   foreground="#fbbf24")

        # Rodapé com botões
        rodape = ctk.CTkFrame(corpo, fg_color="transparent")
        rodape.grid(row=2, column=0, padx=16, pady=(0, 16), sticky="e")

        self.btn_instalar = ctk.CTkButton(
            rodape,
            text="  Instalar Chromium",
            width=180,
            height=38,
            fg_color=AZUL,
            hover_color=AZUL_HOVER,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._iniciar_instalacao,
        )
        self.btn_instalar.pack(side="left", padx=(0, 8))

        self.btn_fechar = ctk.CTkButton(
            rodape,
            text="Fechar",
            width=100,
            height=38,
            fg_color="#6b7280",
            hover_color="#4b5563",
            font=ctk.CTkFont(size=13),
            command=self._fechar,
        )
        self.btn_fechar.pack(side="left")

        # Mensagem inicial no log
        self._append_log("Aguardando instalação do Chromium...\n", "info")

    # ── Logging ───────────────────────────────────────────────────────────────

    def _append_log(self, texto: str, tag: str = "normal"):
        """Adiciona texto ao log na thread principal."""
        def _u():
            self._log_text.configure(state="normal")
            self._log_text.insert("end", texto, tag)
            self._log_text.see("end")
            self._log_text.configure(state="disabled")
        self.after(0, _u)

    # ── Instalação ────────────────────────────────────────────────────────────

    def _iniciar_instalacao(self):
        if self._instalando:
            return
        self._instalando = True
        self.btn_instalar.configure(state="disabled", text="  Instalando...")
        self.btn_fechar.configure(state="disabled")

        t = threading.Thread(target=self._instalar_chromium, daemon=True)
        t.start()

    def _instalar_chromium(self):
        """Roda em thread background; comunica com a GUI via self.after()."""
        cmd = self._encontrar_playwright()
        self._append_log(f"\n> {' '.join(cmd)}\n\n", "info")

        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )

            for linha in proc.stdout:
                linha_stripped = linha.rstrip("\n")
                if not linha_stripped:
                    continue
                # Classifica a linha para colorir
                tag = "normal"
                llow = linha_stripped.lower()
                if any(w in llow for w in ("error", "erro", "failed", "falha")):
                    tag = "erro"
                elif any(w in llow for w in ("downloading", "baixando", "extracting")):
                    tag = "info"
                elif any(w in llow for w in ("done", "success", "concluído", "finished")):
                    tag = "ok"
                self._append_log(linha_stripped + "\n", tag)

            proc.wait()

            if proc.returncode == 0:
                self._append_log("\n  Chromium instalado com sucesso!\n", "ok")
                self.after(0, self._on_sucesso)
            else:
                self._append_log(
                    f"\nInstalacao falhou (código {proc.returncode}).\n"
                    "Tente rodar manualmente: playwright install chromium\n",
                    "erro",
                )
                self.after(0, self._on_erro)

        except FileNotFoundError:
            self._append_log(
                "\nErro: 'playwright' não encontrado no PATH.\n"
                "Instale com: pip install playwright\n",
                "erro",
            )
            self.after(0, self._on_erro)
        except Exception as exc:
            self._append_log(f"\nErro inesperado: {exc}\n", "erro")
            self.after(0, self._on_erro)

    @staticmethod
    def _encontrar_playwright() -> list[str]:
        """
        Retorna o comando para rodar 'playwright install chromium'.
        No .exe PyInstaller usa o driver Node.js bundlado diretamente.
        Em dev usa o CLI playwright normal.
        """
        if getattr(sys, "frozen", False):
            # Dentro do .exe: o driver está em _MEIPASS/playwright/driver/
            base = sys._MEIPASS  # noqa: SLF001
            if sys.platform == "win32":
                node = os.path.join(base, "playwright", "driver", "node.exe")
                cli  = os.path.join(base, "playwright", "driver", "package", "cli.js")
            else:
                node = os.path.join(base, "playwright", "driver", "node")
                cli  = os.path.join(base, "playwright", "driver", "package", "cli.js")
            if os.path.isfile(node) and os.path.isfile(cli):
                return [node, cli, "install", "chromium"]

        # Em dev: usa o CLI playwright do ambiente
        scripts_dir = os.path.join(
            os.path.dirname(sys.executable),
            "Scripts" if sys.platform == "win32" else "",
        )
        for nome in ("playwright.exe", "playwright"):
            c = os.path.join(scripts_dir, nome)
            if os.path.isfile(c):
                return [c, "install", "chromium"]

        return ["playwright", "install", "chromium"]

    # ── Pós-instalação ────────────────────────────────────────────────────────

    def _on_sucesso(self):
        self.btn_instalar.configure(
            state="normal",
            text="  Chromium instalado",
            fg_color=VERDE,
            hover_color=VERD_HOVER,
        )
        self.btn_fechar.configure(
            state="normal",
            text="Continuar",
            fg_color=VERDE,
            hover_color=VERD_HOVER,
            command=self.destroy,
        )
        self._instalando = False

    def _on_erro(self):
        self.btn_instalar.configure(
            state="normal",
            text="  Tentar novamente",
            fg_color=VERMELHO,
            hover_color=VERM_HOVER,
        )
        self.btn_fechar.configure(state="normal")
        self._instalando = False

    def _fechar(self):
        if not self._instalando:
            self.destroy()

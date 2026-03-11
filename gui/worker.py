"""
Worker thread: roda o scraper sem travar a GUI.
Comunica com a janela principal via callbacks chamados com root.after().
"""
import threading
from datetime import datetime, timedelta


class ScraperWorker(threading.Thread):
    def __init__(self, config: dict, app):
        super().__init__(daemon=True)
        self._config = config
        self._app    = app          # referência à AppWindow
        self._parar  = False

    # ─────────────────────────────────────────────────────────────────────────
    def run(self):
        try:
            self._aplicar_config()
            cfg  = self._config
            modo = cfg["modo"]

            if modo == "rate_shopper":
                datas = self._gerar_datas(cfg["data_de"], cfg["data_ate"])
                self._status(f"Iniciando Rate Shopper — {len(datas)} datas...")
                from scraper import scrape_rate_shopper
                hoteis = scrape_rate_shopper(
                    datas,
                    paginas=int(cfg["paginas"]),
                    on_progress=self._on_progress,
                )
            else:
                ci = self._para_iso(cfg["data_de"])
                co = self._para_iso(cfg["data_ate"])
                self._status(f"Buscando {cfg['destino']} — {ci} → {co}...")
                from scraper import scrape
                hoteis = scrape(
                    checkin=ci,
                    checkout=co,
                    paginas=int(cfg["paginas"]),
                    on_progress=self._on_progress,
                )

            self._app.after(0, lambda: self._app.mostrar_resultados(hoteis, modo))
            self._app.after(0, lambda: self._app.set_buscando(False))
            self._status(f"Concluído — {len(hoteis)} hotéis encontrados.")

        except Exception as e:
            self._status(f"Erro: {e}")
            self._app.after(0, lambda: self._app.set_buscando(False))

    # ─────────────────────────────────────────────────────────────────────────
    def _on_progress(self, msg: str, pct: float = None):
        """Callback chamado pelo scraper a cada página coletada."""
        self._status(msg, pct)

    def _status(self, texto: str, pct: float = None):
        self._app.after(0, lambda t=texto, p=pct: self._app.set_status(t, p))

    def _aplicar_config(self):
        from config import SEARCH_CONFIG, SCRAPER_CONFIG
        cfg = self._config
        SEARCH_CONFIG["destino"] = cfg["destino"]
        SEARCH_CONFIG["adultos"] = int(cfg["adultos"]) if cfg["adultos"] else None
        SEARCH_CONFIG["quartos"] = int(cfg["quartos"]) if cfg["quartos"] else None
        SCRAPER_CONFIG["headless"] = True  # sempre headless na GUI

    @staticmethod
    def _para_iso(data_br: str) -> str:
        """Converte dd/mm/yyyy → yyyy-mm-dd."""
        return datetime.strptime(data_br.strip(), "%d/%m/%Y").strftime("%Y-%m-%d")

    @staticmethod
    def _gerar_datas(de_br: str, ate_br: str) -> list[str]:
        inicio = datetime.strptime(de_br.strip(), "%d/%m/%Y")
        fim    = datetime.strptime(ate_br.strip(), "%d/%m/%Y")
        datas  = []
        atual  = inicio
        while atual <= fim:
            datas.append(atual.strftime("%Y-%m-%d"))
            atual += timedelta(days=1)
        return datas

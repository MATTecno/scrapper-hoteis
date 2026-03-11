"""
Worker thread: roda o scraper sem travar a GUI.
Comunica com a janela principal via callbacks chamados com root.after().
"""
import threading
from datetime import datetime, timedelta


class ScraperWorker(threading.Thread):
    def __init__(self, config: dict, app):
        super().__init__(daemon=True)
        self._config  = config
        self._app     = app
        self._parar   = threading.Event()   # sinaliza cancelamento

    def parar(self):
        self._parar.set()

    @property
    def cancelado(self):
        return self._parar.is_set()

    @staticmethod
    def _log_path() -> str:
        import sys, os
        if getattr(sys, "frozen", False):
            base = os.path.dirname(os.path.abspath(sys.argv[0]))
        else:
            base = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base, "scraper.log")

    def _log(self, msg: str):
        import datetime
        try:
            with open(self._log_path(), "a", encoding="utf-8") as f:
                f.write(f"[{datetime.datetime.now():%H:%M:%S}] {msg}\n")
        except Exception:
            pass

    def run(self):
        import sys
        salvar_log = getattr(self._app, "var_logs", None)
        salvar_log = salvar_log.get() if salvar_log else False

        log_file = None
        old_stdout, old_stderr = sys.stdout, sys.stderr

        if salvar_log:
            log_path = self._log_path()
            try:
                import datetime
                log_file = open(log_path, "a", encoding="utf-8")
                log_file.write(f"\n{'='*60}\n[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] INÍCIO DA BUSCA\n{'='*60}\n")
                sys.stdout = log_file
                sys.stderr = log_file
            except Exception:
                log_file = None

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
                    parar=self._parar,
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
                    parar=self._parar,
                )

            if self.cancelado:
                self._status(f"Busca interrompida — {len(hoteis)} hotéis coletados até agora.")
            else:
                self._status(f"Concluído — {len(hoteis)} hotéis encontrados.")

            if hoteis:
                self._app.after(0, lambda: self._app.mostrar_resultados(hoteis, modo))
            self._app.after(0, lambda: self._app.set_buscando(False))

        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            try:
                sys.stdout.write(tb)
            except Exception:
                pass
            self._status(f"Erro: {e}")
            titulo = type(e).__name__
            self._app.after(0, lambda t=titulo, m=tb: self._app.mostrar_erro(t, m))
            self._app.after(0, lambda: self._app.set_buscando(False))
        finally:
            try:
                sys.stdout = old_stdout
                sys.stderr = old_stderr
                if log_file:
                    log_file.close()
            except Exception:
                pass

    def _on_progress(self, msg: str, pct: float = None):
        self._status(msg, pct)

    def _status(self, texto: str, pct: float = None):
        self._app.after(0, lambda t=texto, p=pct: self._app.set_status(t, p))

    def _aplicar_config(self):
        from config import SEARCH_CONFIG, SCRAPER_CONFIG
        cfg = self._config
        SEARCH_CONFIG["destino"] = cfg["destino"]
        SEARCH_CONFIG["adultos"] = int(cfg["adultos"]) if cfg["adultos"] else None
        SEARCH_CONFIG["quartos"] = int(cfg["quartos"]) if cfg["quartos"] else None
        SCRAPER_CONFIG["headless"] = True

    @staticmethod
    def _para_iso(data_br: str) -> str:
        return datetime.strptime(data_br.strip(), "%d/%m/%Y").strftime("%Y-%m-%d")

    @staticmethod
    def _gerar_datas(de_br: str, ate_br: str) -> list[str]:
        inicio = datetime.strptime(de_br.strip(), "%d/%m/%Y")
        fim    = datetime.strptime(ate_br.strip(), "%d/%m/%Y")
        datas, atual = [], inicio
        while atual <= fim:
            datas.append(atual.strftime("%Y-%m-%d"))
            atual += timedelta(days=1)
        return datas

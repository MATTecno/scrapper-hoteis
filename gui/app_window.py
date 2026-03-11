import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from datetime import datetime, timedelta

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

AZUL       = "#1a56a0"
AZUL_HOVER = "#154a8a"
VERDE      = "#2d8a4e"
CINZA_BG   = "#f0f2f5"
BRANCO     = "#ffffff"
TEXTO      = "#1a1a2e"
SUBTEXTO   = "#6b7280"


class AppWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Rate Shopper — Booking.com")
        self.geometry("1100x720")
        self.minsize(900, 600)
        self.configure(fg_color=CINZA_BG)
        self._ultimo_resultado = None
        self._build_ui()

    # ─────────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_header()
        self._build_config_panel()
        self._build_results_panel()
        self._build_status_bar()

    # ── Header ────────────────────────────────────────────────────────────────
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color=AZUL, corner_radius=0, height=56)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Rate Shopper — Booking.com",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=BRANCO,
        ).grid(row=0, column=0, padx=20, pady=14, sticky="w")

    # ── Painel de configuração ────────────────────────────────────────────────
    def _build_config_panel(self):
        panel = ctk.CTkFrame(self, fg_color=BRANCO, corner_radius=8)
        panel.grid(row=1, column=0, sticky="ew", padx=16, pady=(12, 0))
        panel.grid_columnconfigure((1, 3, 5), weight=1)

        label_font  = ctk.CTkFont(size=12)
        entry_font  = ctk.CTkFont(size=13)
        entry_w     = 160

        # ── Linha 1: destino, adultos, quartos, páginas ────────────────────
        ctk.CTkLabel(panel, text="Destino", font=label_font, text_color=SUBTEXTO
                     ).grid(row=0, column=0, padx=(16,4), pady=(14,2), sticky="w")
        self.entry_destino = ctk.CTkEntry(panel, font=entry_font, width=220,
                                          placeholder_text="ex: Lisboa")
        self.entry_destino.grid(row=1, column=0, padx=(16,12), pady=(0,12), sticky="w")
        self.entry_destino.insert(0, "Lisboa")

        ctk.CTkLabel(panel, text="Adultos", font=label_font, text_color=SUBTEXTO
                     ).grid(row=0, column=1, padx=4, pady=(14,2), sticky="w")
        self.entry_adultos = ctk.CTkEntry(panel, font=entry_font, width=70)
        self.entry_adultos.grid(row=1, column=1, padx=(4,12), pady=(0,12), sticky="w")
        self.entry_adultos.insert(0, "2")

        ctk.CTkLabel(panel, text="Quartos", font=label_font, text_color=SUBTEXTO
                     ).grid(row=0, column=2, padx=4, pady=(14,2), sticky="w")
        self.entry_quartos = ctk.CTkEntry(panel, font=entry_font, width=70)
        self.entry_quartos.grid(row=1, column=2, padx=(4,12), pady=(0,12), sticky="w")
        self.entry_quartos.insert(0, "1")

        ctk.CTkLabel(panel, text="Páginas por data", font=label_font, text_color=SUBTEXTO
                     ).grid(row=0, column=3, padx=4, pady=(14,2), sticky="w")
        self.entry_paginas = ctk.CTkEntry(panel, font=entry_font, width=70)
        self.entry_paginas.grid(row=1, column=3, padx=(4,12), pady=(0,12), sticky="w")
        self.entry_paginas.insert(0, "2")

        # ── Linha 2: modo + datas ──────────────────────────────────────────
        sep = ctk.CTkFrame(panel, fg_color="#e5e7eb", height=1)
        sep.grid(row=2, column=0, columnspan=7, sticky="ew", padx=16)

        self.modo_var = tk.StringVar(value="rate_shopper")

        modo_frame = ctk.CTkFrame(panel, fg_color="transparent")
        modo_frame.grid(row=3, column=0, columnspan=7, padx=16, pady=(10,4), sticky="w")

        ctk.CTkLabel(modo_frame, text="Modo:", font=label_font, text_color=SUBTEXTO
                     ).pack(side="left", padx=(0,8))
        ctk.CTkRadioButton(
            modo_frame, text="Rate Shopper (por data)",
            variable=self.modo_var, value="rate_shopper",
            font=ctk.CTkFont(size=13), command=self._on_modo_change,
        ).pack(side="left", padx=(0,20))
        ctk.CTkRadioButton(
            modo_frame, text="Busca simples (período)",
            variable=self.modo_var, value="simples",
            font=ctk.CTkFont(size=13), command=self._on_modo_change,
        ).pack(side="left")

        # ── Campos de data (dinâmicos por modo) ───────────────────────────
        self.datas_frame = ctk.CTkFrame(panel, fg_color="transparent")
        self.datas_frame.grid(row=4, column=0, columnspan=7, padx=16, pady=(4,14), sticky="w")

        hoje = datetime.today()
        self._data_inicio_str = tk.StringVar(value=(hoje + timedelta(days=1)).strftime("%d/%m/%Y"))
        self._data_fim_str    = tk.StringVar(value=(hoje + timedelta(days=8)).strftime("%d/%m/%Y"))

        # Rate shopper: de / até
        self._frame_rs = ctk.CTkFrame(self.datas_frame, fg_color="transparent")
        ctk.CTkLabel(self._frame_rs, text="De", font=label_font, text_color=SUBTEXTO
                     ).grid(row=0, column=0, padx=(0,4), sticky="w")
        self.entry_data_de = ctk.CTkEntry(self._frame_rs, font=entry_font, width=entry_w,
                                           textvariable=self._data_inicio_str)
        self.entry_data_de.grid(row=0, column=1, padx=(0,16))
        ctk.CTkLabel(self._frame_rs, text="Até", font=label_font, text_color=SUBTEXTO
                     ).grid(row=0, column=2, padx=(0,4), sticky="w")
        self.entry_data_ate = ctk.CTkEntry(self._frame_rs, font=entry_font, width=entry_w,
                                            textvariable=self._data_fim_str)
        self.entry_data_ate.grid(row=0, column=3, padx=(0,16))
        ctk.CTkLabel(self._frame_rs, text="(uma diária por dia)", font=ctk.CTkFont(size=11),
                     text_color=SUBTEXTO).grid(row=0, column=4)

        # Busca simples: checkin / checkout
        self._frame_simples = ctk.CTkFrame(self.datas_frame, fg_color="transparent")
        ctk.CTkLabel(self._frame_simples, text="Check-in", font=label_font, text_color=SUBTEXTO
                     ).grid(row=0, column=0, padx=(0,4), sticky="w")
        self.entry_checkin = ctk.CTkEntry(self._frame_simples, font=entry_font, width=entry_w,
                                           textvariable=self._data_inicio_str)
        self.entry_checkin.grid(row=0, column=1, padx=(0,16))
        ctk.CTkLabel(self._frame_simples, text="Check-out", font=label_font, text_color=SUBTEXTO
                     ).grid(row=0, column=2, padx=(0,4), sticky="w")
        self.entry_checkout = ctk.CTkEntry(self._frame_simples, font=entry_font, width=entry_w,
                                            textvariable=self._data_fim_str)
        self.entry_checkout.grid(row=0, column=3)

        self._on_modo_change()  # mostra o frame correto

        # ── Botões ────────────────────────────────────────────────────────
        btn_frame = ctk.CTkFrame(panel, fg_color="transparent")
        btn_frame.grid(row=5, column=0, columnspan=7, padx=16, pady=(0,14), sticky="w")

        self.btn_buscar = ctk.CTkButton(
            btn_frame, text="▶  Buscar", width=130, height=36,
            fg_color=AZUL, hover_color=AZUL_HOVER,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._on_buscar,
        )
        self.btn_buscar.pack(side="left", padx=(0,10))

        self.btn_export_excel = ctk.CTkButton(
            btn_frame, text="⬇  Excel", width=110, height=36,
            fg_color="#2d8a4e", hover_color="#246e3e",
            font=ctk.CTkFont(size=13),
            state="disabled",
            command=self._on_export_excel,
        )
        self.btn_export_excel.pack(side="left", padx=(0,8))

        self.btn_export_csv = ctk.CTkButton(
            btn_frame, text="⬇  CSV", width=100, height=36,
            fg_color="#6b7280", hover_color="#4b5563",
            font=ctk.CTkFont(size=13),
            state="disabled",
            command=self._on_export_csv,
        )
        self.btn_export_csv.pack(side="left")

    # ── Painel de resultados ──────────────────────────────────────────────────
    def _build_results_panel(self):
        panel = ctk.CTkFrame(self, fg_color=BRANCO, corner_radius=8)
        panel.grid(row=2, column=0, sticky="nsew", padx=16, pady=12)
        panel.grid_rowconfigure(1, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        # Cabeçalho do painel
        ctk.CTkLabel(
            panel, text="Resultados",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEXTO,
        ).grid(row=0, column=0, padx=16, pady=(10, 6), sticky="w")

        # Container da tabela com scrollbars
        table_frame = ctk.CTkFrame(panel, fg_color="transparent")
        table_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background=BRANCO,
                        fieldbackground=BRANCO,
                        foreground=TEXTO,
                        rowheight=28,
                        font=("Segoe UI", 11))
        style.configure("Treeview.Heading",
                        background="#e5e7eb",
                        foreground=TEXTO,
                        font=("Segoe UI", 11, "bold"),
                        relief="flat")
        style.map("Treeview", background=[("selected", "#dbeafe")])
        style.map("Treeview.Heading", background=[("active", "#d1d5db")])

        self.tree = ttk.Treeview(table_frame, show="headings", selectmode="browse")
        self.tree.grid(row=0, column=0, sticky="nsew")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        hsb.grid(row=1, column=0, sticky="ew")
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Estado vazio
        self._mostrar_estado_vazio()

    # ── Status bar ────────────────────────────────────────────────────────────
    def _build_status_bar(self):
        bar = ctk.CTkFrame(self, fg_color=BRANCO, corner_radius=0, height=44)
        bar.grid(row=3, column=0, sticky="ew")
        bar.grid_propagate(False)
        bar.grid_columnconfigure(1, weight=1)

        self.lbl_status = ctk.CTkLabel(
            bar, text="Pronto.",
            font=ctk.CTkFont(size=12),
            text_color=SUBTEXTO,
        )
        self.lbl_status.grid(row=0, column=0, padx=16, pady=10, sticky="w")

        self.progress = ctk.CTkProgressBar(bar, width=200, height=8)
        self.progress.grid(row=0, column=1, padx=16, pady=10, sticky="e")
        self.progress.set(0)
        self.progress.grid_remove()

    # ─────────────────────────────────────────────────────────────────────────
    # Helpers de estado
    # ─────────────────────────────────────────────────────────────────────────
    def _on_modo_change(self):
        self._frame_rs.pack_forget()
        self._frame_simples.pack_forget()
        if self.modo_var.get() == "rate_shopper":
            self._frame_rs.pack(side="left")
        else:
            self._frame_simples.pack(side="left")

    def _mostrar_estado_vazio(self):
        for col in self.tree["columns"]:
            self.tree.heading(col, text="")
        self.tree["columns"] = ("msg",)
        self.tree.heading("msg", text="")
        self.tree.column("msg", width=400, anchor="center")
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.tree.insert("", "end", values=("Faça uma busca para ver os resultados.",))

    def set_status(self, texto: str, progresso: float = None):
        """Atualiza label de status e barra de progresso (thread-safe via after)."""
        def _update():
            self.lbl_status.configure(text=texto)
            if progresso is not None:
                self.progress.grid()
                self.progress.set(progresso)
            else:
                self.progress.grid_remove()
        self.after(0, _update)

    def set_buscando(self, ativo: bool):
        """Ativa/desativa o estado de "buscando" na UI."""
        def _update():
            if ativo:
                self.btn_buscar.configure(state="disabled", text="⏳ Buscando...")
                self.btn_export_excel.configure(state="disabled")
                self.btn_export_csv.configure(state="disabled")
                self.progress.grid()
                self.progress.configure(mode="indeterminate")
                self.progress.start()
            else:
                self.btn_buscar.configure(state="normal", text="▶  Buscar")
                self.progress.stop()
                self.progress.configure(mode="determinate")
                self.progress.set(1)
        self.after(0, _update)

    def mostrar_resultados(self, hoteis: list[dict], modo: str):
        """Popula a tabela com os resultados. Chamado via after() do worker."""
        def _update():
            for item in self.tree.get_children():
                self.tree.delete(item)

            if not hoteis:
                self._mostrar_estado_vazio()
                return

            if modo == "rate_shopper":
                self._popular_rate_shopper(hoteis)
            else:
                self._popular_simples(hoteis)

            self.btn_export_excel.configure(state="normal")
            self.btn_export_csv.configure(state="normal")
            self._ultimo_resultado = (hoteis, modo)

        self.after(0, _update)

    def _popular_rate_shopper(self, hoteis: list[dict]):
        from rate_shopper import montar_tabela
        tabela, datas = montar_tabela(hoteis)

        # Colunas: Hotel, Nota, + preço por data
        colunas = ["hotel", "nota"] + [f"d_{d}" for d in datas]
        self.tree["columns"] = colunas
        self.tree.heading("hotel", text="Hotel")
        self.tree.column("hotel", width=240, anchor="w", stretch=False)
        self.tree.heading("nota",  text="Nota")
        self.tree.column("nota",   width=55, anchor="center", stretch=False)
        for d in datas:
            from datetime import datetime as dt
            label = dt.strptime(d, "%Y-%m-%d").strftime("%d/%m")
            self.tree.heading(f"d_{d}", text=label)
            self.tree.column(f"d_{d}", width=90, anchor="center", stretch=False)

        for nome, info in sorted(tabela.items()):
            row = [nome, info.get("avaliacao") or "-"]
            for d in datas:
                dado = info["dados"].get(d, {})
                p = dado.get("preco")
                desc = dado.get("desconto_pct")
                if p:
                    cell = f"R${p:,.0f}".replace(",", ".")
                    if desc:
                        cell += f" -{desc:.0f}%"
                else:
                    cell = "-"
                row.append(cell)
            self.tree.insert("", "end", values=row)

    def _popular_simples(self, hoteis: list[dict]):
        colunas = ["hotel", "nota", "preco", "original", "desconto", "economia"]
        self.tree["columns"] = colunas
        larguras = [280, 55, 100, 100, 70, 100]
        titulos  = ["Hotel", "Nota", "Preço", "Original", "Desc%", "Economia"]
        for col, larg, titulo in zip(colunas, larguras, titulos):
            self.tree.heading(col, text=titulo)
            self.tree.column(col, width=larg, anchor="center" if col != "hotel" else "w", stretch=False)

        for h in sorted(hoteis, key=lambda x: x.get("preco_com_desconto") or 0):
            p     = h.get("preco_com_desconto")
            orig  = h.get("preco_original")
            desc  = h.get("desconto_percentual")
            econ  = h.get("economia")
            self.tree.insert("", "end", values=[
                h["nome"],
                h.get("avaliacao") or "-",
                f"R${p:,.0f}".replace(",", ".") if p else "-",
                f"R${orig:,.0f}".replace(",", ".") if orig else "-",
                f"{desc:.0f}%" if desc else "-",
                f"R${econ:,.0f}".replace(",", ".") if econ else "-",
            ])

    # ─────────────────────────────────────────────────────────────────────────
    # Callbacks dos botões (serão conectados ao worker nas próximas fases)
    # ─────────────────────────────────────────────────────────────────────────
    def _on_buscar(self):
        # Fase 3: conectar ao worker thread
        self.set_status("Em breve: worker thread será conectado aqui.")

    def _on_export_excel(self):
        # Fase 5: exportação
        self.set_status("Em breve: exportar Excel.")

    def _on_export_csv(self):
        # Fase 5: exportação
        self.set_status("Em breve: exportar CSV.")

    def obter_config(self) -> dict:
        """Retorna as configurações preenchidas pelo usuário."""
        return {
            "destino":  self.entry_destino.get().strip(),
            "adultos":  self.entry_adultos.get().strip(),
            "quartos":  self.entry_quartos.get().strip(),
            "paginas":  self.entry_paginas.get().strip(),
            "modo":     self.modo_var.get(),
            "data_de":  self._data_inicio_str.get().strip(),
            "data_ate": self._data_fim_str.get().strip(),
        }

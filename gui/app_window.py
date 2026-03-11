import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from datetime import datetime, timedelta
import os
import webbrowser

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

AZUL       = "#1a56a0"
AZUL_HOVER = "#154a8a"
VERMELHO   = "#dc2626"
VERM_HOVER = "#b91c1c"
VERDE      = "#2d8a4e"
CINZA_BG   = "#f0f2f5"
BRANCO     = "#ffffff"
TEXTO      = "#1a1a2e"
SUBTEXTO   = "#6b7280"
LINK_COR   = "#1a56a0"


class AppWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Rate Shopper — Booking.com")
        self.geometry("1200x760")
        self.minsize(960, 620)
        self.configure(fg_color=CINZA_BG)
        self._ultimo_resultado = None
        self._worker = None
        # links armazenados por item_id da tree
        self._links_por_item = {}
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
            header, text="Rate Shopper — Booking.com",
            font=ctk.CTkFont(size=18, weight="bold"), text_color=BRANCO,
        ).grid(row=0, column=0, padx=20, pady=14, sticky="w")

    # ── Painel de configuração ────────────────────────────────────────────────
    def _build_config_panel(self):
        panel = ctk.CTkFrame(self, fg_color=BRANCO, corner_radius=8)
        panel.grid(row=1, column=0, sticky="ew", padx=16, pady=(12, 0))
        panel.grid_columnconfigure((1, 3, 5), weight=1)

        lf  = ctk.CTkFont(size=12)
        ef  = ctk.CTkFont(size=13)
        ew  = 160

        # Linha 1: campos de texto
        ctk.CTkLabel(panel, text="Destino", font=lf, text_color=SUBTEXTO
                     ).grid(row=0, column=0, padx=(16,4), pady=(14,2), sticky="w")
        self.entry_destino = ctk.CTkEntry(panel, font=ef, width=220, placeholder_text="ex: Lisboa")
        self.entry_destino.grid(row=1, column=0, padx=(16,12), pady=(0,12), sticky="w")
        self.entry_destino.insert(0, "Lisboa")

        ctk.CTkLabel(panel, text="Adultos", font=lf, text_color=SUBTEXTO
                     ).grid(row=0, column=1, padx=4, pady=(14,2), sticky="w")
        self.entry_adultos = ctk.CTkEntry(panel, font=ef, width=70)
        self.entry_adultos.grid(row=1, column=1, padx=(4,12), pady=(0,12), sticky="w")
        self.entry_adultos.insert(0, "2")

        ctk.CTkLabel(panel, text="Quartos", font=lf, text_color=SUBTEXTO
                     ).grid(row=0, column=2, padx=4, pady=(14,2), sticky="w")
        self.entry_quartos = ctk.CTkEntry(panel, font=ef, width=70)
        self.entry_quartos.grid(row=1, column=2, padx=(4,12), pady=(0,12), sticky="w")
        self.entry_quartos.insert(0, "1")

        ctk.CTkLabel(panel, text="Páginas por data", font=lf, text_color=SUBTEXTO
                     ).grid(row=0, column=3, padx=4, pady=(14,2), sticky="w")
        self.entry_paginas = ctk.CTkEntry(panel, font=ef, width=70)
        self.entry_paginas.grid(row=1, column=3, padx=(4,12), pady=(0,12), sticky="w")
        self.entry_paginas.insert(0, "2")

        # Separador
        ctk.CTkFrame(panel, fg_color="#e5e7eb", height=1
                     ).grid(row=2, column=0, columnspan=7, sticky="ew", padx=16)

        # Modo
        self.modo_var = tk.StringVar(value="rate_shopper")
        modo_frame = ctk.CTkFrame(panel, fg_color="transparent")
        modo_frame.grid(row=3, column=0, columnspan=7, padx=16, pady=(10,4), sticky="w")
        ctk.CTkLabel(modo_frame, text="Modo:", font=lf, text_color=SUBTEXTO).pack(side="left", padx=(0,8))
        ctk.CTkRadioButton(modo_frame, text="Rate Shopper (por data)",
                           variable=self.modo_var, value="rate_shopper",
                           font=ctk.CTkFont(size=13), command=self._on_modo_change,
                           ).pack(side="left", padx=(0,20))
        ctk.CTkRadioButton(modo_frame, text="Busca simples (período)",
                           variable=self.modo_var, value="simples",
                           font=ctk.CTkFont(size=13), command=self._on_modo_change,
                           ).pack(side="left")

        # Campos de data
        self.datas_frame = ctk.CTkFrame(panel, fg_color="transparent")
        self.datas_frame.grid(row=4, column=0, columnspan=7, padx=16, pady=(4,14), sticky="w")
        hoje = datetime.today()
        self._data_inicio_str = tk.StringVar(value=(hoje + timedelta(days=1)).strftime("%d/%m/%Y"))
        self._data_fim_str    = tk.StringVar(value=(hoje + timedelta(days=8)).strftime("%d/%m/%Y"))

        self._frame_rs = ctk.CTkFrame(self.datas_frame, fg_color="transparent")
        ctk.CTkLabel(self._frame_rs, text="De", font=lf, text_color=SUBTEXTO
                     ).grid(row=0, column=0, padx=(0,4), sticky="w")
        ctk.CTkEntry(self._frame_rs, font=ef, width=ew, textvariable=self._data_inicio_str
                     ).grid(row=0, column=1, padx=(0,16))
        ctk.CTkLabel(self._frame_rs, text="Até", font=lf, text_color=SUBTEXTO
                     ).grid(row=0, column=2, padx=(0,4), sticky="w")
        ctk.CTkEntry(self._frame_rs, font=ef, width=ew, textvariable=self._data_fim_str
                     ).grid(row=0, column=3, padx=(0,16))
        ctk.CTkLabel(self._frame_rs, text="(uma diária por dia)",
                     font=ctk.CTkFont(size=11), text_color=SUBTEXTO).grid(row=0, column=4)

        self._frame_simples = ctk.CTkFrame(self.datas_frame, fg_color="transparent")
        ctk.CTkLabel(self._frame_simples, text="Check-in", font=lf, text_color=SUBTEXTO
                     ).grid(row=0, column=0, padx=(0,4), sticky="w")
        ctk.CTkEntry(self._frame_simples, font=ef, width=ew, textvariable=self._data_inicio_str
                     ).grid(row=0, column=1, padx=(0,16))
        ctk.CTkLabel(self._frame_simples, text="Check-out", font=lf, text_color=SUBTEXTO
                     ).grid(row=0, column=2, padx=(0,4), sticky="w")
        ctk.CTkEntry(self._frame_simples, font=ef, width=ew, textvariable=self._data_fim_str
                     ).grid(row=0, column=3)

        self._on_modo_change()

        # Botões
        btn_frame = ctk.CTkFrame(panel, fg_color="transparent")
        btn_frame.grid(row=5, column=0, columnspan=7, padx=16, pady=(0,14), sticky="w")

        self.btn_buscar = ctk.CTkButton(
            btn_frame, text="▶  Buscar", width=130, height=36,
            fg_color=AZUL, hover_color=AZUL_HOVER,
            font=ctk.CTkFont(size=13, weight="bold"), command=self._on_buscar,
        )
        self.btn_buscar.pack(side="left", padx=(0,8))

        self.btn_parar = ctk.CTkButton(
            btn_frame, text="⏹  Parar", width=110, height=36,
            fg_color=VERMELHO, hover_color=VERM_HOVER,
            font=ctk.CTkFont(size=13), state="disabled", command=self._on_parar,
        )
        self.btn_parar.pack(side="left", padx=(0,16))

        self.btn_export_excel = ctk.CTkButton(
            btn_frame, text="⬇  Excel", width=110, height=36,
            fg_color=VERDE, hover_color="#246e3e",
            font=ctk.CTkFont(size=13), state="disabled", command=self._on_export_excel,
        )
        self.btn_export_excel.pack(side="left", padx=(0,8))

        self.btn_export_csv = ctk.CTkButton(
            btn_frame, text="⬇  CSV", width=100, height=36,
            fg_color="#6b7280", hover_color="#4b5563",
            font=ctk.CTkFont(size=13), state="disabled", command=self._on_export_csv,
        )
        self.btn_export_csv.pack(side="left")

    # ── Painel de resultados com abas ─────────────────────────────────────────
    def _build_results_panel(self):
        panel = ctk.CTkFrame(self, fg_color=BRANCO, corner_radius=8)
        panel.grid(row=2, column=0, sticky="nsew", padx=16, pady=12)
        panel.grid_rowconfigure(1, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        # Estilo compartilhado das tabelas
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background=BRANCO, fieldbackground=BRANCO,
                        foreground=TEXTO, rowheight=28, font=("Segoe UI", 11))
        style.configure("Treeview.Heading",
                        background="#e5e7eb", foreground=TEXTO,
                        font=("Segoe UI", 11, "bold"), relief="flat")
        style.map("Treeview", background=[("selected", "#dbeafe")])
        style.map("Treeview.Heading", background=[("active", "#d1d5db")])
        # tag de link (cor azul, cursor mãozinha)
        style.configure("Link.Treeview", foreground=LINK_COR)

        # Notebook (abas)
        notebook_style = ttk.Style()
        notebook_style.configure("TNotebook", background=BRANCO, borderwidth=0)
        notebook_style.configure("TNotebook.Tab",
                                 padding=[14, 6], font=("Segoe UI", 11),
                                 background="#e5e7eb", foreground=SUBTEXTO)
        notebook_style.map("TNotebook.Tab",
                           background=[("selected", BRANCO)],
                           foreground=[("selected", AZUL)],
                           font=[("selected", ("Segoe UI", 11, "bold"))])

        self.notebook = ttk.Notebook(panel)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        panel.grid_rowconfigure(0, weight=1)

        # ── Aba 1: Por data (preço, desconto, nota) ───────────────────────
        self._aba_precos   = self._criar_aba("📅  Por Data")
        self.tree_precos   = self._criar_treeview(self._aba_precos)
        self._links_precos = {}   # item_id → url
        self.tree_precos.bind("<Double-1>", lambda e: self._abrir_link(self.tree_precos, self._links_precos))
        self.tree_precos.bind("<Motion>",   lambda e: self._cursor_link(e, self.tree_precos))

        # ── Aba 2: Rate Shopper completo (exportável em Excel) ────────────
        self._aba_rate     = self._criar_aba("📊  Rate Shopper")
        self.tree_rate     = self._criar_treeview(self._aba_rate)
        self._links_rate   = {}
        self.tree_rate.bind("<Double-1>", lambda e: self._abrir_link(self.tree_rate, self._links_rate))
        self.tree_rate.bind("<Motion>",   lambda e: self._cursor_link(e, self.tree_rate))

        self._mostrar_estado_vazio(self.tree_precos, "Aba 1: preço por data com desconto e avaliação")
        self._mostrar_estado_vazio(self.tree_rate,   "Aba 2: Rate Shopper completo (todas as datas)")

        # Dica de link no rodapé da aba
        ctk.CTkLabel(self._aba_precos, text="Dica: clique duplo em um hotel para abrir no Booking.com",
                     font=ctk.CTkFont(size=11), text_color=SUBTEXTO,
                     ).pack(side="bottom", pady=(0, 6))
        ctk.CTkLabel(self._aba_rate, text="Dica: clique duplo em um hotel para abrir no Booking.com",
                     font=ctk.CTkFont(size=11), text_color=SUBTEXTO,
                     ).pack(side="bottom", pady=(0, 6))

    def _criar_aba(self, titulo: str) -> tk.Frame:
        frame = tk.Frame(self.notebook, bg=BRANCO)
        self.notebook.add(frame, text=titulo)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        return frame

    def _criar_treeview(self, parent) -> ttk.Treeview:
        frame = tk.Frame(parent, bg=BRANCO)
        frame.pack(fill="both", expand=True, padx=4, pady=4)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        tree = ttk.Treeview(frame, show="headings", selectmode="browse")
        tree.grid(row=0, column=0, sticky="nsew")

        vsb = ttk.Scrollbar(frame, orient="vertical",   command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        tree.tag_configure("link", foreground=LINK_COR)
        return tree

    # ── Status bar ────────────────────────────────────────────────────────────
    def _build_status_bar(self):
        bar = ctk.CTkFrame(self, fg_color=BRANCO, corner_radius=0, height=44)
        bar.grid(row=3, column=0, sticky="ew")
        bar.grid_propagate(False)
        bar.grid_columnconfigure(1, weight=1)

        self.lbl_status = ctk.CTkLabel(bar, text="Pronto.",
                                       font=ctk.CTkFont(size=12), text_color=SUBTEXTO)
        self.lbl_status.grid(row=0, column=0, padx=16, pady=10, sticky="w")

        self.progress = ctk.CTkProgressBar(bar, width=200, height=8)
        self.progress.grid(row=0, column=1, padx=16, pady=10, sticky="e")
        self.progress.set(0)
        self.progress.grid_remove()

    # ─────────────────────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────────────────────
    def _on_modo_change(self):
        self._frame_rs.pack_forget()
        self._frame_simples.pack_forget()
        if self.modo_var.get() == "rate_shopper":
            self._frame_rs.pack(side="left")
        else:
            self._frame_simples.pack(side="left")

    def _mostrar_estado_vazio(self, tree: ttk.Treeview, msg: str = ""):
        tree["columns"] = ("msg",)
        tree.heading("msg", text="")
        tree.column("msg", width=600, anchor="center")
        for item in tree.get_children():
            tree.delete(item)
        tree.insert("", "end", values=(msg or "Faça uma busca para ver os resultados.",))

    def set_status(self, texto: str, progresso: float = None):
        def _u():
            self.lbl_status.configure(text=texto)
            if progresso is not None:
                self.progress.grid()
                self.progress.set(max(0.0, min(1.0, progresso)))
            else:
                self.progress.grid_remove()
        self.after(0, _u)

    def set_buscando(self, ativo: bool):
        def _u():
            if ativo:
                self.btn_buscar.configure(state="disabled", text="⏳ Buscando...")
                self.btn_parar.configure(state="normal")
                self.btn_export_excel.configure(state="disabled")
                self.btn_export_csv.configure(state="disabled")
                self.progress.grid()
                self.progress.configure(mode="indeterminate")
                self.progress.start()
            else:
                self.btn_buscar.configure(state="normal", text="▶  Buscar")
                self.btn_parar.configure(state="disabled")
                self.progress.stop()
                self.progress.configure(mode="determinate")
                self.progress.set(1)
        self.after(0, _u)

    # ─────────────────────────────────────────────────────────────────────────
    # Popula as duas abas
    # ─────────────────────────────────────────────────────────────────────────
    def mostrar_resultados(self, hoteis: list[dict], modo: str):
        def _u():
            self._links_precos.clear()
            self._links_rate.clear()
            for t in (self.tree_precos, self.tree_rate):
                for item in t.get_children():
                    t.delete(item)

            if not hoteis:
                self._mostrar_estado_vazio(self.tree_precos)
                self._mostrar_estado_vazio(self.tree_rate)
                return

            self._popular_aba_precos(hoteis, modo)
            self._popular_aba_rate(hoteis)

            self.btn_export_excel.configure(state="normal")
            self.btn_export_csv.configure(state="normal")
            self._ultimo_resultado = (hoteis, modo)

        self.after(0, _u)

    def _popular_aba_precos(self, hoteis: list[dict], modo: str):
        """Aba 1 — tabela detalhada por hotel: preço, desconto, nota, link."""
        tree = self.tree_precos
        if modo == "rate_shopper":
            # Agrupa: uma linha por hotel+data, ordenado por data→hotel
            colunas  = ["data", "hotel", "nota", "preco", "original", "desconto", "economia", "link"]
            larguras = [80,     260,      55,     100,      100,        70,          100,        200]
            titulos  = ["Data", "Hotel",  "Nota", "Preço",  "Original", "Desc%",    "Economia", "Link (clique duplo)"]
        else:
            colunas  = ["hotel", "nota", "preco", "original", "desconto", "economia", "link"]
            larguras = [280,      55,     100,      100,        70,          100,        200]
            titulos  = ["Hotel",  "Nota", "Preço",  "Original", "Desc%",    "Economia", "Link (clique duplo)"]

        tree["columns"] = colunas
        for col, larg, titulo in zip(colunas, larguras, titulos):
            tree.heading(col, text=titulo)
            tree.column(col, width=larg,
                        anchor="w" if col in ("hotel", "link") else "center",
                        stretch=(col == "hotel"))

        def _inserir(h):
            p    = h.get("preco_com_desconto")
            orig = h.get("preco_original")
            desc = h.get("desconto_percentual")
            econ = h.get("economia")
            link = h.get("link") or ""
            vals_base = [
                h.get("avaliacao") or "-",
                f"R${p:,.0f}".replace(",", ".") if p else "-",
                f"R${orig:,.0f}".replace(",", ".") if orig else "-",
                f"{desc:.0f}%" if desc else "-",
                f"R${econ:,.0f}".replace(",", ".") if econ else "-",
                "🔗 Abrir no Booking" if link else "",
            ]
            if modo == "rate_shopper":
                data_label = h.get("checkin", "")
                try:
                    data_label = datetime.strptime(data_label, "%Y-%m-%d").strftime("%d/%m")
                except Exception:
                    pass
                vals = [data_label, h["nome"]] + vals_base
            else:
                vals = [h["nome"]] + vals_base

            tags = ("link",) if link else ()
            iid  = tree.insert("", "end", values=vals, tags=tags)
            if link:
                self._links_precos[iid] = link

        if modo == "rate_shopper":
            for h in sorted(hoteis, key=lambda x: (x.get("checkin",""), x.get("preco_com_desconto") or 0)):
                _inserir(h)
        else:
            for h in sorted(hoteis, key=lambda x: x.get("preco_com_desconto") or 0):
                _inserir(h)

    def _popular_aba_rate(self, hoteis: list[dict]):
        """Aba 2 — Rate Shopper: hotel × data, preço por coluna."""
        tree = self.tree_rate
        from rate_shopper import montar_tabela
        tabela, datas = montar_tabela(hoteis)

        colunas = ["hotel", "nota"] + [f"d_{d}" for d in datas] + ["link"]
        tree["columns"] = colunas
        tree.heading("hotel", text="Hotel")
        tree.column("hotel", width=240, anchor="w", stretch=False)
        tree.heading("nota",  text="Nota")
        tree.column("nota",   width=55,  anchor="center", stretch=False)
        for d in datas:
            label = datetime.strptime(d, "%Y-%m-%d").strftime("%d/%m")
            tree.heading(f"d_{d}", text=label)
            tree.column(f"d_{d}", width=95, anchor="center", stretch=False)
        tree.heading("link", text="Link")
        tree.column("link", width=180, anchor="w", stretch=False)

        # Para o link na aba rate, usa o primeiro link disponível do hotel
        links_por_nome = {}
        for h in hoteis:
            nome = h.get("nome")
            if nome and h.get("link") and nome not in links_por_nome:
                links_por_nome[nome] = h["link"]

        for nome, info in sorted(tabela.items()):
            row = [nome, info.get("avaliacao") or "-"]
            for d in datas:
                dado = info["dados"].get(d, {})
                p    = dado.get("preco")
                desc = dado.get("desconto_pct")
                if p:
                    cell = f"R${p:,.0f}".replace(",", ".")
                    if desc:
                        cell += f" -{desc:.0f}%"
                else:
                    cell = "-"
                row.append(cell)

            link = links_por_nome.get(nome, "")
            row.append("🔗 Abrir no Booking" if link else "")
            tags = ("link",) if link else ()
            iid  = tree.insert("", "end", values=row, tags=tags)
            if link:
                self._links_rate[iid] = link

    # ─────────────────────────────────────────────────────────────────────────
    # Link: abrir no browser + cursor
    # ─────────────────────────────────────────────────────────────────────────
    def _abrir_link(self, tree: ttk.Treeview, links: dict):
        sel = tree.selection()
        if not sel:
            return
        iid = sel[0]
        url = links.get(iid)
        if url:
            webbrowser.open(url)

    def _cursor_link(self, event, tree: ttk.Treeview):
        iid = tree.identify_row(event.y)
        if iid and "link" in tree.item(iid, "tags"):
            tree.configure(cursor="hand2")
        else:
            tree.configure(cursor="")

    # ─────────────────────────────────────────────────────────────────────────
    # Callbacks dos botões
    # ─────────────────────────────────────────────────────────────────────────
    def _on_buscar(self):
        erro = self._validar()
        if erro:
            messagebox.showerror("Campo inválido", erro)
            return
        self.set_buscando(True)
        self.set_status("Iniciando...")
        from gui.worker import ScraperWorker
        self._worker = ScraperWorker(self.obter_config(), self)
        self._worker.start()

    def _on_parar(self):
        if self._worker:
            self._worker.parar()
        self.btn_parar.configure(state="disabled", text="⏹ Parando...")
        self.set_status("Interrompendo busca...")

    def _on_export_excel(self):
        if not self._ultimo_resultado:
            return
        hoteis, modo = self._ultimo_resultado
        caminho = filedialog.asksaveasfilename(
            defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")],
            initialfile="rate_shopper.xlsx", initialdir=os.path.expanduser("~"),
        )
        if not caminho:
            return
        from rate_shopper import montar_tabela, salvar_excel_rate_shopper
        tabela, datas = montar_tabela(hoteis)
        salvar_excel_rate_shopper(tabela, datas, caminho)
        self.set_status(f"Excel salvo: {os.path.basename(caminho)}")

    def _on_export_csv(self):
        if not self._ultimo_resultado:
            return
        hoteis, modo = self._ultimo_resultado
        caminho = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV", "*.csv")],
            initialfile="rate_shopper.csv", initialdir=os.path.expanduser("~"),
        )
        if not caminho:
            return
        if modo == "rate_shopper":
            from rate_shopper import montar_tabela, salvar_csv_rate_shopper
            tabela, datas = montar_tabela(hoteis)
            salvar_csv_rate_shopper(tabela, datas, caminho)
        else:
            from relatorio import salvar_csv
            salvar_csv(hoteis, caminho)
        self.set_status(f"CSV salvo: {os.path.basename(caminho)}")

    def _validar(self) -> str | None:
        cfg = self.obter_config()
        if not cfg["destino"]:
            return "Preencha o destino."
        for campo, label in [("adultos","Adultos"),("quartos","Quartos"),("paginas","Páginas")]:
            val = cfg[campo]
            if val and (not val.isdigit() or int(val) < 1):
                return f"{label} deve ser um número maior que zero."
        try:
            de  = datetime.strptime(cfg["data_de"],  "%d/%m/%Y")
            ate = datetime.strptime(cfg["data_ate"], "%d/%m/%Y")
        except ValueError:
            return "Datas inválidas. Use o formato dd/mm/aaaa."
        if ate < de:
            return "A data final não pode ser anterior à data inicial."
        return None

    def obter_config(self) -> dict:
        return {
            "destino":  self.entry_destino.get().strip(),
            "adultos":  self.entry_adultos.get().strip(),
            "quartos":  self.entry_quartos.get().strip(),
            "paginas":  self.entry_paginas.get().strip(),
            "modo":     self.modo_var.get(),
            "data_de":  self._data_inicio_str.get().strip(),
            "data_ate": self._data_fim_str.get().strip(),
        }

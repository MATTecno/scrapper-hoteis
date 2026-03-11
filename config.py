# ─── Configurações da busca ────────────────────────────────────────────────────
SEARCH_CONFIG = {
    "destino": "Lisboa",
    "adultos": 2,
    "quartos": 1,
    "paginas": 3,  # páginas por data (25 hotéis/página)
}

# ─── Rate Shopper: datas a monitorar ──────────────────────────────────────────
# Cada data = 1 diária (checkin + 1 dia). Deixe vazio [] para usar checkin/checkout simples.
DATAS_RATE_SHOPPER = [
    "2026-04-01",
    "2026-04-02",
    "2026-04-03",
    "2026-04-04",
    "2026-04-05",
    "2026-04-06",
    "2026-04-07",
]

# ─── Modo simples (busca única, sem rate shopper por data) ─────────────────────
CHECKIN  = "2026-04-01"
CHECKOUT = "2026-04-05"

# ─── Configurações do scraper ──────────────────────────────────────────────────
SCRAPER_CONFIG = {
    "headless": False,
    "delay_min": 2,
    "delay_max": 5,
    "timeout": 30000,
}

# ─── Arquivos de saída ─────────────────────────────────────────────────────────
OUTPUT_CSV        = "resultados.csv"
OUTPUT_JSON       = "resultados.json"
OUTPUT_RATE_CSV   = "rate_shopper.csv"
OUTPUT_RATE_EXCEL = "rate_shopper.xlsx"

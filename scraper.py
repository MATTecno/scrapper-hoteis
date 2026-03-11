import time
import random
import json
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from config import SEARCH_CONFIG, SCRAPER_CONFIG, CHECKIN, CHECKOUT


def delay():
    """Pausa aleatória para evitar detecção."""
    t = random.uniform(SCRAPER_CONFIG["delay_min"], SCRAPER_CONFIG["delay_max"])
    time.sleep(t)


def build_url(pagina: int = 0, checkin: str = None, checkout: str = None) -> str:
    cfg = SEARCH_CONFIG
    offset = pagina * 25
    ci = checkin or CHECKIN
    co = checkout or CHECKOUT
    url = (
        f"https://www.booking.com/searchresults.pt-br.html"
        f"?ss={cfg['destino'].replace(' ', '+')}"
        f"&checkin={ci}"
        f"&checkout={co}"
        f"&offset={offset}"
        f"&selected_currency=BRL"
        f"&lang=pt-br"
    )
    if cfg.get("adultos") is not None:
        url += f"&group_adults={cfg['adultos']}"
    if cfg.get("quartos") is not None:
        url += f"&no_rooms={cfg['quartos']}"
    return url


def extrair_hotel(card) -> dict | None:
    """Extrai dados de um card de hotel."""
    try:
        # Nome
        nome_el = card.query_selector('[data-testid="title"]')
        nome = nome_el.inner_text().strip() if nome_el else "N/A"

        import re
        preco_texto = None
        preco_original_texto = None

        # Busca a div de acessibilidade pelo conteúdo de texto (independente de classe)
        texto_acessibilidade = card.evaluate("""el => {
            for (const div of el.querySelectorAll('div')) {
                const t = div.innerText || '';
                if (t.includes('Preço atual') || t.includes('Preço original')) return t;
            }
            return null;
        }""")
        if texto_acessibilidade:
            match_atual = re.search(r"Preço atual[:\s]+R\$[\s\xa0]*([\d.,]+)", texto_acessibilidade)
            match_original = re.search(r"Preço original[:\s]+R\$[\s\xa0]*([\d.,]+)", texto_acessibilidade)
            if match_atual:
                preco_texto = "R$ " + match_atual.group(1)
            if match_original:
                preco_original_texto = "R$ " + match_original.group(1)

        # fallback: elementos visuais com data-testid
        if not preco_texto:
            preco_el = card.query_selector('[data-testid="price-and-discounted-price"]')
            preco_texto = preco_el.inner_text().strip() if preco_el else None
        if not preco_original_texto:
            preco_original_el = card.query_selector('[data-testid="strikethrough-price"]')
            preco_original_texto = preco_original_el.inner_text().strip() if preco_original_el else None

        # Badge de desconto: tenta pegar do site, senão calcula pelos preços
        desconto_el = card.query_selector('[data-testid="recommended-units-badge"]')
        desconto_texto = desconto_el.inner_text().strip() if desconto_el else None

        # Avaliação: texto vem como "Com nota 9,0" — extrai só o número
        avaliacao = None
        avaliacao_el = card.query_selector('[data-testid="review-score"]')
        if avaliacao_el:
            import re
            texto = avaliacao_el.get_attribute("aria-label") or avaliacao_el.inner_text()
            match = re.search(r"(\d+[.,]\d+|\d+)", texto)
            if match:
                avaliacao = match.group(1).replace(",", ".")

        # Número de avaliações
        num_avaliacoes = None
        avaliacao_container = card.query_selector('[data-testid="review-score"]')
        if avaliacao_container:
            partes = avaliacao_container.inner_text().split("\n")
            # Última linha costuma ser "X avaliações"
            for parte in reversed(partes):
                if "avalia" in parte.lower() or parte.strip().isdigit():
                    num_avaliacoes = parte.strip()
                    break

        # Link do hotel
        link_el = card.query_selector('a[data-testid="title-link"]')
        link = link_el.get_attribute("href") if link_el else None
        if link and not link.startswith("http"):
            link = "https://www.booking.com" + link

        # Localização
        local_el = card.query_selector('[data-testid="address-link"]')
        localizacao = local_el.inner_text().strip() if local_el else None

        # Tipo de acomodação
        tipo_el = card.query_selector('[data-testid="recommended-units"] h4, [data-testid="property-type"]')
        tipo = tipo_el.inner_text().strip() if tipo_el else None

        preco_final = limpar_preco(preco_texto)
        preco_orig = limpar_preco(preco_original_texto)
        desconto_pct = extrair_percentual(desconto_texto)
        # Se não teve badge, calcula pelo preço original e final
        if desconto_pct is None and preco_orig and preco_final and preco_orig > preco_final:
            desconto_pct = round((1 - preco_final / preco_orig) * 100, 1)

        return {
            "nome": nome,
            "preco_com_desconto": preco_final,
            "preco_original": preco_orig,
            "desconto_percentual": desconto_pct,
            "economia": round(preco_orig - preco_final, 2) if preco_orig and preco_final and preco_orig > preco_final else None,
            "avaliacao": avaliacao,
            "num_avaliacoes": num_avaliacoes,
            "localizacao": localizacao,
            "tipo": tipo,
            "link": link,
            "coletado_em": datetime.now().isoformat(),
        }
    except Exception as e:
        print(f"  Erro ao extrair hotel: {e}")
        return None


def limpar_preco(texto: str | None) -> float | None:
    """Converte string de preço BR para float.
    Ex: 'R$ 1.234'   -> 1234.0   (ponto = milhar)
        'R$ 1.234,56 -> 1234.56  (ponto = milhar, vírgula = decimal)
        'R$ 1234,56' -> 1234.56  (só vírgula = decimal)
    """
    if not texto:
        return None
    import re
    numeros = re.sub(r"[^\d,\.]", "", texto)
    if "," in numeros and "." in numeros:
        # 1.234,56 → remove ponto de milhar, troca vírgula por ponto
        numeros = numeros.replace(".", "").replace(",", ".")
    elif "," in numeros:
        # 1234,56 → vírgula é decimal
        numeros = numeros.replace(",", ".")
    elif "." in numeros:
        # 1.234 → ponto é separador de milhar (padrão BR sem centavos)
        numeros = numeros.replace(".", "")
    try:
        return float(numeros)
    except ValueError:
        return None


def extrair_percentual(texto: str | None) -> float | None:
    """Extrai percentual de desconto. Ex: '-20%' -> 20.0"""
    if not texto:
        return None
    import re
    match = re.search(r"(\d+)", texto)
    return float(match.group(1)) if match else None


def calcular_economia(preco_original: str | None, preco_final: str | None) -> float | None:
    """Calcula valor economizado em reais."""
    orig = limpar_preco(preco_original)
    final = limpar_preco(preco_final)
    if orig and final and orig > final:
        return round(orig - final, 2)
    return None


def _scrape_paginas(page, checkin: str, checkout: str, paginas: int,
                    on_progress=None) -> list[dict]:
    """Coleta hotéis de múltiplas páginas para um par checkin/checkout."""
    hoteis = []
    cookie_fechado = False

    for num_pagina in range(paginas):
        url = build_url(num_pagina, checkin, checkout)
        msg = f"Página {num_pagina + 1}/{paginas} — {checkin}"
        print(f"\n  [{msg}] {url}")
        if on_progress:
            on_progress(msg, (num_pagina) / paginas)

        try:
            page.goto(url, timeout=SCRAPER_CONFIG["timeout"], wait_until="domcontentloaded")
            delay()

            if not cookie_fechado:
                try:
                    btn = page.query_selector('#onetrust-accept-btn-handler, button[id*="accept"]')
                    if btn:
                        btn.click()
                        delay()
                        cookie_fechado = True
                except Exception:
                    pass

            page.wait_for_selector('[data-testid="property-card"]', timeout=SCRAPER_CONFIG["timeout"])

            for _ in range(3):
                page.keyboard.press("End")
                time.sleep(1)
            page.keyboard.press("Home")
            delay()

            cards = page.query_selector_all('[data-testid="property-card"]')
            print(f"  Encontrados {len(cards)} hotéis")

            for card in cards:
                hotel = extrair_hotel(card)
                if hotel and hotel["nome"] != "N/A":
                    hotel["checkin"] = checkin
                    hotel["checkout"] = checkout
                    hoteis.append(hotel)
                    preco_str = f"R$ {hotel['preco_com_desconto']}" if hotel["preco_com_desconto"] else "sem preço"
                    desc_str = f" (-{hotel['desconto_percentual']}%)" if hotel["desconto_percentual"] else ""
                    print(f"  + {hotel['nome'][:50]} | {preco_str}{desc_str}")

        except PlaywrightTimeout:
            print(f"  Timeout na página {num_pagina + 1}, pulando...")
        except Exception as e:
            print(f"  Erro na página {num_pagina + 1}: {e}")

        delay()

    return hoteis


def _criar_browser(p):
    browser = p.chromium.launch(
        headless=SCRAPER_CONFIG["headless"],
        args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
    )
    context = browser.new_context(
        viewport={"width": 1366, "height": 768},
        user_agent=(
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ),
        locale="pt-BR",
    )
    page = context.new_page()
    page.add_init_script("Object.defineProperty(navigator, 'webdriver', { get: () => undefined });")
    return browser, page


def scrape(checkin: str = None, checkout: str = None, paginas: int = None,
           on_progress=None) -> list[dict]:
    """Busca simples: uma data ou período."""
    ci = checkin or CHECKIN
    co = checkout or CHECKOUT
    total_paginas = paginas or SEARCH_CONFIG["paginas"]

    print(f"\nBuscando {SEARCH_CONFIG['destino']} | {ci} → {co}")

    with sync_playwright() as p:
        browser, page = _criar_browser(p)
        hoteis = _scrape_paginas(page, ci, co, total_paginas, on_progress)
        browser.close()

    print(f"\nTotal coletado: {len(hoteis)} hotéis")
    return hoteis


def scrape_rate_shopper(datas: list[str], paginas: int = None,
                        on_progress=None) -> list[dict]:
    """
    Rate Shopper: coleta preços para cada data individualmente (1 diária cada).
    Retorna lista com todos os hotéis de todas as datas.
    """
    total_paginas = paginas or SEARCH_CONFIG["paginas"]
    total_passos  = len(datas) * total_paginas
    passo_atual   = 0
    todos = []

    with sync_playwright() as p:
        browser, page = _criar_browser(p)

        for data in datas:
            checkout = (datetime.strptime(data, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
            print(f"\n{'='*60}\n[Data] {data}\n{'='*60}")

            def _prog(msg, _pct=None, _data=data, _passo=passo_atual):
                nonlocal passo_atual
                passo_atual += 1
                if on_progress:
                    on_progress(f"{_data} — {msg}", passo_atual / total_passos)

            hoteis = _scrape_paginas(page, data, checkout, total_paginas, _prog)
            todos.extend(hoteis)

        browser.close()

    print(f"\nTotal coletado: {len(todos)} registros ({len(datas)} datas)")
    return todos


if __name__ == "__main__":
    hoteis = scrape()
    # Salvar JSON bruto para inspeção
    with open("resultados_raw.json", "w", encoding="utf-8") as f:
        json.dump(hoteis, f, ensure_ascii=False, indent=2)
    print("Dados salvos em resultados_raw.json")

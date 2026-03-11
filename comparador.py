"""
Módulo de comparação e ranking de hotéis por preço e desconto.
"""


def filtrar_com_preco(hoteis: list[dict]) -> list[dict]:
    """Remove hotéis sem preço coletado."""
    return [h for h in hoteis if h.get("preco_com_desconto") is not None]


def ranking_menor_preco(hoteis: list[dict], top: int = 10) -> list[dict]:
    """Ordena pelos menores preços finais."""
    validos = filtrar_com_preco(hoteis)
    return sorted(validos, key=lambda h: h["preco_com_desconto"])[:top]


def ranking_maior_desconto_percentual(hoteis: list[dict], top: int = 10) -> list[dict]:
    """Ordena pelos maiores percentuais de desconto."""
    com_desconto = [h for h in hoteis if h.get("desconto_percentual")]
    return sorted(com_desconto, key=lambda h: h["desconto_percentual"], reverse=True)[:top]


def ranking_maior_economia(hoteis: list[dict], top: int = 10) -> list[dict]:
    """Ordena pelo maior valor economizado em reais."""
    com_economia = [h for h in hoteis if h.get("economia")]
    return sorted(com_economia, key=lambda h: h["economia"], reverse=True)[:top]


def ranking_custo_beneficio(hoteis: list[dict], top: int = 10) -> list[dict]:
    """
    Score combinado: considera preço baixo + desconto alto + boa avaliação.
    Score = (desconto% * 0.4) + (nota * 10 * 0.3) + (100 - preco_normalizado * 0.3)
    """
    validos = filtrar_com_preco(hoteis)
    if not validos:
        return []

    preco_min = min(h["preco_com_desconto"] for h in validos)
    preco_max = max(h["preco_com_desconto"] for h in validos)
    preco_range = preco_max - preco_min or 1

    def score(h):
        # Preço: quanto menor, mais próximo de 100
        preco_norm = ((h["preco_com_desconto"] - preco_min) / preco_range) * 100
        score_preco = 100 - preco_norm

        # Desconto: 0-100
        score_desconto = h.get("desconto_percentual") or 0

        # Avaliação: converte "8.5" para 85
        try:
            score_avaliacao = float(str(h.get("avaliacao") or "0").replace(",", ".")) * 10
        except (ValueError, TypeError):
            score_avaliacao = 0

        return (score_preco * 0.4) + (score_desconto * 0.3) + (score_avaliacao * 0.3)

    return sorted(validos, key=score, reverse=True)[:top]


def resumo_estatisticas(hoteis: list[dict]) -> dict:
    """Gera estatísticas gerais da busca."""
    validos = filtrar_com_preco(hoteis)
    com_desconto = [h for h in validos if h.get("desconto_percentual")]

    if not validos:
        return {"erro": "Nenhum hotel com preço encontrado"}

    precos = [h["preco_com_desconto"] for h in validos]
    descontos = [h["desconto_percentual"] for h in com_desconto]
    economias = [h["economia"] for h in validos if h.get("economia")]

    return {
        "total_hoteis": len(hoteis),
        "hoteis_com_preco": len(validos),
        "hoteis_com_desconto": len(com_desconto),
        "preco_minimo": min(precos),
        "preco_maximo": max(precos),
        "preco_medio": round(sum(precos) / len(precos), 2),
        "desconto_medio_percentual": round(sum(descontos) / len(descontos), 1) if descontos else 0,
        "desconto_maximo_percentual": max(descontos) if descontos else 0,
        "maior_economia_reais": max(economias) if economias else 0,
        "economia_total_potencial": round(sum(economias), 2) if economias else 0,
    }

"""
Uso:
  # Busca simples (um período, relatório de preços)
  python main.py

  # Rate Shopper (preço por data, tabela estilo PDF)
  python main.py --rate-shopper

  # Parâmetros opcionais
  python main.py --destino "Lisboa" --checkin 2026-05-01 --checkout 2026-05-05
  python main.py --rate-shopper --destino "Lisboa" --paginas 2 --headless
"""
import argparse
import sys
import json
from config import SEARCH_CONFIG, SCRAPER_CONFIG, CHECKIN, CHECKOUT, DATAS_RATE_SHOPPER
from scraper import scrape, scrape_rate_shopper
from comparador import (
    ranking_menor_preco, ranking_maior_desconto_percentual,
    ranking_maior_economia, ranking_custo_beneficio, resumo_estatisticas,
)
from relatorio import gerar_relatorio_completo
from rate_shopper import gerar_rate_shopper


def parse_args():
    parser = argparse.ArgumentParser(description="Scraper de preços — Booking.com")
    parser.add_argument("--rate-shopper", action="store_true",
                        help="Modo Rate Shopper: coleta preço por data e gera tabela")
    parser.add_argument("--destino",   type=str)
    parser.add_argument("--checkin",   type=str)
    parser.add_argument("--checkout",  type=str)
    parser.add_argument("--adultos",   type=int)
    parser.add_argument("--paginas",   type=int)
    parser.add_argument("--headless",  action="store_true")
    return parser.parse_args()


def aplicar_args(args):
    if args.destino:
        SEARCH_CONFIG["destino"] = args.destino
    if args.adultos:
        SEARCH_CONFIG["adultos"] = args.adultos
    if args.paginas:
        SEARCH_CONFIG["paginas"] = args.paginas
    if args.headless:
        SCRAPER_CONFIG["headless"] = True


def main():
    args = parse_args()
    aplicar_args(args)

    if args.rate_shopper:
        # ── Modo Rate Shopper ─────────────────────────────────────────────────
        print(f"\nModo: Rate Shopper")
        print(f"Destino: {SEARCH_CONFIG['destino']}")
        print(f"Datas: {DATAS_RATE_SHOPPER[0]} → {DATAS_RATE_SHOPPER[-1]} ({len(DATAS_RATE_SHOPPER)} dias)")

        hoteis = scrape_rate_shopper(DATAS_RATE_SHOPPER, paginas=SEARCH_CONFIG["paginas"])

        if not hoteis:
            print("Nenhum dado coletado.")
            sys.exit(1)

        gerar_rate_shopper(hoteis)

    else:
        # ── Modo busca simples ────────────────────────────────────────────────
        ci = args.checkin  or CHECKIN
        co = args.checkout or CHECKOUT

        print(f"\nModo: Busca simples")
        print(f"Destino: {SEARCH_CONFIG['destino']}  |  {ci} → {co}")
        print(f"Adultos: {SEARCH_CONFIG['adultos']}  |  Páginas: {SEARCH_CONFIG['paginas']}")

        hoteis = scrape(checkin=ci, checkout=co)

        if not hoteis:
            print("Nenhum hotel coletado.")
            sys.exit(1)

        rankings = {
            "menor_preco":    ranking_menor_preco(hoteis),
            "maior_desconto": ranking_maior_desconto_percentual(hoteis),
            "maior_economia": ranking_maior_economia(hoteis),
            "custo_beneficio": ranking_custo_beneficio(hoteis),
        }
        stats = resumo_estatisticas(hoteis)
        gerar_relatorio_completo(hoteis, stats, rankings)


if __name__ == "__main__":
    main()

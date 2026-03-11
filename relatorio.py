"""
Geração de relatórios: CSV, JSON e tabela no terminal.
"""
import csv
import json
from datetime import datetime
from config import OUTPUT_CSV, OUTPUT_JSON


def salvar_csv(hoteis: list[dict], caminho: str = OUTPUT_CSV):
    if not hoteis:
        print("Nenhum dado para salvar.")
        return
    campos = list(hoteis[0].keys())
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(hoteis)
    print(f"CSV salvo: {caminho} ({len(hoteis)} hotéis)")


def salvar_json(hoteis: list[dict], caminho: str = OUTPUT_JSON):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(hoteis, f, ensure_ascii=False, indent=2)
    print(f"JSON salvo: {caminho} ({len(hoteis)} hotéis)")


def formatar_preco(valor: float | None) -> str:
    if valor is None:
        return "  N/A    "
    return f"R$ {valor:>8.2f}"


def imprimir_tabela(titulo: str, hoteis: list[dict], mostrar_desconto: bool = True):
    if not hoteis:
        print(f"\n{titulo}: Nenhum resultado.")
        return

    print(f"\n{'='*90}")
    print(f"  {titulo}")
    print(f"{'='*90}")
    print(f"  {'#':<3} {'Hotel':<45} {'Preço Final':>12} {'Preço Orig':>11} {'Desc%':>6} {'Economia':>10} {'Nota':>5}")
    print(f"  {'-'*3} {'-'*45} {'-'*12} {'-'*11} {'-'*6} {'-'*10} {'-'*5}")

    for i, h in enumerate(hoteis, 1):
        nome = h["nome"][:44]
        preco_final = formatar_preco(h.get("preco_com_desconto"))
        preco_orig = formatar_preco(h.get("preco_original"))
        desconto = f"{h['desconto_percentual']:.0f}%" if h.get("desconto_percentual") else "   -  "
        economia = f"R$ {h['economia']:.2f}" if h.get("economia") else "    -     "
        nota = h.get("avaliacao") or "  -  "
        print(f"  {i:<3} {nome:<45} {preco_final:>12} {preco_orig:>11} {desconto:>6} {economia:>10} {nota:>5}")

    print(f"{'='*90}")


def imprimir_estatisticas(stats: dict):
    print(f"\n{'='*50}")
    print("  RESUMO GERAL DA BUSCA")
    print(f"{'='*50}")
    for chave, valor in stats.items():
        label = chave.replace("_", " ").title()
        if isinstance(valor, float):
            if "preco" in chave or "economia" in chave:
                print(f"  {label:<35} R$ {valor:.2f}")
            else:
                print(f"  {label:<35} {valor}")
        else:
            print(f"  {label:<35} {valor}")
    print(f"{'='*50}")


def gerar_relatorio_completo(hoteis: list[dict], stats: dict, rankings: dict):
    """Imprime relatório completo no terminal e salva arquivos."""
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    print(f"\n{'#'*90}")
    print(f"  RELATÓRIO DE COMPARAÇÃO DE PREÇOS - BOOKING.COM  |  {agora}")
    print(f"{'#'*90}")

    imprimir_estatisticas(stats)
    imprimir_tabela("TOP 10 - MENOR PREÇO FINAL", rankings["menor_preco"])
    imprimir_tabela("TOP 10 - MAIOR DESCONTO (%)", rankings["maior_desconto"])
    imprimir_tabela("TOP 10 - MAIOR ECONOMIA (R$)", rankings["maior_economia"])
    imprimir_tabela("TOP 10 - MELHOR CUSTO-BENEFÍCIO", rankings["custo_beneficio"])

    salvar_csv(hoteis)
    salvar_json(hoteis)

"""
Módulo de auto-atualização.

Uso:
    from updater import verificar_atualizacao, baixar_e_instalar, CURRENT_VERSION
"""
import os
import sys
import subprocess
import tempfile
from urllib import request, error
import json

CURRENT_VERSION = "1.0.0"

GITHUB_OWNER = "mattecnologia"
GITHUB_REPO  = "scrapping-booking"


# ─────────────────────────────────────────────────────────────────────────────
# Helpers de semver
# ─────────────────────────────────────────────────────────────────────────────

def _parse_version(tag: str) -> tuple[int, ...]:
    """Converte uma tag como 'v1.2.3' ou '1.2.3' em (1, 2, 3)."""
    tag = tag.lstrip("v").strip()
    parts = []
    for part in tag.split("."):
        try:
            parts.append(int(part))
        except ValueError:
            parts.append(0)
    # normaliza para 3 partes
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])


def _versao_mais_nova(tag_remota: str, versao_atual: str) -> bool:
    """Retorna True se a versão remota for maior que a atual."""
    return _parse_version(tag_remota) > _parse_version(versao_atual)


# ─────────────────────────────────────────────────────────────────────────────
# API pública
# ─────────────────────────────────────────────────────────────────────────────

def verificar_atualizacao(owner: str = GITHUB_OWNER, repo: str = GITHUB_REPO) -> dict | None:
    """
    Consulta a API do GitHub e retorna o dict da release se houver versão mais
    recente que CURRENT_VERSION, ou None caso contrário.

    O dict retornado inclui pelo menos:
        tag_name  (str)   — ex: "v1.2.0"
        body      (str)   — release notes
        assets    (list)  — lista de assets da release
        html_url  (str)   — URL da página da release
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    try:
        req = request.Request(
            url,
            headers={
                "Accept":     "application/vnd.github+json",
                "User-Agent": f"scrapping-booking/{CURRENT_VERSION}",
            },
        )
        with request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as exc:
        if exc.code == 404:
            # Repositório sem releases ainda
            return None
        raise RuntimeError(f"Erro HTTP {exc.code} ao verificar atualizações.") from exc
    except error.URLError as exc:
        raise RuntimeError(f"Sem conexão com a internet: {exc.reason}") from exc
    except Exception as exc:
        raise RuntimeError(f"Erro inesperado ao verificar atualizações: {exc}") from exc

    tag = data.get("tag_name", "")
    if not tag:
        return None

    if _versao_mais_nova(tag, CURRENT_VERSION):
        return data

    return None


def baixar_e_instalar(url: str, on_progress=None):
    """
    Baixa o arquivo no *url* para um arquivo temporário.

    - Windows: salva em %TEMP% e exibe instrução para o usuário substituir o .exe.
    - Linux/Mac: salva no mesmo diretório do executável atual.

    Parâmetros
    ----------
    url          : URL de download direto do asset
    on_progress  : callable(bytes_baixados, total_bytes) — pode ser None

    Retorna o caminho onde o arquivo foi salvo.
    """
    # Determina onde salvar
    if sys.platform == "win32":
        destino_dir = tempfile.gettempdir()
    else:
        if getattr(sys, "frozen", False):
            destino_dir = os.path.dirname(os.path.abspath(sys.executable))
        else:
            destino_dir = os.path.dirname(os.path.abspath(__file__))

    nome_arquivo = os.path.basename(url.split("?")[0]) or "scrapping-booking-update"
    destino = os.path.join(destino_dir, nome_arquivo)

    try:
        req = request.Request(
            url,
            headers={"User-Agent": f"scrapping-booking/{CURRENT_VERSION}"},
        )
        with request.urlopen(req, timeout=60) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            baixados = 0
            chunk = 65536  # 64 KB
            with open(destino, "wb") as f:
                while True:
                    bloco = resp.read(chunk)
                    if not bloco:
                        break
                    f.write(bloco)
                    baixados += len(bloco)
                    if on_progress:
                        on_progress(baixados, total)
    except error.URLError as exc:
        raise RuntimeError(f"Falha no download: {exc.reason}") from exc
    except OSError as exc:
        raise RuntimeError(f"Erro ao salvar arquivo: {exc}") from exc

    # Windows: prepara script .bat para substituir o executável em execução
    if sys.platform == "win32" and getattr(sys, "frozen", False):
        exe_atual = os.path.abspath(sys.executable)
        bat_path  = os.path.join(tempfile.gettempdir(), "_scrapping_update.bat")
        bat_conteudo = (
            "@echo off\n"
            "timeout /t 2 /nobreak >nul\n"
            f'copy /Y "{destino}" "{exe_atual}"\n'
            f'start "" "{exe_atual}"\n'
            f'del "%~f0"\n'
        )
        with open(bat_path, "w", encoding="cp1252") as bat:
            bat.write(bat_conteudo)
        # NÃO executa aqui — o caller decide quando lançar o bat

    return destino

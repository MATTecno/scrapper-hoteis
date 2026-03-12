"""
Telemetria de uso — fire-and-forget, sem bloquear a GUI.
Falha silenciosamente em qualquer erro de rede ou configuração.
"""
import json
import sys
import threading
import uuid
from urllib import request, error

_SUPABASE_URL = "https://rxhxtnvjnzpdvvmctkmw.supabase.co"
_ANON_KEY = "%%SUPABASE_ANON_KEY%%"  # substituído pelo CI no build

# Permite sobrescrever localmente via variável de ambiente (nunca commitar o valor)
import os as _os
_env_key = _os.environ.get("SUPABASE_ANON_KEY")
if _env_key:
    _ANON_KEY = _env_key

# UUID gerado em memória a cada abertura — nunca salvo em disco
_session_id = str(uuid.uuid4())


def _versao() -> str:
    try:
        from version import VERSION
        return VERSION
    except Exception:
        return "unknown"


def _enviar(payload: dict):
    """Executa em thread daemon — falha silenciosa."""
    try:
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            f"{_SUPABASE_URL}/rest/v1/telemetria_eventos",
            data=body,
            headers={
                "apikey":        _ANON_KEY,
                "Authorization": f"Bearer {_ANON_KEY}",
                "Content-Type":  "application/json",
                "Prefer":        "return=minimal",
            },
            method="POST",
        )
        with request.urlopen(req, timeout=8):
            pass
    except Exception:
        pass


def registrar(evento: str, **kwargs):
    """
    Registra um evento de telemetria de forma assíncrona.

    Parâmetros opcionais via kwargs:
        modo     (str)  — 'rate_shopper' | 'simples'
        hoteis_n (int)  — quantidade de hotéis retornados
        cancelada (bool) — busca foi cancelada pelo usuário
    """
    payload = {
        "evento":     evento,
        "versao":     _versao(),
        "plataforma": sys.platform,
        "session_id": _session_id,
    }
    if "modo" in kwargs:
        payload["modo"] = kwargs["modo"]
    if "hoteis_n" in kwargs:
        payload["hoteis_n"] = int(kwargs["hoteis_n"])

    threading.Thread(target=_enviar, args=(payload,), daemon=True).start()

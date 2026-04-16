"""Consulta de CEP por endereço na API ViaCEP (logradouro)."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from urllib.parse import quote

from app.utils.validation import remove_accentuation

VIACEP_BASE = "https://viacep.com.br/ws"
MIN_SEGMENT_LEN = 3


def _normalize_match(s: str) -> str:
    return remove_accentuation(str(s or "").strip()).lower()


def _only_digits_cep(cep: str) -> str:
    return "".join(filter(str.isdigit, str(cep)))


def buscar_cep_por_endereco(
    uf: str | None,
    cidade: str | None,
    logradouro: str | None,
    bairro_planilha: str | None = None,
) -> str | None:
    """
    GET https://viacep.com.br/ws/{uf}/{cidade}/{logradouro}/json/
    Retorna 8 dígitos ou None. Com vários resultados e bairro na planilha,
    filtra onde o bairro da API (normalizado) contém o bairro da planilha (normalizado).
    Com vários após o filtro, usa o primeiro (ordem ViaCEP).
    """
    uf = (uf or "").strip().upper()
    cidade = (cidade or "").strip()
    logradouro = (logradouro or "").strip()
    if len(uf) != 2 or len(cidade) < MIN_SEGMENT_LEN or len(logradouro) < MIN_SEGMENT_LEN:
        return None

    path = (
        f"{quote(uf, safe='')}/"
        f"{quote(cidade, safe='')}/"
        f"{quote(logradouro, safe='')}/json/"
    )
    url = f"{VIACEP_BASE}/{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "cadastro-art/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read().decode("utf-8")
    except (urllib.error.URLError, OSError, TimeoutError):
        return None

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None

    if not isinstance(data, list) or not data:
        return None

    items = [x for x in data if isinstance(x, dict) and x.get("cep")]
    if not items:
        return None

    bairro_key = (bairro_planilha or "").strip()
    if len(items) > 1 and bairro_key:
        needle = _normalize_match(bairro_key)
        if needle:
            filtered = [
                x
                for x in items
                if needle in _normalize_match(x.get("bairro", ""))
            ]
            if filtered:
                items = filtered

    digits = _only_digits_cep(str(items[0].get("cep", "")))
    return digits if len(digits) == 8 else None

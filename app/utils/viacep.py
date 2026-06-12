"""Consulta de CEP por endereço na API ViaCEP (logradouro)."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from urllib.parse import quote

from app.utils.validation import remove_accentuation

VIACEP_BASE = "https://viacep.com.br/ws"
MIN_SEGMENT_LEN = 3

GENERIC_CITY_LOGRADOURO_TERMS = ("Centro", "Rua", "Avenida", "Praca", "Travessa")


def _normalize_match(s: str) -> str:
    return remove_accentuation(str(s or "").strip()).lower()


def _only_digits_cep(cep: str) -> str:
    return "".join(filter(str.isdigit, str(cep)))


def _fetch_viacep_address_list(
    uf: str | None,
    cidade: str | None,
    logradouro: str | None,
) -> list[dict]:
    uf = (uf or "").strip().upper()
    cidade = (cidade or "").strip()
    logradouro = (logradouro or "").strip()
    if len(uf) != 2 or len(cidade) < MIN_SEGMENT_LEN or len(logradouro) < MIN_SEGMENT_LEN:
        return []

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
        return []

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []

    if not isinstance(data, list) or not data:
        return []

    return [x for x in data if isinstance(x, dict) and x.get("cep")]


def listar_ceps_por_endereco(
    uf: str | None,
    cidade: str | None,
    logradouro: str | None,
    bairro_planilha: str | None = None,
) -> list[str]:
    """
    GET https://viacep.com.br/ws/{uf}/{cidade}/{logradouro}/json/
    Retorna CEPs únicos (8 dígitos). Com bairro na planilha e vários resultados,
    prioriza itens cujo bairro da API contém o bairro informado.
    """
    items = _fetch_viacep_address_list(uf, cidade, logradouro)
    if not items:
        return []

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

    vistos: set[str] = set()
    ceps: list[str] = []
    for item in items:
        digits = _only_digits_cep(str(item.get("cep", "")))
        if len(digits) == 8 and digits not in vistos:
            vistos.add(digits)
            ceps.append(digits)
    return ceps


def buscar_cep_generico_cidade(uf: str | None, cidade: str | None) -> str | None:
    """CEP representativo da cidade (ex.: Centro), para bases que não têm o CEP exato."""
    for termo in GENERIC_CITY_LOGRADOURO_TERMS:
        ceps = listar_ceps_por_endereco(uf, cidade, termo)
        if ceps:
            return ceps[0]
    return None


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
    ceps = listar_ceps_por_endereco(uf, cidade, logradouro, bairro_planilha)
    return ceps[0] if ceps else None

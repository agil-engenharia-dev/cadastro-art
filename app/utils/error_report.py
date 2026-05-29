from __future__ import annotations

import json
import traceback
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import pandas as pd


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_str(value: Any) -> str:
    try:
        if value is None:
            return ""
        return str(value)
    except Exception:
        return "<valor_nao_serializavel>"


def humanizar_erro_validacao(msg: str) -> str:
    """
    Converte mensagens curtas do validation.py em texto mais explícito,
    sem precisar alterar a validação agora.
    """
    m = (msg or "").strip().upper()
    mapping = {
        "NOME ERROR": "Nome inválido (não foi possível interpretar como texto).",
        "CPF ERROR": "CPF inválido (deve ter 11 dígitos e dígitos verificadores válidos).",
        "SEXO ERROR": "Sexo inválido (valores aceitos: FEMININO ou MASCULINO).",
        "CEP ERROR": "CEP inválido (deve ter 8 dígitos).",
        "TIPO DE LOGRADOURO ERROR": "Tipo de logradouro inválido (valor não reconhecido).",
        "LOGRADOURO ERROR": "Logradouro inválido (não foi possível interpretar como texto).",
        "BAIRRO ERROR": "Bairro inválido (não foi possível interpretar como texto).",
        "CIDADE ERROR": "Cidade inválida (não foi possível interpretar como texto).",
        "UF ERROR": "UF inválida (não foi possível interpretar como texto).",
        "VALOR DO PLANO ERROR": "Valor do plano inválido (não foi possível converter para número).",
    }
    if m.startswith("DATA ERROR"):
        return "Data inválida (use DD/MM/AAAA ou AAAA-MM-DD)."
    return mapping.get(m, msg)


@dataclass(frozen=True)
class ErrorRecord:
    row_data: Dict[str, Any]
    erro_resumo: str
    erro_detalhe: Dict[str, Any]


class ErrorReport:
    def __init__(self, colunas_entrada: Iterable[str]):
        self._colunas_entrada = [str(c) for c in colunas_entrada]
        self._records: List[ErrorRecord] = []

    @property
    def has_errors(self) -> bool:
        return len(self._records) > 0

    def add(
        self,
        *,
        row_data: Dict[str, Any],
        etapa: str,
        motivo: str,
        exception: Optional[BaseException] = None,
        contexto: Optional[Dict[str, Any]] = None,
    ) -> None:
        motivo_h = humanizar_erro_validacao(motivo)

        detalhe: Dict[str, Any] = {
            "timestamp": _utc_iso(),
            "etapa": etapa,
            "motivo": motivo_h,
        }

        if contexto:
            detalhe["contexto"] = contexto

        if exception is not None:
            detalhe.update(
                {
                    "exception_type": type(exception).__name__,
                    "exception_message": _safe_str(exception),
                    "traceback": traceback.format_exc(),
                }
            )

        resumo = f"[{etapa}] {motivo_h}"
        self._records.append(
            ErrorRecord(row_data=dict(row_data), erro_resumo=resumo, erro_detalhe=detalhe)
        )

    def to_dataframe(self) -> pd.DataFrame:
        rows: List[Dict[str, Any]] = []
        for rec in self._records:
            row: Dict[str, Any] = {}
            for col in self._colunas_entrada:
                row[col] = rec.row_data.get(col, "")
            row["erro_resumo"] = rec.erro_resumo
            row["erro_detalhe_json"] = json.dumps(
                rec.erro_detalhe, ensure_ascii=False, sort_keys=True
            )
            rows.append(row)
        return pd.DataFrame(rows, columns=[*self._colunas_entrada, "erro_resumo", "erro_detalhe_json"])

    def export(self, output_path: str, *, formato: str) -> Path:
        out = Path(output_path).expanduser()
        out.parent.mkdir(parents=True, exist_ok=True)

        df = self.to_dataframe()
        fmt = (formato or "").strip().lower()
        if fmt in {"xlsx", "excel"}:
            if out.suffix.lower() != ".xlsx":
                out = out.with_suffix(".xlsx")
            df.to_excel(out, index=False)
            return out

        if fmt in {"csv"}:
            if out.suffix.lower() != ".csv":
                out = out.with_suffix(".csv")
            df.to_csv(out, index=False, encoding="utf-8-sig")
            return out

        raise ValueError("Formato inválido. Use 'xlsx' ou 'csv'.")


from __future__ import annotations

import json
import traceback
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import pandas as pd

from app.utils.credentials_store import base_dir_mesmo_do_executavel


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
        "CNPJ ERROR": "CNPJ inválido (deve ter 14 dígitos e dígitos verificadores válidos).",
        "SEXO ERROR": (
            "Sexo/tipo inválido (PF: FEMININO ou MASCULINO; PJ: PUBLICO ou PRIVADO)."
        ),
        "PJ PUBLICO - APENAS EMPRESAS COM TIPO PRIVADO SÃO PROCESSADAS": (
            "Empresa pública (PUBLICO) ignorada — o MA processa apenas contratantes PRIVADO."
        ),
        "PJ PUBLICO - APENAS EMPRESAS COM TIPO PRIVADO SAO PROCESSADAS": (
            "Empresa pública (PUBLICO) ignorada — o MA processa apenas contratantes PRIVADO."
        ),
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
                    "traceback": "".join(
                        traceback.format_exception(
                            type(exception), exception, exception.__traceback__
                        )
                    ),
                }
            )

        resumo = f"[{etapa}] {motivo_h}"
        self._records.append(
            ErrorRecord(
                row_data=dict(row_data), erro_resumo=resumo, erro_detalhe=detalhe
            )
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
        return pd.DataFrame(
            rows, columns=[*self._colunas_entrada, "erro_resumo", "erro_detalhe_json"]
        )

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


def caminho_relatorio_informado_na_ui(caminho: str) -> str:
    """
    Retorna o caminho apenas quando o usuário escolheu um destino real na UI.
    Ignora vazio, ~/, e sugestões antigas só com nome de arquivo (sem pasta),
    que acabam sendo resolvidas contra o cwd (~/ no macOS).
    """
    caminho = (caminho or "").strip()
    if not caminho or caminho in ("~", "~/", "~\\"):
        return ""
    p = Path(caminho).expanduser()
    try:
        if p.is_dir():
            return ""
    except OSError:
        pass
    if not p.is_absolute():
        return ""
    return caminho


def caminho_relatorio_padrao(fmt: str = "xlsx") -> str:
    """Caminho absoluto padrão ao lado do executável, em Erros ARTs/."""
    fmt = (fmt or "xlsx").strip().lower()
    ext = ".xlsx" if fmt in {"xlsx", "excel"} else ".csv"
    base_raiz = base_dir_mesmo_do_executavel()
    base = base_raiz / "Erros ARTs"
    try:
        base.mkdir(parents=True, exist_ok=True)
    except Exception:
        base = base_raiz
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return str(base / f"erros_cadastro_{ts}{ext}")


def resolver_caminho_relatorio(dados: Dict[str, Any]) -> Path:
    """
    Define o caminho do relatório (uma vez por execução) e reutiliza nas gravações
    incrementais. Usa caminho informado na UI; senão, gera na pasta do executável.
    """
    cached = (dados.get("_caminho_relatorio_efetivo") or "").strip()
    if cached:
        return Path(cached).expanduser()

    explicit = caminho_relatorio_informado_na_ui(
        dados.get("caminho_relatorio_erros") or ""
    )
    fmt = (dados.get("formato_relatorio_erros") or "xlsx").strip().lower()
    ext = ".xlsx" if fmt in {"xlsx", "excel"} else ".csv"

    if explicit:
        path = Path(explicit).expanduser()
        if path.suffix.lower() not in {".xlsx", ".csv"}:
            path = path.with_suffix(ext)
    else:
        base_raiz = base_dir_mesmo_do_executavel()
        base = base_raiz / "Erros ARTs"
        try:
            base.mkdir(parents=True, exist_ok=True)
        except Exception:
            # Se falhar criar a subpasta, tenta ao menos salvar ao lado do executável.
            base = base_raiz
            try:
                base.mkdir(parents=True, exist_ok=True)
            except Exception:
                # Não cair em cwd (Finder pode ser ~/); mantém a melhor opção disponível.
                base = base_raiz
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = base / f"erros_cadastro_{ts}{ext}"

    dados["_caminho_relatorio_efetivo"] = str(path)
    return path


def persistir_relatorio_erros(
    dados: Dict[str, Any], error_report: ErrorReport
) -> Optional[Path]:
    """
    Grava o relatório sempre que houver erros registrados (independente do checkbox).
    Pode ser chamado várias vezes na mesma execução (sobrescreve o mesmo arquivo).
    """
    if not error_report.has_errors:
        return None

    formato = dados.get("formato_relatorio_erros") or "xlsx"
    try:
        output_path = resolver_caminho_relatorio(dados)
        saved = error_report.export(str(output_path), formato=formato)
        print(f"\033[33mRelatório de erros salvo em: {saved}\033[0m")
        return saved
    except Exception as e:
        print(f"\033[31mFalha ao salvar relatório de erros: {e}\033[0m")
        try:
            base_raiz = base_dir_mesmo_do_executavel()
            base = base_raiz / "Erros ARTs"
            try:
                base.mkdir(parents=True, exist_ok=True)
            except Exception:
                base = base_raiz
            fallback = base / f"erros_cadastro_fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            saved = error_report.export(str(fallback), formato="csv")
            print(f"\033[33mRelatório de erros salvo (fallback) em: {saved}\033[0m")
            return saved
        except Exception as e2:
            print(f"\033[31mFalha ao salvar relatório de erros (fallback): {e2}\033[0m")
            return None


def registrar_erro_cliente(
    error_report: ErrorReport,
    cliente: Any,
    *,
    etapa: str,
    motivo: str,
    exception: Optional[BaseException] = None,
    contexto: Optional[Dict[str, Any]] = None,
    dados: Optional[Dict[str, Any]] = None,
    persistir: bool = True,
) -> None:
    """Registra erro do cliente, evita duplicata na mesma iteração e persiste o relatório."""
    if getattr(cliente, "_erro_registrado", False):
        if persistir and dados is not None:
            persistir_relatorio_erros(dados, error_report)
        return

    row_data = getattr(cliente, "_row_data", {})
    ctx = dict(contexto or {})
    ctx.setdefault("cliente_nome", getattr(cliente, "nome", ""))
    ctx.setdefault("cliente_index", getattr(cliente, "_row_index", None))

    error_report.add(
        row_data=row_data,
        etapa=etapa,
        motivo=motivo,
        exception=exception,
        contexto=ctx,
    )
    try:
        cliente._erro_registrado = True
    except Exception:
        pass

    if persistir and dados is not None:
        persistir_relatorio_erros(dados, error_report)


def _resolver_caminho_log(dados: Dict[str, Any]) -> Path:
    """
    Resolve o caminho do log texto (uma vez por execução), preferindo ficar ao lado
    do relatório de erros e reaproveitando o mesmo nome base.
    """
    cached = (dados.get("_caminho_log_erros_efetivo") or "").strip()
    if cached:
        return Path(cached).expanduser()

    base_rel = resolver_caminho_relatorio(dados)
    # ex.: erros_cadastro_20260602_084611.xlsx -> erros_cadastro_20260602_084611.log
    log_path = base_rel.with_suffix(".log")
    dados["_caminho_log_erros_efetivo"] = str(log_path)
    return log_path


def anexar_erro_em_log(
    dados: Dict[str, Any],
    *,
    etapa: str,
    motivo: str,
    exception: Optional[BaseException] = None,
    contexto: Optional[Dict[str, Any]] = None,
) -> Optional[Path]:
    """
    Anexa detalhes (incluindo traceback Python) em um arquivo .log separado.
    Retorna o Path do log salvo, ou None se falhar.
    """
    try:
        log_path = _resolver_caminho_log(dados)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        payload: Dict[str, Any] = {
            "timestamp": _utc_iso(),
            "etapa": etapa,
            "motivo": humanizar_erro_validacao(motivo),
        }
        if contexto:
            payload["contexto"] = dict(contexto)
        if exception is not None:
            payload.update(
                {
                    "exception_type": type(exception).__name__,
                    "exception_message": _safe_str(exception),
                    "traceback": "".join(
                        traceback.format_exception(
                            type(exception), exception, exception.__traceback__
                        )
                    ),
                }
            )

        with log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False, sort_keys=True))
            f.write("\n")

        return log_path
    except Exception:
        return None

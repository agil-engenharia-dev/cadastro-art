from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


def base_dir_mesmo_do_executavel() -> Path:
    """
    Em build (PyInstaller), salva ao lado do .exe/.app.
    Em desenvolvimento, usa o diretório atual (onde o usuário executou o script).
    """
    def _dir_de_um_executavel(path: Path) -> Path:
        """
        Dado um path para o executável, retorna o diretório onde os arquivos auxiliares
        devem ser gravados.
        - macOS .app: retorna o diretório pai do bundle (.app).
        - binário normal (.exe / unix): retorna o diretório pai do binário.
        """
        path = path.resolve()
        parts = [p.lower() for p in path.parts]
        app_idx = next((i for i, p in enumerate(parts) if p.endswith(".app")), None)
        if app_idx is not None:
            app_bundle = Path(*path.parts[: app_idx + 1])
            return app_bundle.parent
        return path.parent

    # PyInstaller: sys.executable é a fonte mais confiável do caminho do binário.
    # (Não depende do cwd, que pode cair em ~ quando aberto via Finder.)
    try:
        if getattr(sys, "frozen", False):
            exe = Path(sys.executable).resolve()
            return _dir_de_um_executavel(exe)
    except Exception:
        pass

    # Desenvolvimento / fallback
    return Path.cwd()


def _arquivo_credenciais() -> Path:
    return base_dir_mesmo_do_executavel() / "credenciais_login.json"


def _coerce_str(v: Any) -> str:
    try:
        return "" if v is None else str(v)
    except Exception:
        return ""


@dataclass
class Credenciais:
    login: str = ""
    senha: str = ""


class CredentialsStore:
    def __init__(self, path: Optional[Path] = None):
        self.path = path or _arquivo_credenciais()
        self._data: Dict[str, Any] = {
            "version": 1,
            "last": {"tipo": "", "login": "", "senha": ""},
            "por_tipo": {},
            "ui": {"last_dir_planilha": ""},
        }

    def load(self) -> None:
        try:
            if not self.path.exists():
                return
            raw = self.path.read_text(encoding="utf-8")
            parsed = json.loads(raw) if raw.strip() else {}
            if isinstance(parsed, dict):
                self._data.update(parsed)
        except Exception:
            # não quebra a UI por falha de leitura
            return

    def save(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(
                json.dumps(self._data, ensure_ascii=False, indent=2, sort_keys=True),
                encoding="utf-8",
            )
        except Exception:
            return

    def get_last(self) -> Credenciais:
        last = self._data.get("last") or {}
        return Credenciais(login=_coerce_str(last.get("login")), senha=_coerce_str(last.get("senha")))

    def get_last_tipo(self) -> str:
        last = self._data.get("last") or {}
        return _coerce_str(last.get("tipo")).strip().upper()

    def get_for_tipo(self, tipo: str) -> Credenciais:
        tipo = _coerce_str(tipo).strip().upper()
        por_tipo = self._data.get("por_tipo") or {}
        entry = por_tipo.get(tipo) or {}
        return Credenciais(login=_coerce_str(entry.get("login")), senha=_coerce_str(entry.get("senha")))

    def set_for_tipo(self, tipo: str, *, login: str, senha: str) -> None:
        tipo = _coerce_str(tipo).strip().upper()
        if not tipo:
            return
        por_tipo = self._data.setdefault("por_tipo", {})
        if not isinstance(por_tipo, dict):
            por_tipo = {}
            self._data["por_tipo"] = por_tipo
        por_tipo[tipo] = {"login": _coerce_str(login).strip(), "senha": _coerce_str(senha)}

    def set_last(self, tipo: str, *, login: str, senha: str) -> None:
        self._data["last"] = {
            "tipo": _coerce_str(tipo).strip().upper(),
            "login": _coerce_str(login).strip(),
            "senha": _coerce_str(senha),
        }

    def get_last_dir_planilha(self) -> str:
        ui = self._data.get("ui") or {}
        return _coerce_str(ui.get("last_dir_planilha")).strip()

    def set_last_dir_planilha(self, caminho: str) -> None:
        caminho = _coerce_str(caminho).strip()
        if not caminho:
            return
        diretorio = str(Path(caminho).parent)
        if not diretorio:
            return
        ui = self._data.setdefault("ui", {})
        if not isinstance(ui, dict):
            ui = {}
            self._data["ui"] = ui
        ui["last_dir_planilha"] = diretorio


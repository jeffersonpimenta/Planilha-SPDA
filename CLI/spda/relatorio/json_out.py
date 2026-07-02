"""Relatorio JSON: serializa o Resultado (consumivel por GUI/reimport)."""
from __future__ import annotations

from pathlib import Path

from spda.model.resultado import Resultado


def gerar_json(resultado: Resultado) -> str:
    return resultado.model_dump_json(indent=2)


def salvar_json(resultado: Resultado, caminho: str | Path) -> None:
    Path(caminho).write_text(gerar_json(resultado), encoding="utf-8")

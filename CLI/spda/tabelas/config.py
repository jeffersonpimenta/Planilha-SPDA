"""Carrega as tabelas de referencia com override opcional por arquivo.

O override e raso por chave de topo: o dict do arquivo substitui/atualiza o
default correspondente. Suporta JSON e TOML (pela extensao).
"""
from __future__ import annotations

import json
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from spda.tabelas import referencia as ref


@dataclass
class Tabelas:
    C_D: dict = field(default_factory=lambda: dict(ref.C_D))
    C_I: dict = field(default_factory=lambda: dict(ref.C_I))
    C_T: dict = field(default_factory=lambda: dict(ref.C_T))
    C_E: dict = field(default_factory=lambda: dict(ref.C_E))
    P_TA: dict = field(default_factory=lambda: dict(ref.P_TA))
    P_B: dict = field(default_factory=lambda: dict(ref.P_B))
    P_SPD: dict = field(default_factory=lambda: dict(ref.P_SPD))
    P_EB: dict = field(default_factory=lambda: dict(ref.P_EB))
    P_TU: dict = field(default_factory=lambda: dict(ref.P_TU))
    C_LD: dict = field(default_factory=lambda: dict(ref.C_LD))
    C_LI: dict = field(default_factory=lambda: dict(ref.C_LI))
    R_T: dict = field(default_factory=lambda: dict(ref.R_T))
    R_P: dict = field(default_factory=lambda: dict(ref.R_P))
    R_F: dict = field(default_factory=lambda: dict(ref.R_F))
    R_F_EXPLOSAO: dict = field(default_factory=lambda: dict(ref.R_F_EXPLOSAO))
    R_S: dict = field(default_factory=lambda: dict(ref.R_S))
    L_F: dict = field(default_factory=lambda: dict(ref.L_F))
    RT: dict = field(default_factory=lambda: dict(ref.RT))
    # F_T por criticidade (7.3.4): {"critico": 0.1, "nao_critico": 1.0}.
    FT: dict = field(default_factory=lambda: dict(ref.FT))


def _ler(caminho: Path) -> dict[str, Any]:
    if caminho.suffix == ".toml":
        return tomllib.loads(caminho.read_text(encoding="utf-8"))
    return json.loads(caminho.read_text(encoding="utf-8"))


def carregar_tabelas(caminho: str | Path | None) -> Tabelas:
    t = Tabelas()
    if caminho is None:
        return t
    dados = _ler(Path(caminho))
    for chave, valor in dados.items():
        atual = getattr(t, chave, None)
        if isinstance(atual, dict) and isinstance(valor, dict):
            atual.update(valor)
        else:
            setattr(t, chave, valor)
    return t

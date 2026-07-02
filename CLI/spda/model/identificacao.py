# spda/model/identificacao.py
"""Bloco de identificacao assinavel do laudo (cabecalho ART). Modelo puro.

Todos os campos sao opcionais para o relatorio rodar mesmo incompleto; o motor de
notas (Plano 3) avisa o que falta antes de assinar. Registro profissional: CREA.
"""
from __future__ import annotations

from pydantic import BaseModel


class Identificacao(BaseModel):
    titulo: str | None = None
    cliente: str | None = None
    endereco: str | None = None
    responsavel: str | None = None
    art: str | None = None               # numero da ART
    registro: str | None = None          # CREA + UF
    norma: str = "ABNT NBR 5419-2"
    revisao: str = "2026"
    data: str | None = None
    observacoes: str | None = None

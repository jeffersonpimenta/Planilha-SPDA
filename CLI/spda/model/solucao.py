# spda/model/solucao.py
"""Solucao adotada (overlay do Estudo de Solucoes): delta de medidas por
estrutura, persistido no proprio JSON do Projeto.

Guarda apenas o degrau ADOTADO alem do instalado, serializado por
Medida.degrau_str (value do enum, "nenhum" para None, "0.2" para floats).
A semantica dos ids/degraus vive em spda/solucao/catalogo.py.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class SolucaoEstrutura(BaseModel):
    # medida_id (catalogo.MEDIDAS) -> degrau adotado serializado
    medidas: dict[str, str] = Field(default_factory=dict)


class Solucao(BaseModel):
    # chave = Estrutura.nome (primeira ocorrencia, se nomes repetirem)
    estruturas: dict[str, SolucaoEstrutura] = Field(default_factory=dict)

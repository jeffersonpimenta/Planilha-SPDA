"""FakePrompter: devolve respostas roteirizadas, em ordem de chamada.

Cada metodo consome o proximo valor da fila `respostas`. Use para testar
wizards e menu sem terminal interativo.
"""
from __future__ import annotations

from typing import Any


class FakePrompter:
    def __init__(self, respostas: list[Any]):
        self._fila = list(respostas)

    def _prox(self):
        if not self._fila:
            raise AssertionError(
                "FakePrompter: fila de respostas esgotada — o roteiro tem menos "
                "respostas do que perguntas feitas pelo wizard."
            )
        return self._fila.pop(0)

    def texto(self, msg: str, default: str | None = None) -> str:
        return self._prox()

    def numero(self, msg: str, default: float | None = None,
               minimo: float | None = None, maximo: float | None = None,
               tabela: str | None = None) -> float:
        return self._prox()

    def numero_tabelado(self, msg: str, opcoes: list[float],
                        default: float | None = None,
                        tabela: str | None = None) -> float:
        return self._prox()

    def inteiro(self, msg: str, default: int | None = None,
                minimo: int | None = None) -> int:
        return self._prox()

    def confirmar(self, msg: str, default: bool = False,
                  tabela: str | None = None) -> bool:
        return self._prox()

    def opcao(self, msg: str, opcoes, default=None, tabela: str | None = None):
        return self._prox()

    def opcao_opcional(self, msg: str, opcoes, default=None,
                       tabela: str | None = None):
        return self._prox()

    def selecionar(self, msg: str, opcoes: list[str], default: str | None = None) -> str:
        return self._prox()

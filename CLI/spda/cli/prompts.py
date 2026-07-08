"""Abstracao de perguntas. QuestionaryPrompter fala com o terminal; qualquer
outro frontend (GUI, testes) implementa o mesmo Protocol Prompter.

So este modulo (e nada do nucleo) conhece questionary.
"""
from __future__ import annotations

from enum import Enum
from typing import Protocol, runtime_checkable


@runtime_checkable
class Prompter(Protocol):
    def texto(self, msg: str, default: str | None = None) -> str: ...
    def numero(self, msg: str, default: float | None = None,
               minimo: float | None = None, maximo: float | None = None,
               tabela: str | None = None) -> float: ...
    def numero_tabelado(self, msg: str, opcoes: list[float],
                        default: float | None = None,
                        tabela: str | None = None) -> float: ...
    def inteiro(self, msg: str, default: int | None = None,
                minimo: int | None = None) -> int: ...
    def confirmar(self, msg: str, default: bool = False,
                  tabela: str | None = None) -> bool: ...
    def opcao(self, msg: str, opcoes: type[Enum], default=None,
              tabela: str | None = None): ...
    def opcao_opcional(self, msg: str, opcoes: type[Enum], default=None,
                       tabela: str | None = None): ...
    def selecionar(self, msg: str, opcoes: list[str],
                   default: str | None = None) -> str: ...


def _abortar_se_none(valor):
    # questionary devolve None em Ctrl-C/EOF; tratamos como cancelamento.
    if valor is None:
        raise KeyboardInterrupt("entrada cancelada")
    return valor


# Sentinela para a opcao "(nenhum)": distingue a escolha legitima de "sem valor"
# do None que questionary devolve em Ctrl-C/EOF (que e cancelamento).
_NENHUM = object()


class QuestionaryPrompter:
    """Implementacao concreta com questionary."""

    def texto(self, msg: str, default: str | None = None) -> str:
        import questionary
        return _abortar_se_none(
            questionary.text(msg, default=default or "").ask()
        )

    def numero(self, msg: str, default: float | None = None,
               minimo: float | None = None, maximo: float | None = None,
               tabela: str | None = None) -> float:
        import questionary
        from spda.tabelas.fontes import anexar_ref
        msg = anexar_ref(msg, tabela)
        while True:
            bruto = _abortar_se_none(
                questionary.text(
                    msg, default="" if default is None else str(default)
                ).ask()
            )
            try:
                v = float(bruto.replace(",", "."))
            except ValueError:
                print("  Valor inválido; digite um número.")
                continue
            if minimo is not None and v < minimo:
                print(f"  Deve ser >= {minimo}.")
                continue
            if maximo is not None and v > maximo:
                print(f"  Deve ser <= {maximo}.")
                continue
            return v

    def numero_tabelado(self, msg: str, opcoes: list[float],
                        default: float | None = None,
                        tabela: str | None = None) -> float:
        # Escolha travada num conjunto de valores tabelados (ex.: colunas de
        # U_W da Tabela B.9). questionary.select impede valor fora da lista.
        import questionary
        from spda.tabelas.fontes import anexar_ref
        escolhas = [questionary.Choice(title=f"{v:g}", value=v) for v in opcoes]
        return _abortar_se_none(
            questionary.select(anexar_ref(msg, tabela), choices=escolhas,
                               default=default).ask()
        )

    def inteiro(self, msg: str, default: int | None = None,
                minimo: int | None = None) -> int:
        v = self.numero(msg, default=default, minimo=minimo)
        return int(v)

    def confirmar(self, msg: str, default: bool = False,
                  tabela: str | None = None) -> bool:
        import questionary
        from spda.tabelas.fontes import anexar_ref
        return _abortar_se_none(
            questionary.confirm(anexar_ref(msg, tabela), default=default).ask())

    def opcao(self, msg: str, opcoes: type[Enum], default=None,
              tabela: str | None = None):
        import questionary
        from spda.model.enums import rotulo
        from spda.tabelas.fontes import anexar_ref, fonte_de
        escolhas = [questionary.Choice(title=rotulo(e), value=e) for e in opcoes]
        msg = anexar_ref(msg, tabela or fonte_de(opcoes))
        return _abortar_se_none(
            questionary.select(msg, choices=escolhas, default=default).ask()
        )

    def opcao_opcional(self, msg: str, opcoes: type[Enum], default=None,
                       tabela: str | None = None):
        import questionary
        from spda.model.enums import rotulo
        from spda.tabelas.fontes import anexar_ref, fonte_de
        escolhas = [questionary.Choice(title="(nenhum)", value=_NENHUM)]
        escolhas += [questionary.Choice(title=rotulo(e), value=e) for e in opcoes]
        msg = anexar_ref(msg, tabela or fonte_de(opcoes))
        escolhido = questionary.select(msg, choices=escolhas,
                                       default=default).ask()
        if escolhido is None:  # Ctrl-C/EOF
            raise KeyboardInterrupt("entrada cancelada")
        return None if escolhido is _NENHUM else escolhido

    def selecionar(self, msg: str, opcoes: list[str],
                   default: str | None = None) -> str:
        import questionary
        return _abortar_se_none(
            questionary.select(msg, choices=opcoes, default=default).ask()
        )

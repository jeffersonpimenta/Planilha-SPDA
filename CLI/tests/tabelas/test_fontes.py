# -*- coding: utf-8 -*-
"""Cobre o registro de fontes (tabela de origem das perguntas)."""
from spda.model.enums import (
    Localizacao, NivelDPS, ProtecaoToquePasso, RelevanciaAD,
)
from spda.tabelas.fontes import FONTE_POR_ENUM, anexar_ref, fonte_de


def test_fonte_de_enum_conhecido():
    assert fonte_de(Localizacao) == "Tabela A.1 - Fator de localização C_D"


def test_fonte_de_enum_sem_tabela():
    # RelevanciaAD e selecao de parte da estrutura, sem tabela de origem.
    assert fonte_de(RelevanciaAD) is None


def test_enums_ambiguos_ficam_fora():
    # Esses mapeiam a tabelas diferentes por contexto; o call site passa tabela=.
    assert ProtecaoToquePasso not in FONTE_POR_ENUM
    assert NivelDPS not in FONTE_POR_ENUM


def test_todas_as_fontes_tem_acento_ou_texto():
    # Toda referencia comeca com "Tabela" e tem titulo apos o hifen.
    for ref in FONTE_POR_ENUM.values():
        assert ref.startswith("Tabela ")
        assert " - " in ref


def test_anexar_ref_com_e_sem():
    assert anexar_ref("Localizacao (C_D)", "Tabela A.1 - X") == \
        "Localizacao (C_D)  [Tabela A.1 - X]"
    assert anexar_ref("Comprimento L (m)", None) == "Comprimento L (m)"

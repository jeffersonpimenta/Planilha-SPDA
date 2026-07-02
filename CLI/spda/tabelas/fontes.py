# -*- coding: utf-8 -*-
"""Fontes (tabela de origem) dos parametros das perguntas da CLI.

Cada Enum qualitativo usado numa pergunta vem de uma tabela da NBR 5419-2:2026.
Aqui consolidamos essa correspondencia (antes so em comentarios de codigo) numa
string de referencia pronta para exibir junto da pergunta -- ex.:

    Localizacao (C_D)  [Tabela A.1 - Fator de localizacao C_D]

So enums *nao ambiguos* entram em FONTE_POR_ENUM. Dois enums mapeiam a tabelas
diferentes conforme o contexto (ProtecaoToquePasso -> B.1 ou B.6; NivelDPS ->
B.3 ou B.7); esses ficam de fora e o call site em wizards.py passa `tabela=`
explicito. Os titulos (com acentuacao correta) vem dos cabecalhos de tabelas.md.
"""
from __future__ import annotations

from enum import Enum

from spda.model.enums import (
    AmbienteLinha, CategoriaLinha, ClasseBlindagemRS, FiacaoInterna,
    InstalacaoLinha, Localizacao, NivelProtecao, PerigoEspecial,
    ProvidenciaIncendio, RiscoIncendio, TipoConstrucao, TipoLinha,
    TipoLinhaExterna, TipoOcupacao, TipoSuperficie, ZonaExplosao,
)

# Enum -> referencia renderizada (id + titulo). So enums de tabela unica.
FONTE_POR_ENUM: dict[type[Enum], str] = {
    Localizacao: "Tabela A.1 - Fator de localização C_D",
    InstalacaoLinha: "Tabela A.2 - Fator de instalação C_I",
    TipoLinha: "Tabela A.3 - Fator tipo de linha C_T",
    AmbienteLinha: "Tabela A.4 - Fator ambiental C_E",
    NivelProtecao: "Tabela B.2 - Probabilidade P_B",
    TipoLinhaExterna: "Tabela B.4 - Fatores C_LD e C_LI",
    FiacaoInterna: "Tabela B.5 - Fator K_S3",
    ClasseBlindagemRS: "Tabela B.8 - Probabilidade P_LD",
    CategoriaLinha: "Tabela B.9 - Probabilidade P_LI",
    TipoOcupacao: "Tabela C.2 - Perda L_F por ocupação",
    TipoSuperficie: "Tabela C.3 - Fator r_t",
    ProvidenciaIncendio: "Tabela C.4 - Fator r_p",
    RiscoIncendio: "Tabela C.5 - Fator r_f (incêndio)",
    ZonaExplosao: "Tabela C.5 - Fator r_f (explosão)",
    PerigoEspecial: "Tabela C.6 - Fator h_z",
    TipoConstrucao: "Tabela C.7 - Fator r_s",
    # RelevanciaAD: sem tabela (selecao de parte da estrutura) -> omitido.
}


def fonte_de(opcoes: type[Enum]) -> str | None:
    """Referencia da tabela de origem de um Enum de pergunta (None se nao houver)."""
    return FONTE_POR_ENUM.get(opcoes)


def anexar_ref(msg: str, ref: str | None) -> str:
    """Anexa a referencia entre colchetes ao texto da pergunta (no-op se None)."""
    return f"{msg}  [{ref}]" if ref else msg

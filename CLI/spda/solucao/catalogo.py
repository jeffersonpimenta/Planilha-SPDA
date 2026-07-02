"""Catalogo de medidas de protecao (Secao 11.3) modeladas como escadas discretas.

Cada Medida sabe: ler o degrau atual de uma Estrutura, aplicar o proximo degrau
(devolvendo uma COPIA modificada) e quais componentes R_x se beneficiam. Sao os
overrides discretos que o model suporta diretamente; medidas continuas (P_EB,
K_S1..K_S4, C_LD/C_LI) ficam reservadas para refino futuro.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from spda.model.enums import (
    NivelDPS, NivelProtecao, ProtecaoToquePasso, ProvidenciaIncendio,
    rotulo,
)
from spda.model.projeto import Estrutura

# Tipo de retorno: (estrutura_modificada, rotulo_de, rotulo_para) ou None no topo.
_Resultado = tuple[Estrutura, str, str] | None


@dataclass(frozen=True)
class Medida:
    id: str
    descricao: str
    parametro: str
    componentes: tuple[str, ...]
    _atual: Callable[[Estrutura], str]
    _aplicar: Callable[[Estrutura], _Resultado]

    def nivel_atual(self, est: Estrutura) -> str:
        return self._atual(est)

    def aplicar_proximo(self, est: Estrutura) -> _Resultado:
        """Devolve (copia com proximo degrau, de, para) ou None se ja no topo."""
        return self._aplicar(est)


def _rotulo(valor) -> str:
    """Rotulo legivel de um enum/None (proximo aos termos da norma)."""
    return rotulo(valor)


def _indice(valor, escada: list) -> int | None:
    """Degrau do valor na escada, ou None se o valor esta fora da escada.

    Valores fora da escada (ex.: NivelProtecao.I_descida_natural,
    ProtecaoToquePasso.malha_equipotencial) sao medidas que esta escada
    discreta nao controla -> tratadas como "nao avancavel" (aplicar -> None).

    NivelProtecao.nenhum e tratado como sinonimo de None (degrau base "sem
    SPDA"): ambos tem P_B = 1.0, logo a medida SPDA deve ser proposta tambem
    para uma estrutura explicitamente marcada como 'nenhum'.
    """
    if valor == NivelProtecao.nenhum and None in escada:
        valor = None
    return escada.index(valor) if valor in escada else None


def _idx_zonas(est: Estrutura, campo: str, escada: list) -> int | None:
    """Menor degrau entre as zonas (mais conservador), ou None se alguma zona
    tem valor fora da escada (nesse caso nao sobrescrevemos cegamente)."""
    idxs = [_indice(getattr(z.medidas, campo), escada) for z in est.zonas]
    if not idxs or any(i is None for i in idxs):
        return None
    return min(idxs)


def _atual_estrutura(campo: str, escada: list) -> Callable[[Estrutura], str]:
    def atual(est: Estrutura) -> str:
        valor = getattr(est, campo)
        i = _indice(valor, escada)
        return _rotulo(escada[i]) if i is not None else _rotulo(valor)
    return atual


def _atual_zonas(campo: str, escada: list) -> Callable[[Estrutura], str]:
    def atual(est: Estrutura) -> str:
        i = _idx_zonas(est, campo, escada)
        if i is not None:
            return _rotulo(escada[i])
        # fora da escada (ou sem zonas): mostra o valor real da primeira zona
        if est.zonas:
            return _rotulo(getattr(est.zonas[0].medidas, campo))
        return _rotulo(escada[0])
    return atual


def _atual_sistemas(escada: list) -> Callable[[Estrutura], str]:
    """Nivel atual de DPS: minimo entre todos os sistemas internos de todas as zonas."""
    def atual(est: Estrutura) -> str:
        sistemas = [s for z in est.zonas for s in z.sistemas_internos]
        if not sistemas:
            return _rotulo(None)
        idxs = [_indice(s.dps, escada) for s in sistemas]
        if any(i is None for i in idxs):
            return _rotulo(sistemas[0].dps)
        return _rotulo(escada[min(idxs)])
    return atual


def _aplicar_sistemas(escada: list) -> Callable[[Estrutura], _Resultado]:
    """Avanca DPS em todos os sistemas internos de todas as zonas (minimo sobe 1)."""
    def aplicar(est: Estrutura) -> _Resultado:
        sistemas = [s for z in est.zonas for s in z.sistemas_internos]
        if not sistemas:
            return None
        idxs = [_indice(s.dps, escada) for s in sistemas]
        if any(i is None for i in idxs):
            return None
        i = min(idxs)
        if i + 1 >= len(escada):
            return None
        prox = escada[i + 1]
        copia = est.model_copy(deep=True)
        for z in copia.zonas:
            for s in z.sistemas_internos:
                s.dps = prox
        return copia, _rotulo(escada[i]), _rotulo(prox)
    return aplicar


def _aplicar_estrutura(campo: str, escada: list) -> Callable[[Estrutura], _Resultado]:
    def aplicar(est: Estrutura) -> _Resultado:
        i = _indice(getattr(est, campo), escada)
        if i is None or i + 1 >= len(escada):
            return None
        prox = escada[i + 1]
        copia = est.model_copy(deep=True)
        setattr(copia, campo, prox)
        return copia, _rotulo(escada[i]), _rotulo(prox)
    return aplicar


def _aplicar_zonas(campo: str, escada: list) -> Callable[[Estrutura], _Resultado]:
    def aplicar(est: Estrutura) -> _Resultado:
        if not est.zonas:
            return None
        i = _idx_zonas(est, campo, escada)
        if i is None or i + 1 >= len(escada):
            return None
        prox = escada[i + 1]
        copia = est.model_copy(deep=True)
        for z in copia.zonas:
            setattr(z.medidas, campo, prox)
        return copia, _rotulo(escada[i]), _rotulo(prox)
    return aplicar


_ESC_SPDA = [None, NivelProtecao.IV, NivelProtecao.III, NivelProtecao.II,
             NivelProtecao.I]
_ESC_DPS = [None, NivelDPS.IV, NivelDPS.III, NivelDPS.II, NivelDPS.I,
            NivelDPS.melhor_I]
# Apenas os tres degraus discretos controlados aqui; malha_equipotencial /
# descida_natural / restricoes_fisicas sao medidas fora desta escada (ver _indice).
_ESC_TP = [ProtecaoToquePasso.nenhuma, ProtecaoToquePasso.avisos,
           ProtecaoToquePasso.isolacao]
_ESC_INC = [ProvidenciaIncendio.nenhuma, ProvidenciaIncendio.extintor,
            ProvidenciaIncendio.fixo_automatico]


MEDIDAS: list[Medida] = [
    Medida(
        id="spda", descricao="SPDA (nivel de protecao I-IV)", parametro="P_B",
        componentes=("R_B", "R_V"),
        _atual=_atual_estrutura("nivel_spda", _ESC_SPDA),
        _aplicar=_aplicar_estrutura("nivel_spda", _ESC_SPDA),
    ),
    Medida(
        id="toque_passo",
        descricao="Protecao contra tensao de toque e passo", parametro="P_TA",
        componentes=("R_A", "R_U"),
        _atual=_atual_zonas("protecao_toque_passo", _ESC_TP),
        _aplicar=_aplicar_zonas("protecao_toque_passo", _ESC_TP),
    ),
    Medida(
        id="dps", descricao="Sistema coordenado de DPS", parametro="P_SPD",
        componentes=("R_C", "R_W", "R_Z"),
        _atual=_atual_sistemas(_ESC_DPS),
        _aplicar=_aplicar_sistemas(_ESC_DPS),
    ),
    Medida(
        id="incendio", descricao="Sistema de combate a incendio", parametro="r_p",
        componentes=("R_B", "R_V"),
        _atual=_atual_estrutura("providencias_incendio", _ESC_INC),
        _aplicar=_aplicar_estrutura("providencias_incendio", _ESC_INC),
    ),
]

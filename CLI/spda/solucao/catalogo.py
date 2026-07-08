"""Catalogo de medidas de protecao (Secao 11.3) modeladas como escadas discretas.

Cada Medida sabe: ler o degrau atual de uma Estrutura (indice na escada, ou
None se o valor real esta fora da escada / nao ha elemento aplicavel), definir
um degrau arbitrario (devolvendo uma COPIA modificada) e quais componentes R_x
se beneficiam. Valores fora da escada (ex.: malha_equipotencial, fibra optica,
K_S3 custom) tornam a medida "nao avancavel" naquela estrutura.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isclose
from typing import Callable

from spda.model.enums import (
    ClasseBlindagemRS, NivelDPS, NivelProtecao, ProtecaoToquePasso,
    ProvidenciaIncendio, TipoLinhaExterna, rotulo,
)
from spda.model.projeto import Estrutura

# Tipo de retorno de aplicar_proximo: (copia, rotulo_de, rotulo_para) ou None.
_Resultado = tuple[Estrutura, str, str] | None


@dataclass(frozen=True)
class Medida:
    id: str
    descricao: str
    parametro: str
    componentes: tuple[str, ...]
    escada: tuple                                # degraus, do mais fraco ao mais forte
    _indice: Callable[[Estrutura], int | None]   # None = fora da escada / nao aplicavel
    _definir: Callable[[Estrutura, int], Estrutura]
    _bruto: Callable[[Estrutura], str]           # rotulo do valor real (fallback)
    rotulos: tuple[str, ...] | None = None       # rotulos por degrau (floats etc.)

    def __post_init__(self):
        # Invariante: rotulos explicitos cobrem a escada inteira.
        assert self.rotulos is None or len(self.rotulos) == len(self.escada), (
            f"Medida '{self.id}': rotulos ({len(self.rotulos)}) "
            f"!= escada ({len(self.escada)})")

    def indice_atual(self, est: Estrutura) -> int | None:
        return self._indice(est)

    def nivel_atual(self, est: Estrutura) -> str:
        i = self._indice(est)
        return self.rotulo_degrau(i) if i is not None else self._bruto(est)

    def rotulo_degrau(self, i: int) -> str:
        if self.rotulos is not None:
            return self.rotulos[i]
        return rotulo(self.escada[i])

    def rotulos_escada(self) -> list[str]:
        return [self.rotulo_degrau(i) for i in range(len(self.escada))]

    def definir_nivel(self, est: Estrutura, i: int) -> Estrutura:
        """Copia de `est` com o degrau `i` aplicado uniformemente."""
        return self._definir(est, i)

    def aplicar_proximo(self, est: Estrutura) -> _Resultado:
        i = self._indice(est)
        if i is None or i + 1 >= len(self.escada):
            return None
        prox = self.definir_nivel(est, i + 1)
        return prox, self.rotulo_degrau(i), self.rotulo_degrau(i + 1)

    # --- serializacao do degrau (Solucao.medidas) ---

    def degrau_str(self, i: int) -> str:
        v = self.escada[i]
        if v is None:
            return "nenhum"
        if isinstance(v, Enum):
            return v.value
        if isinstance(v, float):
            return format(v, "g")
        return str(v)

    def indice_de_degrau_str(self, s: str) -> int | None:
        for i in range(len(self.escada)):
            if self.degrau_str(i) == s:
                return i
        return None


def _indice_valor(valor, escada) -> int | None:
    """Degrau do valor na escada, ou None se fora dela.

    NivelProtecao.nenhum e sinonimo de None (degrau base "sem SPDA"): ambos
    tem P_B = 1.0, logo a medida SPDA vale tambem para estrutura marcada
    explicitamente como 'nenhum'.
    """
    if valor == NivelProtecao.nenhum and None in escada:
        valor = None
    return escada.index(valor) if valor in escada else None


# --- campo direto da Estrutura (nivel_spda, providencias_incendio) ---

def _ind_estrutura(campo: str, escada: tuple):
    def f(est: Estrutura) -> int | None:
        return _indice_valor(getattr(est, campo), escada)
    return f


def _def_estrutura(campo: str, escada: tuple):
    def f(est: Estrutura, i: int) -> Estrutura:
        copia = est.model_copy(deep=True)
        setattr(copia, campo, escada[i])
        return copia
    return f


def _bruto_estrutura(campo: str):
    def f(est: Estrutura) -> str:
        return rotulo(getattr(est, campo))
    return f


# --- campo em Zona.medidas (protecao_toque_passo) ---

def _ind_zonas(campo: str, escada: tuple):
    def f(est: Estrutura) -> int | None:
        idxs = [_indice_valor(getattr(z.medidas, campo), escada) for z in est.zonas]
        if not idxs or any(i is None for i in idxs):
            return None
        return min(idxs)  # mais conservador
    return f


def _def_zonas(campo: str, escada: tuple):
    def f(est: Estrutura, i: int) -> Estrutura:
        copia = est.model_copy(deep=True)
        for z in copia.zonas:
            setattr(z.medidas, campo, escada[i])
        return copia
    return f


def _bruto_zonas(campo: str, escada: tuple):
    def f(est: Estrutura) -> str:
        if est.zonas:
            return rotulo(getattr(est.zonas[0].medidas, campo))
        return rotulo(escada[0])
    return f


# --- SistemaInterno.dps (todas as zonas) ---

def _sistemas(est: Estrutura):
    return [s for z in est.zonas for s in z.sistemas_internos]


def _ind_sistemas_dps(escada: tuple):
    def f(est: Estrutura) -> int | None:
        sistemas = _sistemas(est)
        if not sistemas:
            return None
        idxs = [_indice_valor(s.dps, escada) for s in sistemas]
        if any(i is None for i in idxs):
            return None
        return min(idxs)
    return f


def _def_sistemas_dps(escada: tuple):
    def f(est: Estrutura, i: int) -> Estrutura:
        copia = est.model_copy(deep=True)
        for z in copia.zonas:
            for s in z.sistemas_internos:
                s.dps = escada[i]
        return copia
    return f


def _bruto_sistemas_dps():
    def f(est: Estrutura) -> str:
        sistemas = _sistemas(est)
        return rotulo(sistemas[0].dps) if sistemas else rotulo(None)
    return f


# --- campo em Linha (nivel_eb, protecao_toque_entrada) ---

def _ind_linhas(campo: str, escada: tuple):
    def f(est: Estrutura) -> int | None:
        if not est.linhas:
            return None
        idxs = [_indice_valor(getattr(li, campo), escada) for li in est.linhas]
        if any(i is None for i in idxs):
            return None
        return min(idxs)
    return f


def _def_linhas(campo: str, escada: tuple):
    def f(est: Estrutura, i: int) -> Estrutura:
        copia = est.model_copy(deep=True)
        for li in copia.linhas:
            setattr(li, campo, escada[i])
        return copia
    return f


def _bruto_linhas(campo: str, escada: tuple):
    def f(est: Estrutura) -> str:
        if est.linhas:
            return rotulo(getattr(est.linhas[0], campo))
        return rotulo(escada[0])
    return f


# --- blindagem de linha: par (tipo_externa, classe_blindagem) ---
# Linhas ja "melhores" que a escada (C_LD = 0) nunca sao tocadas.
_TIPOS_LINHA_MELHORES = {
    TipoLinhaExterna.eletroduto_metalico,
    TipoLinhaExterna.fibra_optica,
    TipoLinhaExterna.interface_isolante,
}
_ESC_BLIND = (ClasseBlindagemRS.nao_blindada, ClasseBlindagemRS.rs_5_20,
              ClasseBlindagemRS.rs_1_5, ClasseBlindagemRS.rs_ate_1)
_ROT_BLIND = (
    "Não blindada",
    "Blindada interligada, 5 < RS <= 20 ohm/km",
    "Blindada interligada, 1 < RS <= 5 ohm/km",
    "Blindada interligada, RS <= 1 ohm/km",
)


def _linhas_blindaveis(est: Estrutura):
    return [li for li in est.linhas if li.tipo_externa not in _TIPOS_LINHA_MELHORES]


def _ind_blindagem(est: Estrutura) -> int | None:
    linhas = _linhas_blindaveis(est)
    if not linhas:
        return None
    idxs = []
    for li in linhas:
        if li.classe_blindagem == ClasseBlindagemRS.nao_blindada:
            idxs.append(0)
        elif (li.tipo_externa == TipoLinhaExterna.blindada_interligada
              and li.classe_blindagem in _ESC_BLIND):
            idxs.append(_ESC_BLIND.index(li.classe_blindagem))
        else:
            return None  # blindada mas nao interligada etc. -> fora da escada
    return min(idxs)


def _def_blindagem(est: Estrutura, i: int) -> Estrutura:
    copia = est.model_copy(deep=True)
    for li in copia.linhas:
        if li.tipo_externa in _TIPOS_LINHA_MELHORES:
            continue
        if i == 0:
            # Degrau base coerente: sem credito de blindagem NEM de C_LI.
            # (blindada_interligada + nao_blindada seria estado fisicamente
            # inconsistente: C_LI=0 sem blindagem real.)
            li.tipo_externa = TipoLinhaExterna.aerea_nao_blindada
            li.classe_blindagem = ClasseBlindagemRS.nao_blindada
        else:
            li.tipo_externa = TipoLinhaExterna.blindada_interligada
            li.classe_blindagem = _ESC_BLIND[i]
    return copia


def _bruto_blindagem(est: Estrutura) -> str:
    if est.linhas:
        return rotulo(est.linhas[0].classe_blindagem)
    return rotulo(_ESC_BLIND[0])


# --- atributo float de SistemaInterno (K_S3, K_S2) ---

def _ind_sistemas_float(attr: str, escada: tuple):
    def f(est: Estrutura) -> int | None:
        sistemas = _sistemas(est)
        if not sistemas:
            return None
        idxs = []
        for s in sistemas:
            v = getattr(s, attr)
            j = next((k for k, dv in enumerate(escada)
                      if isclose(v, dv, rel_tol=1e-9)), None)
            if j is None:
                return None  # valor custom -> nao sobrescrevemos cegamente
            idxs.append(j)
        return min(idxs)
    return f


def _def_sistemas_float(attr: str, escada: tuple):
    def f(est: Estrutura, i: int) -> Estrutura:
        copia = est.model_copy(deep=True)
        for z in copia.zonas:
            for s in z.sistemas_internos:
                setattr(s, attr, escada[i])
        return copia
    return f


def _bruto_sistemas_float(attr: str):
    def f(est: Estrutura) -> str:
        sistemas = _sistemas(est)
        return f"{getattr(sistemas[0], attr):g}" if sistemas else "--"
    return f


_ESC_SPDA = (None, NivelProtecao.IV, NivelProtecao.III, NivelProtecao.II,
             NivelProtecao.I)
_ESC_DPS = (None, NivelDPS.IV, NivelDPS.III, NivelDPS.II, NivelDPS.I,
            NivelDPS.melhor_I)
# Apenas os tres degraus discretos controlados aqui; malha_equipotencial /
# descida_natural / restricoes_fisicas ficam fora da escada (nao avancavel).
_ESC_TP = (ProtecaoToquePasso.nenhuma, ProtecaoToquePasso.avisos,
           ProtecaoToquePasso.isolacao)
_ESC_INC = (ProvidenciaIncendio.nenhuma, ProvidenciaIncendio.extintor,
            ProvidenciaIncendio.fixo_automatico)
_ESC_EB = (None, NivelDPS.IV, NivelDPS.III, NivelDPS.II, NivelDPS.I,
           NivelDPS.melhor_I)

# Tabela B.5 (K_S3) e blindagem espacial em malha (K_S2 = 0,12 * w_m).
_ESC_KS3 = (1.0, 0.5, 0.2, 0.01, 0.0001)
_ROT_KS3 = (
    "Cabo não blindado, sem cuidado no roteamento (laço ~50 m2)",
    "Cabo não blindado, evitando grandes laços (~25 m2)",
    "Cabo não blindado, evitando laços médios (~10 m2)",
    "Cabo não blindado, evitando pequenos laços (~0,5 m2)",
    "Cabo blindado ou em conduto metálico",
)
_ESC_KS2 = (1.0, 0.24, 0.12, 0.06, 0.012)
_ROT_KS2 = (
    "Sem blindagem espacial (K_S2 = 1)",
    "Malha de blindagem 2 m (K_S2 = 0,24)",
    "Malha de blindagem 1 m (K_S2 = 0,12)",
    "Malha de blindagem 0,5 m (K_S2 = 0,06)",
    "Malha de blindagem 0,1 m (K_S2 = 0,012)",
)


MEDIDAS: list[Medida] = [
    Medida(
        id="spda", descricao="SPDA (nível de proteção I-IV)", parametro="P_B",
        componentes=("R_B", "R_V"), escada=_ESC_SPDA,
        _indice=_ind_estrutura("nivel_spda", _ESC_SPDA),
        _definir=_def_estrutura("nivel_spda", _ESC_SPDA),
        _bruto=_bruto_estrutura("nivel_spda"),
    ),
    Medida(
        id="toque_passo",
        descricao="Proteção contra tensão de toque e passo (zonas)",
        parametro="P_TA",
        componentes=("R_A",),  # P_TA so afeta R_A; R_U e do toque_entrada (P_TU)
        escada=_ESC_TP,
        _indice=_ind_zonas("protecao_toque_passo", _ESC_TP),
        _definir=_def_zonas("protecao_toque_passo", _ESC_TP),
        _bruto=_bruto_zonas("protecao_toque_passo", _ESC_TP),
    ),
    Medida(
        id="dps", descricao="Sistema coordenado de DPS", parametro="P_SPD",
        componentes=("R_C", "R_W", "R_Z"), escada=_ESC_DPS,
        _indice=_ind_sistemas_dps(_ESC_DPS),
        _definir=_def_sistemas_dps(_ESC_DPS),
        _bruto=_bruto_sistemas_dps(),
    ),
    Medida(
        id="incendio", descricao="Sistema de combate a incêndio", parametro="r_p",
        componentes=("R_B", "R_V"), escada=_ESC_INC,
        _indice=_ind_estrutura("providencias_incendio", _ESC_INC),
        _definir=_def_estrutura("providencias_incendio", _ESC_INC),
        _bruto=_bruto_estrutura("providencias_incendio"),
    ),
    Medida(
        id="ligacao_eq",
        descricao="Ligação equipotencial na entrada (DPS de EB)",
        parametro="P_EB",
        componentes=("R_U", "R_V"), escada=_ESC_EB,
        _indice=_ind_linhas("nivel_eb", _ESC_EB),
        _definir=_def_linhas("nivel_eb", _ESC_EB),
        _bruto=_bruto_linhas("nivel_eb", _ESC_EB),
    ),
    Medida(
        id="toque_entrada",
        descricao="Proteção contra tensão de toque na entrada das linhas",
        parametro="P_TU",
        componentes=("R_U",), escada=_ESC_TP,
        _indice=_ind_linhas("protecao_toque_entrada", _ESC_TP),
        _definir=_def_linhas("protecao_toque_entrada", _ESC_TP),
        _bruto=_bruto_linhas("protecao_toque_entrada", _ESC_TP),
    ),
    Medida(
        id="blindagem_linha",
        descricao="Blindagem e interligação das linhas externas",
        parametro="P_LD/C_LI",
        componentes=("R_U", "R_V", "R_W", "R_Z"),
        escada=_ESC_BLIND, rotulos=_ROT_BLIND,
        _indice=_ind_blindagem,
        _definir=_def_blindagem,
        _bruto=_bruto_blindagem,
    ),
    Medida(
        id="fiacao",
        descricao="Fiação interna (roteamento/blindagem dos circuitos)",
        parametro="K_S3",
        componentes=("R_M",), escada=_ESC_KS3, rotulos=_ROT_KS3,
        _indice=_ind_sistemas_float("K_S3", _ESC_KS3),
        _definir=_def_sistemas_float("K_S3", _ESC_KS3),
        _bruto=_bruto_sistemas_float("K_S3"),
    ),
    Medida(
        id="blindagem_espacial",
        descricao="Blindagem espacial em malha (zona)",
        parametro="K_S2",
        componentes=("R_M",), escada=_ESC_KS2, rotulos=_ROT_KS2,
        _indice=_ind_sistemas_float("K_S2", _ESC_KS2),
        _definir=_def_sistemas_float("K_S2", _ESC_KS2),
        _bruto=_bruto_sistemas_float("K_S2"),
    ),
]


def por_id() -> dict[str, Medida]:
    return {m.id: m for m in MEDIDAS}

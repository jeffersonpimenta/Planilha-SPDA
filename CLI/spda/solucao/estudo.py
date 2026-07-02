"""Estudo de Solucao (Secao 11): propoe medidas ate R1 <= RT e F <= FT (greedy).

Funcao pura. Para cada estrutura cujo R1 e/ou F excede o toleravel, simula degraus
de medidas do catalogo reusando analisar() e escolhe, a cada passo, a medida que
mais reduz a violacao normalizada viol = max(R1/RT, F/FT). Para quando ambos os
riscos estao dentro do limite (viol <= 1) ou nenhuma medida pode avancar/reduzir. A
decisao final e do engenheiro; aqui so produzimos a proposta ordenada.
"""
from __future__ import annotations

from pydantic import BaseModel, Field

from spda.app import analisar
from spda.model.projeto import Estrutura, Projeto
from spda.solucao.catalogo import MEDIDAS


class PassoSolucao(BaseModel):
    medida: str
    parametro: str
    componentes: list[str]
    de: str
    para: str
    R_projetado: float
    F_projetado: float
    atingiu_rt: bool
    atingiu_ft: bool


class EstudoEstrutura(BaseModel):
    nome: str
    R1_inicial: float
    rt_R1: float
    R1_final: float
    atingiu_rt: bool
    F_inicial: float
    ft: float
    F_final: float
    atingiu_ft: bool
    passos: list[PassoSolucao] = Field(default_factory=list)


class EstudoSolucao(BaseModel):
    projeto: str
    estruturas: list[EstudoEstrutura] = Field(default_factory=list)


def _metricas_de(projeto_base: Projeto, est: Estrutura,
                 config: str | None) -> tuple[float, float]:
    """(R1, F) da estrutura isolada num Projeto minimo (mesmos N_G/overrides)."""
    p = Projeto(
        nome=projeto_base.nome, N_G=projeto_base.N_G,
        rt_override=projeto_base.rt_override,
        ft_override=projeto_base.ft_override, estruturas=[est],
    )
    re = analisar(p, config).estruturas[0]
    return re.R1, re.F


def _viol(R1: float, F: float, rt_R1: float, ft: float) -> float:
    """Violacao normalizada combinada (soma). Recompensa progresso em R1 OU F;
    assim uma medida que so reduz R1 ainda avanca mesmo quando F esta preso por
    falta de medida aplicavel (e vice-versa)."""
    return R1 / rt_R1 + F / ft


def _estudar_estrutura(projeto: Projeto, est: Estrutura, rt_R1: float,
                       ft: float, config: str | None) -> EstudoEstrutura:
    atual = est.model_copy(deep=True)
    R1_ini, F_ini = _metricas_de(projeto, atual, config)
    passos: list[PassoSolucao] = []
    R1, F = R1_ini, F_ini

    while R1 > rt_R1 or F > ft:
        viol_atual = _viol(R1, F, rt_R1, ft)
        melhor = None  # (viol_novo, R1_novo, F_novo, est_novo, medida, de, para)
        for medida in MEDIDAS:
            res = medida.aplicar_proximo(atual)
            if res is None:
                continue
            candidato, de, para = res
            R1_novo, F_novo = _metricas_de(projeto, candidato, config)
            viol_novo = _viol(R1_novo, F_novo, rt_R1, ft)
            if melhor is None or viol_novo < melhor[0]:
                melhor = (viol_novo, R1_novo, F_novo, candidato, medida, de, para)
        if melhor is None:
            break  # nenhuma medida pode avancar
        # So aceita o passo se ele de fato reduz a violacao. Garante decrescimo
        # monotonico e evita "downgrade" em entradas com zonas heterogeneas.
        if melhor[0] >= viol_atual:
            break
        _, R1, F, atual, medida, de, para = melhor
        passos.append(PassoSolucao(
            medida=medida.descricao, parametro=medida.parametro,
            componentes=list(medida.componentes), de=de, para=para,
            R_projetado=R1, F_projetado=F,
            atingiu_rt=R1 <= rt_R1, atingiu_ft=F <= ft,
        ))

    return EstudoEstrutura(
        nome=est.nome, R1_inicial=R1_ini, rt_R1=rt_R1, R1_final=R1,
        atingiu_rt=R1 <= rt_R1, F_inicial=F_ini, ft=ft, F_final=F,
        atingiu_ft=F <= ft, passos=passos,
    )


def estudo_solucao(projeto: Projeto, config: str | None = None) -> EstudoSolucao:
    res = analisar(projeto, config)
    rt_R1 = res.rt["R1"]
    # F_T e por estrutura (7.3.4): 0.1 (criticos) / 1.0 (nao criticos) / override.
    estudos = [
        _estudar_estrutura(projeto, est, rt_R1, res_est.ft, config)
        for est, res_est in zip(projeto.estruturas, res.estruturas)
        if res_est.excede_R1 or res_est.excede_F
    ]
    return EstudoSolucao(projeto=projeto.nome, estruturas=estudos)

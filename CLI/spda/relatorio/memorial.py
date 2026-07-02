# spda/relatorio/memorial.py
"""Monta o memorial de calculo completo (Documento) a partir da Memoria.

Ordem: identificacao -> sumario de riscos -> por estrutura (entradas, eventos, por
linha/trecho, por zona com perdas/probabilidades/componentes, agregacao) ->
recomendacoes (Estudo de Solucao) -> glossario + indices. Markdown e HTML saem do
mesmo Documento.
"""
from __future__ import annotations

from spda.model.memoria import (
    Memoria, MemoriaEstrutura, MemoriaLinha, MemoriaZona, Operacao,
)
from spda.relatorio.documento import (
    Documento, Equacao, Glossario, Lista, Nota, Paragrafo, QuebraPagina, Tabela,
    Titulo, para_markdown,
)
from spda.relatorio.diagnostico import gerar_diagnostico
from spda.relatorio.notas import gerar_notas
from spda.relatorio.formato import fmt
from spda.relatorio.glossario import indice_equacoes, indice_tabelas, simbolos_usados
from spda.relatorio.html import para_html
from spda.relatorio.moldes import renderizar_operacao


def _campo(valor) -> str:
    return "--" if valor is None or valor == "" else str(valor)


def _bloco_identificacao(mem: Memoria) -> list:
    ident = mem.identificacao
    titulo = None
    if ident is not None:
        titulo = ident.titulo
    blocos = [Titulo(1, titulo or "Analise de Risco -- Descargas Atmosfericas")]
    linhas = []
    if ident is not None:
        linhas = [
            ["Cliente", _campo(ident.cliente)],
            ["Endereco", _campo(ident.endereco)],
            ["Responsavel tecnico", _campo(ident.responsavel)],
            ["ART", _campo(ident.art)],
            ["Registro CREA", _campo(ident.registro)],
            ["Norma", f"{_campo(ident.norma)} ({_campo(ident.revisao)})"],
            ["Data", _campo(ident.data)],
            ["Observacoes", _campo(ident.observacoes)],
        ]
    else:
        linhas = [["Identificacao", "-- (nao informada)"]]
    blocos.append(Tabela(["Campo", "Valor"], linhas))
    blocos.append(Paragrafo(
        f"Projeto: **{mem.projeto}** -- Cidade: **{_campo(mem.cidade)}**."))
    return blocos


def _status(excede: bool) -> str:
    return "EXCEDE" if excede else "OK"


def _bloco_sumario(mem: Memoria) -> list:
    blocos = [Titulo(2, "Sumario executivo")]
    cab = ["Estrutura", "R1", "RT(R1)", "R3", "RT(R3)", "R4", "RT(R4)", "F", "FT"]
    linhas = []
    from spda.calc import riscos
    for me in mem.estruturas:
        linhas.append([
            me.nome,
            f"{fmt(me.R1.resultado)} ({_status(riscos.excede(me.R1.resultado, mem.rt['R1']))})",
            fmt(mem.rt["R1"]),
            f"{fmt(me.R3.resultado)} ({_status(riscos.excede(me.R3.resultado, mem.rt['R3']))})",
            fmt(mem.rt["R3"]),
            f"{fmt(me.R4.resultado)} ({_status(riscos.excede(me.R4.resultado, mem.rt['R4']))})",
            fmt(mem.rt["R4"]),
            f"{fmt(me.F.resultado)} ({_status(riscos.excede(me.F.resultado, me.ft))})",
            fmt(me.ft),
        ])
    blocos.append(Tabela(cab, linhas))
    return blocos


def _bloco_notas(mem: Memoria) -> list:
    notas = gerar_notas(mem)
    if not notas:
        return []
    return [Titulo(2, "Notas tecnicas"), *notas]


def _eq(op: Operacao) -> Equacao:
    return renderizar_operacao(op)


def _bloco_linha(ml: MemoriaLinha) -> list:
    blocos = [Titulo(4, f"Linha: {ml.nome}")]
    if ml.nivel_eb:
        blocos.append(Paragrafo(f"DPS de entrada (P_EB): {ml.nivel_eb}."))
    blocos.append(Paragrafo(f"U_W usado nas colunas P_LD/P_LI: {_campo(ml.uw_min)}."))
    for op in (ml.C_LD, ml.C_LI, ml.P_LD, ml.P_LI, ml.P_TU, ml.P_EB,
               ml.P_U, ml.P_V, ml.P_W, ml.P_Z):
        blocos.append(_eq(op))
    for t in ml.trechos:
        blocos.append(Titulo(4, f"  {t.nome} (L_L={fmt(t.L_L)} m)"))
        ops = [t.C_I, t.C_E, t.C_T, t.A_L, t.N_L, t.A_I, t.N_I]
        if t.N_DJ is not None:
            ops.append(t.N_DJ)
        for op in ops:
            blocos.append(_eq(op))
    return blocos


def _bloco_zona(mz: MemoriaZona) -> list:
    blocos = [Titulo(3, f"Zona: {mz.nome}")]
    blocos.append(Paragrafo(
        f"Pessoas n_z={mz.n_z}, presenca t_z={fmt(mz.t_z)} h/ano."))
    blocos.append(Titulo(4, "Coeficientes"))
    for nome in ("r_t", "r_p", "r_f", "r_s", "P_TA", "P_B"):
        if nome in mz.coefs:
            blocos.append(_eq(mz.coefs[nome]))
    blocos.append(Titulo(4, "Presenca e perdas"))
    for op in (mz.presenca, mz.L_A, mz.L_B, mz.L_sis):
        blocos.append(_eq(op))
    for op in (mz.L_B3, mz.L4_A, mz.L4_B, mz.L4_sis):
        if op is not None:
            blocos.append(_eq(op))
    if mz.sistemas:
        blocos.append(Titulo(4, "Sistemas internos"))
        for ms in mz.sistemas:
            blocos.append(Paragrafo(
                f"**{ms.nome}** -- U_W={_campo(ms.U_W)}, DPS={_campo(ms.dps)}."))
            for op in (ms.K_S1, ms.K_S2, ms.K_S3, ms.K_S4, ms.P_SPD, ms.P_MS_i,
                       ms.P_C_i):
                blocos.append(_eq(op))
    blocos.append(Titulo(4, "Probabilidades agregadas"))
    for op in (mz.P_A, mz.P_C, mz.P_M):
        blocos.append(_eq(op))
    if mz.linhas:
        blocos.append(Titulo(4, "Linhas e eventos"))
        for ml in mz.linhas:
            blocos += _bloco_linha(ml)
    blocos.append(Titulo(4, "Componentes de risco da zona"))
    comps = [mz.R_A, mz.R_B, mz.R_C, mz.R_M, mz.R_U, mz.R_V, mz.R_W, mz.R_Z]
    for op in (mz.R_B3, mz.R_V3, mz.R4_total, mz.F_zona):
        if op is not None:
            comps.append(op)
    for op in comps:
        blocos.append(_eq(op))
    return blocos


def _bloco_estrutura(me: MemoriaEstrutura) -> list:
    blocos = [QuebraPagina(), Titulo(2, f"Estrutura: {me.nome}")]
    blocos.append(Titulo(3, "Dados de entrada"))
    blocos.append(Tabela(["Parametro", "Valor"],
                         [[k, _campo(v)] for k, v in me.entradas.items()]))
    blocos.append(Titulo(3, "Numero de eventos"))
    for op in (me.A_D, me.C_D, me.N_D, me.A_M, me.N_M):
        blocos.append(_eq(op))
    for mz in me.zonas:
        blocos += _bloco_zona(mz)
    blocos.append(Titulo(3, "Agregacao de riscos"))
    for op in (me.R1, me.R3, me.R4, me.F):
        blocos.append(_eq(op))
    if me.dominantes:
        itens = [f"{nome} = {fmt(val)}" for nome, val in me.dominantes]
        blocos.append(Paragrafo("**Componentes dominantes de R1:**"))
        blocos.append(Lista(itens, ordenada=True))
    return blocos


def _bloco_recomendacoes(estudo) -> list:
    if estudo is None or not estudo.estruturas:
        return []
    blocos = [QuebraPagina(), Titulo(2, "Recomendacoes (Estudo de Solucao)")]
    for e in estudo.estruturas:
        blocos.append(Titulo(3, e.nome))
        veredito = ("R1 <= RT e F <= FT atingidos com as medidas abaixo."
                    if e.atingiu_rt and e.atingiu_ft
                    else "limites nao atingidos; reporta-se o menor R1/F alcancavel.")
        blocos.append(Paragrafo(
            f"R1 inicial = {fmt(e.R1_inicial)} -> final = {fmt(e.R1_final)} "
            f"(RT = {fmt(e.rt_R1)}); F inicial = {fmt(e.F_inicial)} -> final = "
            f"{fmt(e.F_final)} (FT = {fmt(e.ft)}). {veredito}"))
        linhas = [[str(i), p.medida, p.parametro, f"{p.de} -> {p.para}",
                   fmt(p.R_projetado), fmt(p.F_projetado)]
                  for i, p in enumerate(e.passos, 1)]
        if linhas:
            blocos.append(Tabela(
                ["#", "Medida", "Parametro", "De -> Para", "R1 projetado",
                 "F projetado"], linhas))
    return blocos


def _bloco_glossario_indices(mem: Memoria) -> list:
    blocos = [QuebraPagina(), Titulo(2, "Glossario e indices")]
    blocos.append(Titulo(3, "Glossario de simbolos"))
    blocos.append(Glossario(simbolos_usados(mem)))
    blocos.append(Titulo(3, "Indice de equacoes"))
    blocos.append(Tabela(["Eq.", "Titulo", "Referencia"], indice_equacoes(mem)))
    blocos.append(Titulo(3, "Indice de tabelas"))
    blocos.append(Tabela(["Tabela", "Coeficiente", "Referencia"],
                         indice_tabelas(mem)))
    return blocos


def gerar_documento(memoria: Memoria, estudo=None) -> Documento:
    blocos: list = []
    blocos += _bloco_identificacao(memoria)
    blocos += _bloco_sumario(memoria)
    blocos += _bloco_notas(memoria)
    blocos += gerar_diagnostico(memoria)
    for me in memoria.estruturas:
        blocos += _bloco_estrutura(me)
    blocos += _bloco_recomendacoes(estudo)
    blocos += _bloco_glossario_indices(memoria)
    return Documento(blocos)


def gerar_memorial_markdown(memoria: Memoria, estudo=None) -> str:
    return para_markdown(gerar_documento(memoria, estudo))


def gerar_memorial_html(memoria: Memoria, estudo=None) -> str:
    ident = memoria.identificacao
    titulo = None
    if ident is not None and ident.titulo:
        titulo = ident.titulo
    return para_html(gerar_documento(memoria, estudo),
                     titulo=titulo or f"Analise de Risco -- {memoria.projeto}")

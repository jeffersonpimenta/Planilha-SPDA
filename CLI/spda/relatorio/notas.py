# spda/relatorio/notas.py
"""Motor de notas tecnicas automaticas.

Varre a Memoria e emite avisos deterministicos (info/aviso/critico) sobre
lacunas de assinatura, hipoteses conservadoras e riscos excedidos. Puro: nao
faz I/O; recebe a Memoria e devolve blocos Nota prontos para o Documento.
"""
from __future__ import annotations

from spda.calc import riscos
from spda.model.memoria import Memoria
from spda.relatorio.documento import Nota
from spda.relatorio.formato import fmt

# Campos exigidos para a assinatura da ART (rotulos legiveis).
_CAMPOS_ASSINATURA = [
    ("responsavel", "responsavel tecnico"),
    ("art", "numero da ART"),
    ("registro", "registro CREA"),
    ("data", "data"),
]


def _notas_identificacao(mem: Memoria) -> list[Nota]:
    notas: list[Nota] = []
    if not getattr(mem, "cidade", ""):
        notas.append(Nota("aviso",
                           "Cidade nao informada: e a base do N_G (tabela de "
                           "municipios da norma) e deve constar no laudo."))
    ident = mem.identificacao
    if ident is None:
        notas.append(Nota("aviso",
                     "Bloco de identificacao ausente: laudo nao assinavel sem "
                     "responsavel tecnico, ART e registro CREA."))
        return notas
    faltando = [rotulo for attr, rotulo in _CAMPOS_ASSINATURA
                if getattr(ident, attr, None) in (None, "")]
    if faltando:
        notas.append(Nota("aviso",
                     "Identificacao incompleta para assinatura: "
                     + ", ".join(faltando) + "."))
    return notas


def _notas_riscos(mem: Memoria) -> list[Nota]:
    notas: list[Nota] = []
    algum_excede = False
    for me in mem.estruturas:
        checagens = [
            ("R1", me.R1.resultado, mem.rt["R1"], "critico",
             "risco de perda de vida humana"),
            ("R3", me.R3.resultado, mem.rt["R3"], "aviso",
             "risco de perda de patrimonio cultural"),
            ("R4", me.R4.resultado, mem.rt["R4"], "aviso",
             "risco de perda economica"),
            ("F", me.F.resultado, me.ft, "aviso",
             "frequencia de danos toleravel"),
        ]
        for simbolo, valor, limite, nivel, desc in checagens:
            if riscos.excede(valor, limite):
                algum_excede = True
                notas.append(Nota(nivel,
                    f"{me.nome}: {simbolo} = {fmt(valor)} excede o limite "
                    f"{fmt(limite)} ({desc}). Requer medidas de protecao."))
    if not algum_excede:
        notas.append(Nota("info",
            "Todos os riscos calculados estao dentro dos limites da norma."))
    return notas


def _notas_hipoteses(mem: Memoria) -> list[Nota]:
    notas: list[Nota] = []
    for me in mem.estruturas:
        for mz in me.zonas:
            for ms in mz.sistemas:
                onde = f"{me.nome}/{mz.nome}/{ms.nome}"
                if ms.U_W is None:
                    notas.append(Nota("info",
                        f"{onde}: U_W desconhecido; adotado P_M = 1 (pior caso)."))
                if ms.dps is None:
                    notas.append(Nota("info",
                        f"{onde}: sem DPS coordenado; adotado P_SPD = 1."))
    return notas


def _notas_r4_metodo(mem: Memoria) -> list[Nota]:
    """Explicita o metodo de avaliacao de R4 (afeta como ler o gate R4)."""
    if not any(me.R4.resultado > 0 for me in mem.estruturas):
        return []
    rt_r4 = fmt(mem.rt.get("R4", 0.0))
    if getattr(mem, "r4_representativo", False):
        return [Nota("info",
            f"R4 avaliado com R_T representativo (Tabela 4 = {rt_r4}); as razoes "
            "c/c_t foram adotadas como 1 (nota das Eqs D.1-D.4).")]
    return [Nota("info",
        "R4 avaliado pelo metodo detalhado do Anexo D (razoes c/c_t). O gate "
        f"R4 vs {rt_r4} e indicativo; a justificativa economica formal e por "
        "custo-beneficio (C_L vs C_RL + C_PM).")]


def gerar_notas(mem: Memoria) -> list[Nota]:
    return (_notas_identificacao(mem)
            + _notas_riscos(mem)
            + _notas_r4_metodo(mem)
            + _notas_hipoteses(mem))

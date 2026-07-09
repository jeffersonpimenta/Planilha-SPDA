# GUI/server.py
"""Servidor local da GUI do SPDA (ABNT NBR 5419-2:2026).

Serve o frontend (cópia fiel do design em guibase/) e expõe o motor de cálculo
do CLI (pacote `spda`) por HTTP em 127.0.0.1 — o cálculo, o estudo de solução e
o relatório vêm do Python, não do porte JavaScript do design.

Uso:  python GUI/server.py [--port 8420] [--no-browser]
Requisitos: os mesmos do CLI (pydantic); rode a partir do repositório ou com o
pacote `spda` instalado (pip install -e .).
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
import threading
import webbrowser
from copy import deepcopy
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from math import isclose
from pathlib import Path

RAIZ = Path(__file__).resolve().parent          # GUI/
sys.path.insert(0, str(RAIZ.parent))            # repositório (pacote spda/)

from spda.app import analisar, analisar_memoria, _projetar_resultado  # noqa: E402
from spda.model.projeto import Projeto  # noqa: E402
from spda.relatorio.documento import Paragrafo, Tabela, Titulo  # noqa: E402
from spda.relatorio.html import para_html  # noqa: E402
from spda.relatorio.memorial import gerar_documento  # noqa: E402
from spda.relatorio.formato import fmt  # noqa: E402
from spda.solucao.estudo import estudo_solucao  # noqa: E402
from spda.tabelas.config import carregar_tabelas  # noqa: E402

# ---------------------------------------------------------------------------
# Estudo de Solução da GUI — mesmo comportamento do design (guibase):
# busca combinatória sobre 4 medidas (SPDA, toque/passo, DPS, incêndio),
# operando sobre o JSON cru do projeto e avaliando cada combinação com o
# analisar() do CLI. Os rótulos espelham ENUM_OPTIONS de spda-model.js.
# ---------------------------------------------------------------------------

ESC_SPDA = [None, "IV", "III", "II", "I"]
ESC_DPS = [None, "IV", "III", "II", "I", "melhor_I"]
# Escada completa da Tabela B.1 (o simulador oferece todos os degraus); a
# busca automática só avança até "isolacao" (busca_max=3) para não zerar
# R_A/R_U com os degraus extremos (restrições físicas -> P = 0).
ESC_TP = ["nenhuma", "avisos", "isolacao", "malha_equipotencial",
          "descida_natural", "restricoes_fisicas"]
ESC_TU = ["nenhuma", "avisos", "isolacao", "restricoes_fisicas"]
ESC_INC = ["nenhuma", "extintor", "fixo_automatico"]
ESC_EB = [None, "IV", "III", "II", "I", "melhor_I"]
ESC_BLIND = ["nao_blindada", "rs_5_20", "rs_1_5", "rs_ate_1"]
ESC_KS3 = [1.0, 0.5, 0.2, 0.01, 0.0001]
ESC_KS2 = [1.0, 0.24, 0.12, 0.06, 0.012]

_ROT_SPDA = {"IV": "SPDA nível IV", "III": "SPDA nível III",
             "II": "SPDA nível II", "I": "SPDA nível I"}
_ROT_DPS = {"IV": "DPS para NP IV", "III": "DPS para NP III",
            "II": "DPS para NP II", "I": "DPS para NP I",
            "melhor_I": "DPS melhor que NP I"}
_ROT_TP = {"nenhuma": "Nenhuma medida", "avisos": "Avisos de alerta",
           "isolacao": "Isolação elétrica",
           "malha_equipotencial": "Malha de equipotencialização do solo",
           "descida_natural": "Descida natural (metálica/concreto)",
           "restricoes_fisicas": "Restrições físicas fixas"}
_ROT_INC = {"nenhuma": "Nenhuma providência",
            "extintor": "Manuais (extintores, hidrantes, alarme, rotas de fuga)",
            "fixo_automatico": "Instalações fixas automáticas"}
_ROT_EB = {"IV": "DPS de EB para NP IV", "III": "DPS de EB para NP III",
           "II": "DPS de EB para NP II", "I": "DPS de EB para NP I",
           "melhor_I": "DPS de EB melhor que NP I"}
_ROT_BLIND = {"nao_blindada": "Não blindada",
              "rs_5_20": "Blindada interligada, 5–20 Ω/km",
              "rs_1_5": "Blindada interligada, 1–5 Ω/km",
              "rs_ate_1": "Blindada interligada, ≤ 1 Ω/km"}
_ROT_KS3 = {1.0: "Não blindado, sem cuidado no roteamento (laço ≈ 50 m²)",
            0.5: "Não blindado, evitando grandes laços (≈ 25 m²)",
            0.2: "Não blindado, evitando laços médios (≈ 10 m²)",
            0.01: "Não blindado, evitando pequenos laços (≈ 0,5 m²)",
            0.0001: "Cabo blindado ou em conduto metálico"}
_ROT_KS2 = {1.0: "Sem blindagem espacial (K_S2 = 1)",
            0.24: "Malha de blindagem 2 m (K_S2 = 0,24)",
            0.12: "Malha de blindagem 1 m (K_S2 = 0,12)",
            0.06: "Malha de blindagem 0,5 m (K_S2 = 0,06)",
            0.012: "Malha de blindagem 0,1 m (K_S2 = 0,012)"}


def _rot(mapa: dict, v) -> str:
    return "nenhum" if v is None else mapa.get(v, str(v))


def _idx_of(valor, escada):
    if valor == "nenhum" and None in escada:
        valor = None
    return escada.index(valor) if valor in escada else None


def _idx_zonas(est: dict, campo: str, escada):
    zonas = est.get("zonas") or []
    if not zonas:
        return None
    idxs = [_idx_of((z.get("medidas") or {}).get(campo), escada) for z in zonas]
    if any(i is None for i in idxs):
        return None
    return min(idxs)


def _idx_sistemas(est: dict, escada):
    sistemas = [s for z in (est.get("zonas") or [])
                for s in (z.get("sistemas_internos") or [])]
    if not sistemas:
        return None
    idxs = [_idx_of(s.get("dps"), escada) for s in sistemas]
    if any(i is None for i in idxs):
        return None
    return min(idxs)


def _idx_float(valor, escada):
    if not isinstance(valor, (int, float)) or isinstance(valor, bool):
        return None
    return next((i for i, dv in enumerate(escada)
                 if isclose(float(valor), dv, rel_tol=1e-9)), None)


def _idx_linhas(est: dict, campo: str, escada):
    linhas = est.get("linhas") or []
    if not linhas:
        return None
    idxs = [_idx_of(li.get(campo), escada) for li in linhas]
    if any(i is None for i in idxs):
        return None
    return min(idxs)


def _idx_sistemas_float(est: dict, attr: str, escada):
    sistemas = [s for z in (est.get("zonas") or [])
                for s in (z.get("sistemas_internos") or [])]
    if not sistemas:
        return None
    idxs = [_idx_float(s.get(attr), escada) for s in sistemas]
    if any(i is None for i in idxs):
        return None  # valor custom -> não sobrescrevemos cegamente
    return min(idxs)


# Linhas já "melhores" que a escada de blindagem (C_LD = 0) nunca são tocadas.
_TIPOS_LINHA_MELHORES = {"eletroduto_metalico", "fibra_optica",
                         "interface_isolante"}


def _idx_blindagem(est: dict):
    linhas = [li for li in (est.get("linhas") or [])
              if li.get("tipo_externa") not in _TIPOS_LINHA_MELHORES]
    if not linhas:
        return None
    idxs = []
    for li in linhas:
        cb = li.get("classe_blindagem")
        if cb == "nao_blindada":
            idxs.append(0)
        elif (li.get("tipo_externa") == "blindada_interligada"
              and cb in ESC_BLIND):
            idxs.append(ESC_BLIND.index(cb))
        else:
            return None  # blindada mas não interligada etc. -> fora da escada
    return min(idxs)


def _aplicar_spda(est: dict, valor) -> dict:
    copia = deepcopy(est)
    copia["nivel_spda"] = valor
    return copia


def _aplicar_tp(est: dict, valor) -> dict:
    copia = deepcopy(est)
    for z in copia.get("zonas") or []:
        z.setdefault("medidas", {})["protecao_toque_passo"] = valor
    return copia


def _aplicar_dps(est: dict, valor) -> dict:
    copia = deepcopy(est)
    for z in copia.get("zonas") or []:
        for s in z.get("sistemas_internos") or []:
            s["dps"] = valor
    return copia


def _aplicar_inc(est: dict, valor) -> dict:
    copia = deepcopy(est)
    copia["providencias_incendio"] = valor
    return copia


def _aplicar_linhas(campo: str):
    def f(est: dict, valor) -> dict:
        copia = deepcopy(est)
        for li in copia.get("linhas") or []:
            li[campo] = valor
        return copia
    return f


def _aplicar_blindagem(est: dict, valor) -> dict:
    copia = deepcopy(est)
    for li in copia.get("linhas") or []:
        if li.get("tipo_externa") in _TIPOS_LINHA_MELHORES:
            continue
        if valor == "nao_blindada":
            if li.get("classe_blindagem") == "nao_blindada":
                continue  # já no degrau base: não reescreve tipo_externa
            # Degrau base coerente: sem crédito de blindagem NEM de C_LI
            # (blindada_interligada + nao_blindada seria inconsistente).
            li["tipo_externa"] = "aerea_nao_blindada"
            li["classe_blindagem"] = "nao_blindada"
        else:
            li["tipo_externa"] = "blindada_interligada"
            li["classe_blindagem"] = valor
    return copia


def _aplicar_sistemas_float(attr: str):
    def f(est: dict, valor) -> dict:
        copia = deepcopy(est)
        for z in copia.get("zonas") or []:
            for s in z.get("sistemas_internos") or []:
                s[attr] = float(valor)
        return copia
    return f


# Mesmo catálogo do CLI (spda/solucao/catalogo.py), sobre o JSON cru.
# "busca_max": limite (exclusivo) de degrau para a busca automática; o
# simulador continua oferecendo a escada inteira. "num": escada de floats
# (valores vindos de <select> chegam como string e são normalizados).
MEDIDAS_GUI = [
    {"id": "spda", "descricao": "SPDA (nível de proteção)", "escada": ESC_SPDA,
     "rotulo": lambda v: _rot(_ROT_SPDA, v),
     "aplicavel": lambda est: True,
     "indice": lambda est: _idx_of(est.get("nivel_spda"), ESC_SPDA),
     "aplicar": _aplicar_spda},
    {"id": "toque_passo", "descricao": "Proteção contra tensão de toque e passo",
     "escada": ESC_TP, "busca_max": 3,
     "rotulo": lambda v: _rot(_ROT_TP, v),
     "aplicavel": lambda est: bool(est.get("zonas")),
     "indice": lambda est: _idx_zonas(est, "protecao_toque_passo", ESC_TP),
     "aplicar": _aplicar_tp},
    {"id": "dps", "descricao": "Sistema coordenado de DPS", "escada": ESC_DPS,
     "rotulo": lambda v: _rot(_ROT_DPS, v),
     "aplicavel": lambda est: any(z.get("sistemas_internos")
                                  for z in est.get("zonas") or []),
     "indice": lambda est: _idx_sistemas(est, ESC_DPS),
     "aplicar": _aplicar_dps},
    {"id": "incendio", "descricao": "Sistema de combate a incêndio",
     "escada": ESC_INC,
     "rotulo": lambda v: _rot(_ROT_INC, v),
     "aplicavel": lambda est: True,
     "indice": lambda est: _idx_of(est.get("providencias_incendio"), ESC_INC),
     "aplicar": _aplicar_inc},
    {"id": "ligacao_eq",
     "descricao": "Ligação equipotencial na entrada (DPS de EB)",
     "escada": ESC_EB,
     "rotulo": lambda v: _rot(_ROT_EB, v),
     "aplicavel": lambda est: bool(est.get("linhas")),
     "indice": lambda est: _idx_linhas(est, "nivel_eb", ESC_EB),
     "aplicar": _aplicar_linhas("nivel_eb")},
    {"id": "toque_entrada",
     "descricao": "Proteção contra tensão de toque na entrada das linhas",
     "escada": ESC_TU, "busca_max": 3,
     "rotulo": lambda v: _rot(_ROT_TP, v),
     "aplicavel": lambda est: bool(est.get("linhas")),
     "indice": lambda est: _idx_linhas(est, "protecao_toque_entrada", ESC_TU),
     "aplicar": _aplicar_linhas("protecao_toque_entrada")},
    {"id": "blindagem_linha",
     "descricao": "Blindagem e interligação das linhas externas",
     "escada": ESC_BLIND,
     "rotulo": lambda v: _rot(_ROT_BLIND, v),
     "aplicavel": lambda est: bool(est.get("linhas")),
     "indice": _idx_blindagem,
     "aplicar": _aplicar_blindagem},
    {"id": "fiacao",
     "descricao": "Fiação interna (roteamento/blindagem dos circuitos)",
     "escada": ESC_KS3, "num": True,
     "rotulo": lambda v: _rot(_ROT_KS3, v),
     "aplicavel": lambda est: any(z.get("sistemas_internos")
                                  for z in est.get("zonas") or []),
     "indice": lambda est: _idx_sistemas_float(est, "K_S3", ESC_KS3),
     "aplicar": _aplicar_sistemas_float("K_S3")},
    {"id": "blindagem_espacial",
     "descricao": "Blindagem espacial em malha (zona)",
     "escada": ESC_KS2, "num": True,
     "rotulo": lambda v: _rot(_ROT_KS2, v),
     "aplicavel": lambda est: any(z.get("sistemas_internos")
                                  for z in est.get("zonas") or []),
     "indice": lambda est: _idx_sistemas_float(est, "K_S2", ESC_KS2),
     "aplicar": _aplicar_sistemas_float("K_S2")},
]


def _indice_valor_medida(m: dict, valor):
    """Degrau de `valor` na escada da medida (tolerante a floats/strings)."""
    if m.get("num"):
        if isinstance(valor, str) and valor:
            try:
                valor = float(valor)
            except ValueError:
                return None
        return _idx_float(valor, m["escada"])
    return _idx_of(valor, m["escada"])


def _medidas_disponiveis(est: dict):
    return [m for m in MEDIDAS_GUI
            if m["aplicavel"](est) and m["indice"](est) is not None]


def _metricas_estrutura(projeto: dict, est: dict):
    """ResultadoEstrutura da estrutura isolada num projeto mínimo (como o design)."""
    mini = {
        "nome": projeto.get("nome", ""), "N_G": projeto.get("N_G"),
        "rt_override": projeto.get("rt_override"),
        "ft_override": projeto.get("ft_override"),
        "r4_representativo": projeto.get("r4_representativo", False),
        "estruturas": [est],
    }
    return analisar(Projeto.model_validate(mini)).estruturas[0]


def _rt_r1(projeto: dict, rt_padrao: dict) -> float:
    rt_ov = projeto.get("rt_override") or {}
    return rt_ov.get("R1", rt_padrao["R1"])


def _aplicar_combo(est: dict, medidas, combo: dict) -> dict:
    # Chave ausente no combo (ex.: proposta salva antes de uma medida passar a
    # existir na estrutura) mantém o valor atual — nunca anula a medida.
    # Medida sem mudança (ou com valor fora da escada) não é aplicada: manter
    # o estado real evita que o "aplicar uniforme" reescreva valores mistos
    # (ex.: sistemas com DPS diferentes) num combo que não mexe na medida.
    atual = est
    for m in medidas:
        i_atual = m["indice"](est)
        valor = combo.get(m["id"], m["escada"][i_atual])
        i_alvo = _indice_valor_medida(m, valor)
        if i_alvo is None or i_alvo == i_atual:
            continue
        atual = m["aplicar"](atual, m["escada"][i_alvo])
    return atual


# Amostragem de alvos por medida (máx. 4 por escada, como o design) com
# orçamento global: com 9 medidas o produto cartesiano explode, então o
# número de alvos por medida cai até o total de combinações caber no teto.
MAX_ALVOS_POR_MEDIDA = 4
ORCAMENTO_COMBOS = 600


def _amostrar_alvos(m: dict, i_atual: int, max_alvos: int):
    escada = m["escada"]
    fim = m.get("busca_max") or len(escada)
    if i_atual >= fim:
        return [escada[i_atual]]  # acima da faixa de busca: fica como está
    faixa = escada[i_atual:fim]
    if len(faixa) <= max_alvos:
        return faixa
    passo = (len(faixa) - 1) / (max_alvos - 1)
    idxs = sorted({round(k * passo) for k in range(max_alvos)})
    return [faixa[i] for i in idxs]


def pacotes_para_estrutura(projeto: dict, est: dict, rt_padrao: dict,
                           max_pacotes: int = 3) -> dict:
    base = _metricas_estrutura(projeto, est)
    medidas = _medidas_disponiveis(est)
    medidas_info = []
    for m in medidas:
        i_atual = m["indice"](est)
        medidas_info.append({
            "id": m["id"], "descricao": m["descricao"],
            "opcoes": [{"valor": v, "rotulo": m["rotulo"](v),
                        "disponivel": idx >= i_atual}
                       for idx, v in enumerate(m["escada"])],
            "valorAtual": m["escada"][i_atual],
        })
    identidade = {m["id"]: m["escada"][m["indice"](est)] for m in medidas}
    if not (base.excede_R1 or base.excede_F):
        return {"nome": est.get("nome", ""), "jaConforme": True,
                "R1": base.R1, "F": base.F, "rt_R1": None, "ft": base.ft,
                "medidas": medidas_info, "identidade": identidade,
                "pacotes": [], "semSolucao": False}
    rt_r1 = _rt_r1(projeto, rt_padrao)
    max_alvos = MAX_ALVOS_POR_MEDIDA
    while True:
        alvos_por_medida = [(m, _amostrar_alvos(m, m["indice"](est), max_alvos))
                            for m in medidas]
        n_combos = 1
        for _, alvos in alvos_por_medida:
            n_combos *= len(alvos)
        if n_combos <= ORCAMENTO_COMBOS or max_alvos <= 2:
            break
        max_alvos -= 1
    avaliados = []
    for valores in itertools.product(*(alvos for _, alvos in alvos_por_medida)):
        combo = {m["id"]: v for (m, _), v in zip(alvos_por_medida, valores)}
        est_mod = _aplicar_combo(est, medidas, combo)
        re = _metricas_estrutura(projeto, est_mod)
        mudancas, saltos, detalhes = 0, 0, []
        for m in medidas:
            i_atual = m["indice"](est)
            i_alvo = _indice_valor_medida(m, combo[m["id"]])
            mudou = i_alvo != i_atual
            if mudou:
                mudancas += 1
                saltos += abs(i_alvo - i_atual)
            detalhes.append({"id": m["id"], "descricao": m["descricao"],
                             "de": m["rotulo"](m["escada"][i_atual]),
                             "para": m["rotulo"](combo[m["id"]]),
                             "mudou": mudou})
        avaliados.append({
            "combo": combo, "re": re, "mudancas": mudancas, "saltos": saltos,
            "detalhes": detalhes,
            "valido": re.R1 <= rt_r1 and re.F <= re.ft,
        })
    validos = [a for a in avaliados if a["valido"] and a["mudancas"] > 0]
    validos.sort(key=lambda a: (a["mudancas"], a["saltos"], a["re"].R1))
    vistos, top = set(), []
    for a in validos:
        chave = json.dumps(a["combo"], sort_keys=True)
        if chave in vistos:
            continue
        vistos.add(chave)
        top.append(a)
        if len(top) >= max_pacotes:
            break
    return {
        "nome": est.get("nome", ""), "jaConforme": False,
        "R1": base.R1, "F": base.F, "rt_R1": rt_r1, "ft": base.ft,
        "medidas": medidas_info, "identidade": identidade,
        "pacotes": [{
            "indice": i + 1, "combo": a["combo"],
            "mudancas": [d for d in a["detalhes"] if d["mudou"]],
            "R1": a["re"].R1, "R3": a["re"].R3, "R4": a["re"].R4,
            "F": a["re"].F, "ft": a["re"].ft,
        } for i, a in enumerate(top)],
        "semSolucao": len(validos) == 0,
    }


def avaliar_combinacao(projeto: dict, est: dict, combo: dict) -> dict:
    medidas = _medidas_disponiveis(est)
    re = _metricas_estrutura(projeto, _aplicar_combo(est, medidas, combo))
    return {"R1": re.R1, "R3": re.R3, "R4": re.R4, "F": re.F, "ft": re.ft,
            "excede_R1": re.excede_R1, "excede_R3": re.excede_R3,
            "excede_R4": re.excede_R4, "excede_F": re.excede_F}


# ---------------------------------------------------------------------------
# Relatório — memorial do CLI + propostas registradas na GUI ("Salvar
# proposta"), inseridas como blocos antes do glossário.
# ---------------------------------------------------------------------------

def _blocos_propostas(projeto_raw: dict, rt_padrao: dict) -> list:
    linhas_blocos: list = []
    rt_r1 = _rt_r1(projeto_raw, rt_padrao)
    for est in projeto_raw.get("estruturas") or []:
        proposta = est.get("proposta") or {}
        combo = proposta.get("combo")
        if not combo:
            continue
        medidas = _medidas_disponiveis(est)
        mudancas = []
        for m in medidas:
            i_atual = m["indice"](est)
            valor = combo.get(m["id"], m["escada"][i_atual])
            i_alvo = _indice_valor_medida(m, valor)
            if i_alvo is None or i_alvo == i_atual:
                continue
            mudancas.append([m["descricao"],
                             m["rotulo"](m["escada"][i_atual]),
                             m["rotulo"](m["escada"][i_alvo])])
        atual = _metricas_estrutura(projeto_raw, est)
        if not mudancas:
            # Proposta igual ao as-built: registra mesmo assim — omitir em
            # silêncio faz a proposta salva "sumir" do relatório.
            linhas_blocos.append(Titulo(3, est.get("nome", "")))
            linhas_blocos.append(Paragrafo(
                f"A proposta salva é idêntica às medidas atuais (as-built) — "
                f"nenhuma mudança a listar. Situação: R1 = {fmt(atual.R1)} "
                f"(RT = {fmt(rt_r1)}); F = {fmt(atual.F)} "
                f"(FT = {fmt(atual.ft)})."))
            continue
        avaliado = avaliar_combinacao(projeto_raw, est, combo)
        atinge = (avaliado["R1"] <= rt_r1) and (avaliado["F"] <= avaliado["ft"])
        veredito = ("atende R1 e F" if atinge
                    else "não atinge os limites toleráveis")
        linhas_blocos.append(Titulo(3, est.get("nome", "")))
        linhas_blocos.append(Paragrafo(
            f"Situação atual: R1 = {fmt(atual.R1)} (RT = {fmt(rt_r1)}); "
            f"F = {fmt(atual.F)} (FT = {fmt(atual.ft)}). Com a proposta: "
            f"R1 = {fmt(avaliado['R1'])}; F = {fmt(avaliado['F'])}; "
            f"R3 = {fmt(avaliado['R3'])}; R4 = {fmt(avaliado['R4'])} "
            f"— {veredito}. A proposta NÃO altera os dados atuais (as-built); "
            f"registra o cenário avaliado pelo engenheiro."))
        linhas_blocos.append(Tabela(["Medida", "Atual", "Proposto"], mudancas))
    if not linhas_blocos:
        return []
    return [Titulo(2, "Propostas avaliadas (Estudo de Solução)")] + linhas_blocos


def gerar_relatorio_html(projeto_raw: dict, rt_padrao: dict) -> str:
    projeto = Projeto.model_validate(projeto_raw)
    memoria = analisar_memoria(projeto)
    try:
        estudo = estudo_solucao(projeto)
    except Exception:
        estudo = None
    propostas = _blocos_propostas(projeto_raw, rt_padrao)
    doc = gerar_documento(memoria, estudo, solucao=propostas)
    ident = memoria.identificacao
    titulo = (ident.titulo if ident is not None and ident.titulo
              else f"Análise de Risco -- {memoria.projeto}")
    return para_html(doc, titulo=titulo)


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------

class Handler(SimpleHTTPRequestHandler):
    # tabelas carregadas uma vez (RT padrão da Tabela 4)
    tabelas = carregar_tabelas(None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(RAIZ), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def log_message(self, fmt_, *args):
        pass  # silencioso; erros de API respondem 400 com a mensagem

    def do_GET(self):  # noqa: N802 (nome da stdlib)
        if self.path.split("?", 1)[0] == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return
        super().do_GET()

    def _json(self, status: int, payload) -> None:
        corpo = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def _html(self, status: int, html: str) -> None:
        corpo = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def do_POST(self):  # noqa: N802 (nome da stdlib)
        try:
            tamanho = int(self.headers.get("Content-Length") or 0)
            corpo = json.loads(self.rfile.read(tamanho) or b"{}")
            rota = self.path.split("?", 1)[0]
            if rota == "/api/ref":
                self._json(200, {"RT": dict(self.tabelas.RT)})
            elif rota == "/api/analise":
                self._api_analise(corpo)
            elif rota == "/api/pacotes":
                pac = pacotes_para_estrutura(
                    corpo["projeto"],
                    corpo["projeto"]["estruturas"][corpo["estIndex"]],
                    dict(self.tabelas.RT), corpo.get("maxPacotes", 3))
                self._json(200, pac)
            elif rota == "/api/avaliar":
                av = avaliar_combinacao(
                    corpo["projeto"],
                    corpo["projeto"]["estruturas"][corpo["estIndex"]],
                    corpo["combo"])
                self._json(200, av)
            elif rota == "/api/relatorio":
                self._html(200, gerar_relatorio_html(
                    corpo["projeto"], dict(self.tabelas.RT)))
            else:
                self._json(404, {"erro": f"rota desconhecida: {rota}"})
        except Exception as exc:  # validação/cálculo -> mensagem ao usuário
            self._json(400, {"erro": str(exc)})

    def _api_analise(self, corpo: dict) -> None:
        projeto = Projeto.model_validate(corpo["projeto"])
        memoria = analisar_memoria(projeto)
        resultado = _projetar_resultado(memoria)
        # identificacao é tipada como `object` na Memoria (evita import
        # circular) e não é usada pelo frontend — zera antes de serializar.
        mem = memoria.model_copy(update={"identificacao": None})
        self._json(200, {"resultado": resultado.model_dump(mode="json"),
                         "memoria": mem.model_dump(mode="json")})


def main() -> None:
    ap = argparse.ArgumentParser(description="GUI local do SPDA (NBR 5419-2)")
    ap.add_argument("--port", type=int, default=8420)
    ap.add_argument("--no-browser", action="store_true",
                    help="não abrir o navegador automaticamente")
    args = ap.parse_args()

    servidor = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    url = f"http://127.0.0.1:{args.port}/"
    print(f"SPDA GUI em {url}  (Ctrl+C para encerrar)")
    if not args.no_browser:
        threading.Timer(0.4, webbrowser.open, args=(url,)).start()
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        servidor.server_close()


if __name__ == "__main__":
    main()

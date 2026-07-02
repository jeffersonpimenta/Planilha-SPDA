"""Orquestracao: monta os valores resolvidos do model, chama calc/ e captura a
memoria de calculo. analisar() projeta o Resultado enxuto da Memoria."""
from __future__ import annotations

from spda.calc import componentes, eventos, frequencia, perdas
from spda.calc import probabilidades as pr
from spda.calc import riscos
from spda.model.memoria import (
    Memoria, MemoriaEstrutura, MemoriaLinha, MemoriaSistemaInterno,
    MemoriaTrecho, MemoriaZona, Operacao,
)
from spda.model.enums import rotulo, TipoOcupacao, ZonaExplosao
from spda.model.projeto import Estrutura, Linha, Projeto, Zona
from spda.model.resultado import Resultado, ResultadoEstrutura, ResultadoZona
from spda.tabelas import referencia as ref
from spda.tabelas.config import Tabelas, carregar_tabelas

_UW_CONSERVADOR_KV = 1.0  # coluna de U_W assumida quando desconhecida (pior caso)


def _op(simbolo: str, eq: str, operandos: dict, fn, *, valor=None,
        origem=None) -> Operacao:
    """Grava uma Operacao. Se `valor` e None, computa fn(**operandos)."""
    if valor is None:
        valor = fn(**operandos)
    return Operacao(simbolo=simbolo, eq=eq, operandos=operandos,
                    resultado=valor, origem=origem)


def _coef(simbolo: str, eq: str, valor: float, origem: str) -> Operacao:
    """Operacao de lookup de tabela (sem operandos; guarda a origem)."""
    return Operacao(simbolo=simbolo, eq=eq, operandos={}, resultado=valor,
                    origem=origem)


# ---------------------------------------------------------------------------
# Captura da memoria
# ---------------------------------------------------------------------------

def analisar_memoria(projeto: Projeto, config: str | None = None) -> Memoria:
    tab = carregar_tabelas(config)
    rt = dict(tab.RT)
    if projeto.rt_override:
        rt.update(projeto.rt_override)
    estruturas = [_mem_estrutura(projeto, est, tab) for est in projeto.estruturas]
    return Memoria(projeto=projeto.nome, cidade=projeto.cidade,
                   identificacao=projeto.identificacao,
                   rt=rt, r4_representativo=projeto.r4_representativo,
                   estruturas=estruturas)


def _ft_estrutura(projeto: Projeto, est: Estrutura, tab: Tabelas) -> float:
    """F_T da estrutura (7.3.4): 0.1/ano se ha sistemas criticos (imutavel,
    salvo autoridade com jurisdicao -> ft_override), senao 1/ano."""
    if projeto.ft_override is not None:
        return projeto.ft_override
    chave = "critico" if est.sistemas_criticos else "nao_critico"
    return tab.FT[chave]


def _mem_eventos_estrutura(projeto: Projeto, est: Estrutura, tab: Tabelas):
    if est.H_min is not None and est.H_max is not None:
        A_D = _op("A_D", "A.1/A.2",
                  {"L": est.L, "W": est.W, "H_min": est.H_min,
                   "H_max": est.H_max}, eventos.area_AD_complexa,
                  origem="forma complexa (A.2.1.3.2): maior entre A_D(H_min) "
                         "e A'_D = pi*(3*H_max)^2")
    else:
        A_D = _op("A_D", "A.1", {"L": est.L, "W": est.W, "H": est.H},
                  eventos.area_AD)
    C_D = _coef("C_D", "Tabela A.1", tab.C_D[est.localizacao],
                rotulo(est.localizacao))
    N_D = _op("N_D", "A.3",
              {"N_G": projeto.N_G, "A_D": A_D.resultado, "C_D": C_D.resultado},
              eventos.N_D)
    A_M = _op("A_M", "A.6", {"L": est.L, "W": est.W}, eventos.area_AM)
    N_M = _op("N_M", "A.5", {"N_G": projeto.N_G, "A_M": A_M.resultado},
              eventos.N_M)
    return A_D, C_D, N_D, A_M, N_M


def _n_dj_linha(projeto: Projeto, linha: Linha, tab: Tabelas) -> float:
    if linha.adjacente is None:
        return 0.0
    adj = linha.adjacente
    A_DJ = eventos.area_AD(adj.L_J, adj.W_J, adj.H_J)
    return eventos.N_DJ(projeto.N_G, A_DJ, tab.C_D[adj.localizacao_J],
                        tab.C_T[linha.tipo])


def _mem_linha(projeto: Projeto, linha: Linha, uw_min,
               sistemas, uw_label, tab: Tabelas) -> MemoriaLinha:
    """Captura coeficientes e probabilidades de uma linha (eventos por trecho)."""
    N_DJ_val = _n_dj_linha(projeto, linha, tab)
    ml = MemoriaLinha(
        nome=linha.nome,
        nivel_eb=None if linha.nivel_eb is None else rotulo(linha.nivel_eb),
        uw_min=uw_min,
    )
    N_L_total = 0.0
    N_I_total = 0.0
    for i, tr in enumerate(linha.trechos):
        inst = tr.instalacao or linha.instalacao
        amb = tr.ambiente or linha.ambiente
        tip = tr.tipo or linha.tipo
        C_I = _coef("C_I", "Tabela A.2", tab.C_I[inst], rotulo(inst))
        C_E = _coef("C_E", "Tabela A.4", tab.C_E[amb], rotulo(amb))
        C_T = _coef("C_T", "Tabela A.3", tab.C_T[tip], rotulo(tip))
        A_L_val = eventos.area_AL(tr.L_L, tr.rho)
        A_L_ops = {"L_L": tr.L_L} if tr.rho is None else {"L_L": tr.L_L, "rho": tr.rho}
        A_L = _op("A_L", "A.8", A_L_ops, eventos.area_AL, valor=A_L_val)
        N_L = _op("N_L", "A.7",
                  {"N_G": projeto.N_G, "A_L": A_L.resultado,
                   "C_I": C_I.resultado, "C_E": C_E.resultado,
                   "C_T": C_T.resultado}, eventos.N_L)
        A_I = _op("A_I", "A.10", {"L_L": tr.L_L}, eventos.area_AI)
        N_I = _op("N_I", "A.9",
                  {"N_G": projeto.N_G, "A_I": A_I.resultado,
                   "C_I": C_I.resultado, "C_E": C_E.resultado,
                   "C_T": C_T.resultado}, eventos.N_I)
        N_DJ = None
        if i == 0 and N_DJ_val:
            N_DJ = Operacao(simbolo="N_DJ", eq="A.4", operandos={},
                            resultado=N_DJ_val,
                            origem=f"adjacente: {rotulo(linha.adjacente.localizacao_J)}")
        ml.trechos.append(MemoriaTrecho(
            nome=f"trecho {i + 1}", L_L=tr.L_L, rho=tr.rho,
            C_I=C_I, C_E=C_E, C_T=C_T, A_L=A_L, N_L=N_L, A_I=A_I, N_I=N_I,
            N_DJ=N_DJ))
        N_L_total += N_L.resultado + (N_DJ_val if i == 0 else 0.0)
        N_I_total += N_I.resultado
    ml.N_L_total = N_L_total
    ml.N_I_total = N_I_total

    C_LD = _coef("C_LD", "Tabela B.4", tab.C_LD[linha.tipo_externa],
                 rotulo(linha.tipo_externa))
    C_LI = _coef("C_LI", "Tabela B.4", tab.C_LI[linha.tipo_externa],
                 rotulo(linha.tipo_externa))
    P_LD = _coef("P_LD", "Tabela B.8", ref.pld(linha.classe_blindagem, uw_min),
                 f"{rotulo(linha.classe_blindagem)}, U_W={uw_label}")
    P_LI = _coef("P_LI", "Tabela B.9", ref.pli(linha.categoria, uw_min),
                 f"{rotulo(linha.categoria)}, U_W={uw_label}")
    P_TU = _coef("P_TU", "Tabela B.6", tab.P_TU[linha.protecao_toque_entrada],
                 rotulo(linha.protecao_toque_entrada))
    P_EB_val = 1.0 if linha.nivel_eb is None else tab.P_EB[linha.nivel_eb]
    P_EB = _coef("P_EB", "Tabela B.7", P_EB_val,
                 "sem DPS" if linha.nivel_eb is None else rotulo(linha.nivel_eb))
    ml.C_LD, ml.C_LI = C_LD, C_LI
    ml.P_LD, ml.P_LI, ml.P_TU, ml.P_EB = P_LD, P_LI, P_TU, P_EB
    ml.P_U = _op("P_U", "B.8",
                 {"P_TU": P_TU.resultado, "P_EB": P_EB.resultado,
                  "P_LD": P_LD.resultado, "C_LD": C_LD.resultado}, pr.P_U)
    ml.P_V = _op("P_V", "B.9",
                 {"P_EB": P_EB.resultado, "P_LD": P_LD.resultado,
                  "C_LD": C_LD.resultado}, pr.P_V)
    # R_W/R_Z (e F_W/F_Z): valor unico pior-caso sobre sistemas (norma 6.9.1.2a
    # / 7.4.1.2a) -- NAO se combina como R_C/R_M.
    P_W_val = pr.pior_caso(
        [pr.P_W(s["P_SPD"], P_LD.resultado, C_LD.resultado) for s in sistemas])
    P_Z_val = pr.pior_caso(
        [pr.P_Z(s["P_SPD"], P_LI.resultado, C_LI.resultado) for s in sistemas])
    ml.P_W = Operacao(simbolo="P_W", eq="B.10",
                      operandos={"P_LD": P_LD.resultado, "C_LD": C_LD.resultado},
                      resultado=P_W_val,
                      origem="pior caso sobre sistemas (6.9.1.2a/7.4.1.2a)")
    ml.P_Z = Operacao(simbolo="P_Z", eq="B.11",
                      operandos={"P_LI": P_LI.resultado, "C_LI": C_LI.resultado},
                      resultado=P_Z_val,
                      origem="pior caso sobre sistemas (6.9.1.2a/7.4.1.2a)")
    return ml


def _tem_explosao(est: Estrutura) -> bool:
    return est.risco_explosao or est.zona_explosao is not ZonaExplosao.nenhuma


def _zona_explosao_efetiva(est: Estrutura) -> ZonaExplosao:
    """Zona usada para r_f. risco_explosao (bool) sem zona -> pior caso (0/20)."""
    if est.zona_explosao is not ZonaExplosao.nenhuma:
        return est.zona_explosao
    return ZonaExplosao.zona_0_20 if est.risco_explosao else ZonaExplosao.nenhuma


def _resolver_r_f_r_p(est: Estrutura, tab: Tabelas) -> tuple[Operacao, Operacao]:
    """r_f e r_p. Com risco de explosao: r_f da Tabela C.5 e r_p=1 (C.3.4)."""
    if _tem_explosao(est):
        ze = _zona_explosao_efetiva(est)
        r_f = _coef("r_f", "Tabela C.5", tab.R_F_EXPLOSAO[ze],
                    rotulo(ze))
        r_p = _coef("r_p", "C.3.4", 1.0, "risco de explosão → r_p = 1")
        return r_f, r_p
    r_f = _coef("r_f", "Tabela C.5", tab.R_F[est.risco_incendio],
                rotulo(est.risco_incendio))
    r_p = _coef("r_p", "Tabela C.4", tab.R_P[est.providencias_incendio],
                rotulo(est.providencias_incendio))
    return r_f, r_p


def _resolver_L_F(est: Estrutura, tab: Tabelas) -> float:
    """L_F (Tabela C.2) por ocupacao; estrutura com explosao -> 0.1."""
    return ref.L_F_EXPLOSAO if _tem_explosao(est) else tab.L_F[est.ocupacao]


def _resolver_L_O(est: Estrutura) -> float:
    if _tem_explosao(est):
        return ref.L_O_EXPLOSAO
    if est.sistemas_criticos:
        return ref.L_O_HOSPITAL_CRITICO
    return ref.L_O_PADRAO


def _resolver_L_F_L4(est: Estrutura) -> float:
    """L_F economico (L4, Tabela C.12); explosao -> 1.0. NAO usa a tabela de L1."""
    return ref.L_F_L4_EXPLOSAO if _tem_explosao(est) else ref.L_F_L4[est.ocupacao]


def _resolver_L_O_L4(est: Estrutura) -> float:
    """L_O economico (L4, Tabela C.12); explosao -> 0.1. NAO usa a tabela de L1."""
    return ref.L_O_L4_EXPLOSAO if _tem_explosao(est) else ref.L_O_L4[est.ocupacao]


def _mem_zona(projeto: Projeto, est: Estrutura, zona: Zona,
              eventos_est, tab: Tabelas) -> MemoriaZona:
    A_D, C_D, N_D_op, A_M, N_M_op = eventos_est
    N_D = N_D_op.resultado
    N_M = N_M_op.resultado

    r_t = _coef("r_t", "Tabela C.3", tab.R_T[zona.superficie], rotulo(zona.superficie))
    r_f, r_p = _resolver_r_f_r_p(est, tab)
    r_s = _coef("r_s", "Tabela C.7", tab.R_S[est.tipo_construcao],
                rotulo(est.tipo_construcao))
    L_F_val = _resolver_L_F(est, tab)
    P_TA = _coef("P_TA", "Tabela B.1", tab.P_TA[zona.medidas.protecao_toque_passo],
                 rotulo(zona.medidas.protecao_toque_passo))
    P_B_val = 1.0 if est.nivel_spda is None else tab.P_B[est.nivel_spda]
    P_B = _coef("P_B", "Tabela B.2", P_B_val,
                "sem SPDA" if est.nivel_spda is None else rotulo(est.nivel_spda))

    mz = MemoriaZona(nome=zona.nome, n_z=zona.n_z, t_z=zona.t_z,
                     coefs={"r_t": r_t, "r_p": r_p, "r_f": r_f, "r_s": r_s,
                            "P_TA": P_TA, "P_B": P_B})

    L_O = _resolver_L_O(est)
    mz.presenca = _op("presenca", "C.6",
                      {"n_z": zona.n_z, "n_t": est.n_t, "t_z": zona.t_z},
                      perdas._presenca)
    mz.L_A = _op("L_A", "C.1",
                 {"r_t": r_t.resultado, "L_T": ref.L_T, "n_z": zona.n_z,
                  "n_t": est.n_t, "t_z": zona.t_z, "r_s": r_s.resultado},
                 perdas.L_choque)
    mz.L_B = _op("L_B", "C.3",
                 {"r_p": r_p.resultado, "r_f": r_f.resultado, "h_z": zona.h_z,
                  "L_F": L_F_val, "n_z": zona.n_z, "n_t": est.n_t,
                  "t_z": zona.t_z, "r_s": r_s.resultado}, perdas.L_fisico)
    mz.L_sis = _op("L_sis", "C.4",
                   {"L_O": L_O, "n_z": zona.n_z, "n_t": est.n_t, "t_z": zona.t_z,
                    "r_s": r_s.resultado}, perdas.L_sistemas)

    tem_l3 = zona.c_z is not None and est.c_t is not None and est.c_t > 0
    if tem_l3:
        mz.L_B3 = _op("L_B3", "C.7",
                      {"r_p": r_p.resultado, "r_f": r_f.resultado,
                       "L_F": ref.L_F_L3, "c_z": zona.c_z, "c_t": est.c_t},
                      perdas.L3_patrimonio)
    tem_l4 = est.c_t is not None and est.c_t > 0
    if tem_l4:
        # L4 tem tabela propria (C.12): L_F/L_O NAO sao os de L1.
        L_F_L4_val = _resolver_L_F_L4(est)
        L_O_L4_val = _resolver_L_O_L4(est)
        if projeto.r4_representativo:
            # R_T representativo (Tabela 4) -> razoes c/c_t = 1 (nota Eqs D.1-D.4).
            org = "R_T representativo (Tabela 4) -> razao = 1 (nota Eqs D.1-D.4)"
            # Tabela C.12: L_T so onde ha animais (c_a > 0); sem animais D1 = 0.
            tem_animais = bool(zona.c_a)
            if tem_animais:
                mz.L4_A = _op("L4_A", "D.1",
                              {"r_t": r_t.resultado, "L_T": ref.L_T},
                              perdas.L4_choque,
                              valor=perdas.L4_choque(r_t.resultado, ref.L_T,
                                                     representativo=True),
                              origem=org)
            else:
                mz.L4_A = Operacao(
                    simbolo="L4_A", eq="D.1", operandos={}, resultado=0.0,
                    origem="sem animais na zona -> L_T nao se aplica "
                           "(Tabela C.12) -> L4_A = 0")
            mz.L4_B = _op("L4_B", "D.3",
                          {"r_p": r_p.resultado, "r_f": r_f.resultado,
                           "L_F": L_F_L4_val}, perdas.L4_fisico,
                          valor=perdas.L4_fisico(r_p.resultado, r_f.resultado,
                                                 L_F_L4_val, representativo=True),
                          origem=org)
            mz.L4_sis = _op("L4_sis", "D.4", {"L_O": L_O_L4_val},
                            perdas.L4_sistemas,
                            valor=perdas.L4_sistemas(L_O_L4_val,
                                                     representativo=True),
                            origem=org)
        else:
            mz.L4_A = _op("L4_A", "D.1",
                          {"r_t": r_t.resultado, "L_T": ref.L_T,
                           "c_a": zona.c_a or 0.0, "c_t": est.c_t},
                          perdas.L4_choque)
            mz.L4_B = _op("L4_B", "D.3",
                          {"r_p": r_p.resultado, "r_f": r_f.resultado,
                           "L_F": L_F_L4_val, "c_a": zona.c_a or 0.0,
                           "c_b": zona.c_b or 0.0, "c_c": zona.c_c or 0.0,
                           "c_s": zona.c_s or 0.0, "c_t": est.c_t},
                          perdas.L4_fisico)
            mz.L4_sis = _op("L4_sis", "D.4",
                            {"L_O": L_O_L4_val, "c_s": zona.c_s or 0.0,
                             "c_t": est.c_t}, perdas.L4_sistemas)

    # --- sistemas internos: P_SPD por sistema, P_C_i, P_MS_i ---
    sistemas_calc = []   # dicts leves p/ reusar nas linhas (P_SPD por sistema)
    P_C_list, P_M_list = [], []
    for sis in zona.sistemas_internos:
        P_SPD_val = 1.0 if sis.dps is None else tab.P_SPD[sis.dps]
        k_s4_val = (sis.K_S4 if sis.K_S4 is not None
                    else (pr.fator_KS4(sis.U_W) if sis.U_W is not None else 1.0))
        if sis.U_W is None:
            P_MS_val = 1.0
        else:
            P_MS_val = pr.P_MS(sis.K_S1, sis.K_S2, sis.K_S3, k_s4_val)
        P_C_val = pr.P_C(P_SPD_val, _C_LD_zona(est))
        k_s4_origem = ("informado" if sis.K_S4 is not None
                       else "1/U_W" if sis.U_W is not None
                       else "default 1.0")
        if sis.U_W is None:
            p_ms_op = _coef("P_MS", "B.4", P_MS_val,
                            "U_W desconhecido -> 1 (pior caso)")
        else:
            p_ms_op = _op("P_MS", "B.4",
                          {"K_S1": sis.K_S1, "K_S2": sis.K_S2, "K_S3": sis.K_S3,
                           "K_S4": k_s4_val}, pr.P_MS, valor=P_MS_val)
        ms = MemoriaSistemaInterno(
            nome=sis.nome, U_W=sis.U_W,
            dps=None if sis.dps is None else rotulo(sis.dps),
            K_S1=_coef("K_S1", "Tabela B.5", sis.K_S1, "informado"),
            K_S2=_coef("K_S2", "Tabela B.5", sis.K_S2, "informado"),
            K_S3=_coef("K_S3", "Tabela B.5", sis.K_S3, "informado"),
            K_S4=_coef("K_S4", "Tabela B.5", k_s4_val, k_s4_origem),
            P_SPD=_coef("P_SPD", "Tabela B.3", P_SPD_val,
                        "sem DPS" if sis.dps is None else rotulo(sis.dps)),
            P_MS_i=p_ms_op,
            P_C_i=_op("P_C", "B.2",
                      {"P_SPD": P_SPD_val, "C_LD": _C_LD_zona(est)}, pr.P_C),
        )
        mz.sistemas.append(ms)
        # P_M = P_SPD*P_MS com DPS coordenado (B.4.9); sem DPS -> P_SPD=1 -> P_MS
        # (B.4.8). U_W desconhecido -> P_M=1 (B.4.10), sem credito de P_SPD.
        P_M_i = P_MS_val if sis.U_W is None else P_SPD_val * P_MS_val
        sistemas_calc.append({"P_SPD": P_SPD_val})
        P_C_list.append(P_C_val)
        P_M_list.append(P_M_i)
    P_C_comb = pr.combinar_sistemas(P_C_list)
    P_M_comb = pr.combinar_sistemas(P_M_list)
    mz.P_A = _op("P_A", "B.1", {"P_TA": P_TA.resultado, "P_B": P_B.resultado}, pr.P_A)
    mz.P_C = Operacao(simbolo="P_C", eq="eq.12", operandos={}, resultado=P_C_comb,
                      origem="1 - prod(1 - P_C_i) sobre sistemas")
    mz.P_M = Operacao(simbolo="P_M", eq="eq.13", operandos={}, resultado=P_M_comb,
                      origem="1 - prod(1 - P_M_i) sobre sistemas; "
                             "P_M_i = P_SPD x P_MS (B.4.9)")

    # --- componentes na/proximo da estrutura ---
    mz.R_A = _op("R_A", "eq.3", {"N": N_D, "P": mz.P_A.resultado,
                                 "L": mz.L_A.resultado}, componentes.componente)
    mz.R_B = _op("R_B", "eq.4", {"N": N_D, "P": P_B.resultado,
                                 "L": mz.L_B.resultado}, componentes.componente)
    mz.R_C = _op("R_C", "eq.5", {"N": N_D, "P": P_C_comb,
                                 "L": mz.L_sis.resultado}, componentes.componente)
    mz.R_M = _op("R_M", "eq.6", {"N": N_M, "P": P_M_comb,
                                 "L": mz.L_sis.resultado}, componentes.componente)
    if tem_l3:
        mz.R_B3 = _op("R_B3", "L3", {"N": N_D, "P": P_B.resultado,
                                     "L": mz.L_B3.resultado},
                      componentes.componente)

    # --- componentes na/proximo da linha ---
    _uws = [s.U_W for s in zona.sistemas_internos]
    uw_min = None if (not _uws or any(u is None for u in _uws)) else min(_uws)
    uw_label = (f"{_UW_CONSERVADOR_KV:g} kV (conservador)" if uw_min is None
                else f"{uw_min} kV")
    R_U = R_V = R_W = R_Z = 0.0
    R_V3 = 0.0
    R4_total = 0.0
    if tem_l4:
        R4_total += (
            componentes.componente(N_D, mz.P_A.resultado, mz.L4_A.resultado)
            + componentes.componente(N_D, P_B.resultado, mz.L4_B.resultado)
            + componentes.componente(N_D, P_C_comb, mz.L4_sis.resultado)
            + componentes.componente(N_M, P_M_comb, mz.L4_sis.resultado))
    # F_B so quando ha equipamento em ZPR 0A (Tabela 7, nota a).
    F_B_val = (frequencia.F_B(N_D, P_B.resultado)
               if any(s.em_zpr0a for s in zona.sistemas_internos) else 0.0)
    F_zona_val = (F_B_val + frequencia.F_C(N_D, P_C_comb)
                  + frequencia.F_M(N_M, P_M_comb))
    for linha in est.linhas:
        ml = _mem_linha(projeto, linha, uw_min, sistemas_calc, uw_label, tab)
        mz_trechos = [(t.N_L.resultado,
                       t.N_DJ.resultado if t.N_DJ is not None else 0.0)
                      for t in ml.trechos]
        R_U += componentes.R_linha(mz_trechos, ml.P_U.resultado, mz.L_A.resultado)
        R_V += componentes.R_linha(mz_trechos, ml.P_V.resultado, mz.L_B.resultado)
        R_W += componentes.R_linha(mz_trechos, ml.P_W.resultado, mz.L_sis.resultado)
        R_Z += componentes.componente(ml.N_I_total, ml.P_Z.resultado,
                                      mz.L_sis.resultado)
        if tem_l3:
            R_V3 += componentes.R_linha(mz_trechos, ml.P_V.resultado,
                                        mz.L_B3.resultado)
        if tem_l4:
            R4_total += (
                componentes.R_linha(mz_trechos, ml.P_U.resultado, mz.L4_A.resultado)
                + componentes.R_linha(mz_trechos, ml.P_V.resultado,
                                      mz.L4_B.resultado)
                + componentes.R_linha(mz_trechos, ml.P_W.resultado,
                                      mz.L4_sis.resultado)
                + componentes.componente(ml.N_I_total, ml.P_Z.resultado,
                                         mz.L4_sis.resultado))
        # Tabela 7: F_V = (N_L + N_DJ) x P_EB (nao P_V).
        F_zona_val += (frequencia.F_V(ml.N_L_total, ml.P_EB.resultado)
                       + frequencia.F_W(ml.N_L_total, ml.P_W.resultado)
                       + frequencia.F_Z(ml.N_I_total, ml.P_Z.resultado))
        mz.linhas.append(ml)

    mz.R_U = Operacao(simbolo="R_U", eq="eq.8", operandos={}, resultado=R_U,
                      origem="soma sobre linhas/trechos")
    mz.R_V = Operacao(simbolo="R_V", eq="eq.9", operandos={}, resultado=R_V,
                      origem="soma sobre linhas/trechos")
    mz.R_W = Operacao(simbolo="R_W", eq="eq.10", operandos={}, resultado=R_W,
                      origem="soma sobre linhas/trechos")
    mz.R_Z = Operacao(simbolo="R_Z", eq="eq.11", operandos={}, resultado=R_Z,
                      origem="soma sobre linhas (N_I)")
    if tem_l3:
        mz.R_V3 = Operacao(simbolo="R_V3", eq="L3", operandos={}, resultado=R_V3,
                           origem="soma sobre linhas/trechos")
    if tem_l4:
        mz.R4_total = Operacao(simbolo="R4_total", eq="13.3", operandos={},
                               resultado=R4_total, origem="soma D1+D2+D3 (L4)")
    mz.F_zona = Operacao(simbolo="F_zona", eq="Secao 7", operandos={},
                         resultado=F_zona_val,
                         origem="F_B+F_C+F_M+F_V+F_W+F_Z (F_V com P_EB; F_B "
                                "so com equipamento em ZPR 0A)")
    return mz


def _C_LD_zona(est: Estrutura) -> float:
    """C_LD usado em P_C por zona. Default conservador 1.0."""
    # TODO: refinar associando C_LD a linha conectada ao sistema; 1.0 e o
    # pior caso conservador ate la.
    return 1.0


def _mem_estrutura(projeto: Projeto, est: Estrutura,
                   tab: Tabelas) -> MemoriaEstrutura:
    eventos_est = _mem_eventos_estrutura(projeto, est, tab)
    A_D, C_D, N_D, A_M, N_M = eventos_est
    zonas = [_mem_zona(projeto, est, z, eventos_est, tab) for z in est.zonas]

    # D3 entra em R1 com explosao, sistemas criticos ou hospital (Tabela C.2
    # preve L_O para "outras partes de hospital").
    incluir_d3 = (_tem_explosao(est) or est.sistemas_criticos
                  or est.ocupacao is TipoOcupacao.hospital)
    me = MemoriaEstrutura(
        nome=est.nome,
        ft=_ft_estrutura(projeto, est, tab),
        entradas={
            "L": est.L, "W": est.W, "H": est.H,
            "localizacao": rotulo(est.localizacao),
            "tipo_construcao": rotulo(est.tipo_construcao),
            "risco_incendio": rotulo(est.risco_incendio),
            "providencias_incendio": rotulo(est.providencias_incendio),
            "ocupacao": rotulo(est.ocupacao),
            "zona_explosao": rotulo(est.zona_explosao),
            "risco_explosao": est.risco_explosao,
            "sistemas_criticos": est.sistemas_criticos,
            "nivel_spda": None if est.nivel_spda is None else rotulo(est.nivel_spda),
            "n_t": est.n_t, "c_t": est.c_t,
        },
        A_D=A_D, C_D=C_D, N_D=N_D, A_M=A_M, N_M=N_M,
        zonas=zonas,
    )

    r1_parcelas = {c: sum(getattr(z, c).resultado for z in zonas)
                   for c in ("R_A", "R_B", "R_U", "R_V")}
    if incluir_d3:
        for c in ("R_C", "R_M", "R_W", "R_Z"):
            r1_parcelas[c] = sum(getattr(z, c).resultado for z in zonas)
    R1_val = sum(r1_parcelas.values())
    R3_val = sum((z.R_B3.resultado if z.R_B3 else 0.0)
                 + (z.R_V3.resultado if z.R_V3 else 0.0) for z in zonas)
    R4_val = sum(z.R4_total.resultado if z.R4_total else 0.0 for z in zonas)
    F_val = sum(z.F_zona.resultado for z in zonas)

    me.R1 = Operacao(simbolo="R1", eq="Secao 8", operandos=r1_parcelas,
                     resultado=R1_val, origem="soma das parcelas por zona")
    me.R3 = Operacao(simbolo="R3", eq="Secao 8", operandos={}, resultado=R3_val,
                     origem="soma (R_B3+R_V3)")
    me.R4 = Operacao(simbolo="R4", eq="Secao 8", operandos={}, resultado=R4_val,
                     origem="soma R4_total")
    me.F = Operacao(simbolo="F", eq="Secao 7", operandos={}, resultado=F_val,
                    origem="soma F_zona")
    me.dominantes = sorted(r1_parcelas.items(), key=lambda kv: kv[1], reverse=True)
    return me


# ---------------------------------------------------------------------------
# Projecao do Resultado enxuto a partir da Memoria
# ---------------------------------------------------------------------------

def _projetar_zona(mz: MemoriaZona) -> ResultadoZona:
    rz = ResultadoZona(nome=mz.nome)
    for c in ("R_A", "R_B", "R_C", "R_M", "R_U", "R_V", "R_W", "R_Z"):
        setattr(rz, c, getattr(mz, c).resultado)
    rz.R_B3 = mz.R_B3.resultado if mz.R_B3 else 0.0
    rz.R_V3 = mz.R_V3.resultado if mz.R_V3 else 0.0
    rz.R4_total = mz.R4_total.resultado if mz.R4_total else 0.0
    rz.F_zona = mz.F_zona.resultado
    return rz


def _projetar_estrutura(me: MemoriaEstrutura,
                        rt: dict[str, float]) -> ResultadoEstrutura:
    # N_DJ e zona-independente; toma das linhas da primeira zona (se houver).
    linhas0 = me.zonas[0].linhas if me.zonas else []
    N_DJ = sum(t.N_DJ.resultado for l in linhas0 for t in l.trechos
               if t.N_DJ is not None)
    return ResultadoEstrutura(
        nome=me.nome, N_D=me.N_D.resultado, N_M=me.N_M.resultado, N_DJ=N_DJ,
        R1=me.R1.resultado, R3=me.R3.resultado, R4=me.R4.resultado,
        F=me.F.resultado, ft=me.ft,
        excede_R1=riscos.excede(me.R1.resultado, rt["R1"]),
        excede_R3=riscos.excede(me.R3.resultado, rt["R3"]),
        excede_R4=riscos.excede(me.R4.resultado, rt["R4"]),
        excede_F=riscos.excede(me.F.resultado, me.ft),
        dominantes=me.dominantes,
        zonas=[_projetar_zona(z) for z in me.zonas],
    )


def _projetar_resultado(mem: Memoria) -> Resultado:
    estruturas = [_projetar_estrutura(me, mem.rt) for me in mem.estruturas]
    return Resultado(projeto=mem.projeto, rt=mem.rt, estruturas=estruturas)


def analisar(projeto: Projeto, config: str | None = None) -> Resultado:
    return _projetar_resultado(analisar_memoria(projeto, config))

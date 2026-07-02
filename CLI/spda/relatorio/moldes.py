# spda/relatorio/moldes.py
"""Catalogo de moldes simbolicos EXECUTAVEIS + renderizacao de Operacao.

Cada molde e uma funcao operandos -> str que devolve a EXPRESSAO PYTHON do lado
direito da equacao (mesma algebra das funcoes de calc/). Isso permite:
1. substituicao para o memorial (troca nomes por numeros);
2. um teste de consistencia que da eval() na expressao com os operandos gravados e
   compara com o resultado -- garante que o molde espelha calc/ (garantia ART).

Quantidades agregadas (R_U..R_Z, R1, P_W/P_Z combinados, P_C de zona) e lookups de
tabela (coeficientes, K_S*, P_SPD) NAO tem molde: sao renderizadas como
`simbolo = valor (origem)`. O criterio de consistencia e: `simbolo in MOLDES and
operandos`.

ATENCAO: ao mexer numa funcao de calc/, ajuste o molde correspondente aqui -- o
teste de consistencia falha se divergirem.
"""
from __future__ import annotations

import math
from typing import Callable

from spda.model.memoria import Operacao
from spda.relatorio.documento import Equacao
from spda.relatorio.formato import fmt, substituir

# Nomes permitidos na avaliacao das formas (alem dos operandos).
EVAL_GLOBAIS = {"__builtins__": {}, "pi": math.pi, "sqrt": math.sqrt,
                "min": min, "max": max}


def _forma_AD(o: dict) -> str:
    # Forma complexa (A.2.1.3.2): max(A_D(H_min) eq A.1, A'_D = pi*(3*H_P)^2 eq A.2).
    if "H_min" in o:
        a = "(L*W + 2*(3*H_min)*(L+W) + pi*(3*H_min)**2)"
        return f"max({a}, pi*(3*H_max)**2)"
    return "L*W + 2*(3*H)*(L+W) + pi*(3*H)**2"


def _forma_AL(o: dict) -> str:
    if "rho" in o and o["rho"] > 400:
        return "0.6*sqrt(rho)*L_L"
    return "40*L_L"


def _forma_presenca(o: dict) -> str:
    if o.get("n_t", 0) == 0:
        return "0"
    return "(n_z/n_t)*(t_z/8760)"


def _forma_L_A(o: dict) -> str:
    return f"r_t*L_T*{_forma_presenca(o)}*r_s"


def _forma_L_B(o: dict) -> str:
    return f"r_p*r_f*h_z*L_F*{_forma_presenca(o)}*r_s"


def _forma_L_sis(o: dict) -> str:
    return f"L_O*{_forma_presenca(o)}*r_s"


# L4: com R_T representativo (norma:2635) as razoes c/c_t viram 1 -- nesse caso
# os operandos c_* nem sao gravados, entao a forma cai para o produto sem razao.
def _forma_L4_A(o: dict) -> str:
    return "r_t*L_T*(c_a/c_t)" if "c_a" in o else "r_t*L_T"


def _forma_L4_B(o: dict) -> str:
    return ("r_p*r_f*L_F*(c_a+c_b+c_c+c_s)/c_t" if "c_a" in o
            else "r_p*r_f*L_F")


def _forma_L4_sis(o: dict) -> str:
    return "L_O*(c_s/c_t)" if "c_s" in o else "L_O"


# Catalogo: simbolo -> (forma_fn). Cada forma_fn devolve a expressao do lado direito.
MOLDES: dict[str, Callable[[dict], str]] = {
    "A_D": _forma_AD,
    "N_D": lambda o: "N_G*A_D*C_D*1e-6",
    "A_M": lambda o: "2*500*(L+W) + pi*500**2",
    "N_M": lambda o: "N_G*A_M*1e-6",
    "A_L": _forma_AL,
    "N_L": lambda o: "N_G*A_L*C_I*C_E*C_T*1e-6",
    "A_I": lambda o: "4000*L_L",
    "N_I": lambda o: "N_G*A_I*C_I*C_E*C_T*1e-6",
    "presenca": _forma_presenca,
    "L_A": _forma_L_A,
    "L_B": _forma_L_B,
    "L_sis": _forma_L_sis,
    "L_B3": lambda o: "min(1.0, r_p*r_f*L_F*(c_z/c_t))",
    "L4_A": _forma_L4_A,
    "L4_B": _forma_L4_B,
    "L4_sis": _forma_L4_sis,
    "P_A": lambda o: "P_TA*P_B",
    "P_MS": lambda o: "(K_S1*K_S2*K_S3*K_S4)**2",
    "P_C": lambda o: "P_SPD*C_LD",
    "P_U": lambda o: "P_TU*P_EB*P_LD*C_LD",
    "P_V": lambda o: "P_EB*P_LD*C_LD",
    "R_A": lambda o: "N*P*L",
    "R_B": lambda o: "N*P*L",
    "R_C": lambda o: "N*P*L",
    "R_M": lambda o: "N*P*L",
    "R_B3": lambda o: "N*P*L",
}


def renderizar_operacao(op: Operacao) -> Equacao:
    """Operacao -> bloco Equacao. Com molde e operandos: mostra substituicao.

    Sem molde (agregado/lookup) ou sem operandos: so simbolo = resultado (origem).
    """
    if op.simbolo in MOLDES and op.operandos:
        forma = MOLDES[op.simbolo](op.operandos)
        return Equacao(
            simbolo=op.simbolo, eq=op.eq,
            forma_simbolica=f"{op.simbolo} = {forma}",
            substituicao=substituir(forma, op.operandos),
            resultado=fmt(op.resultado), origem=op.origem)
    return Equacao(simbolo=op.simbolo, eq=op.eq, forma_simbolica=None,
                   substituicao=None, resultado=fmt(op.resultado),
                   origem=op.origem)

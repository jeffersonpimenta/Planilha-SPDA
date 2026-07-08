"""Glossario de simbolos e indices de equacoes/tabelas, auto-filtrados.

Percorre a Memoria, coleta os simbolos das Operacao presentes e as chaves `eq`
usadas, e emite apenas o que foi efetivamente usado no relatorio. Descricoes e
referencias normativas sao tabelas estaticas (dados).
"""
from __future__ import annotations

from spda.model.memoria import Memoria, Operacao

# simbolo -> (descricao, unidade)
_GLOSSARIO = {
    "N_G": ("densidade de descargas atmosféricas", "1/km2/ano"),
    "A_D": ("área de exposição equivalente da estrutura", "m2"),
    "A_M": ("área de exposição para descargas perto da estrutura", "m2"),
    "A_L": ("área de captação da linha", "m2"),
    "A_I": ("área de exposição para descargas perto da linha", "m2"),
    "C_D": ("fator de localização da estrutura", "-"),
    "C_I": ("fator de instalação da linha", "-"),
    "C_E": ("fator ambiental da linha", "-"),
    "C_T": ("fator de transformador (AT/BT) da linha", "-"),
    "C_LD": ("fator de blindagem/aterramento (dano)", "-"),
    "C_LI": ("fator de blindagem/aterramento (indução)", "-"),
    "N_D": ("descargas diretas na estrutura", "1/ano"),
    "N_M": ("descargas perto da estrutura", "1/ano"),
    "N_DJ": ("descargas na estrutura adjacente", "1/ano"),
    "N_L": ("descargas na linha", "1/ano"),
    "N_I": ("descargas perto da linha", "1/ano"),
    "P_TA": ("prob. de choque por toque/passo (estrutura)", "-"),
    "P_B": ("prob. de dano físico (nível de SPDA)", "-"),
    "P_SPD": ("prob. ligada ao DPS coordenado do sistema", "-"),
    "P_EB": ("prob. ligada à ligação equipotencial na entrada", "-"),
    "P_TU": ("prob. de choque por toque na entrada da linha", "-"),
    "P_LD": ("prob. de falha por surto na linha (dano)", "-"),
    "P_LI": ("prob. de falha por surto induzido na linha", "-"),
    "K_S1": ("fator de blindagem espacial (interface ZPR0/1)", "-"),
    "K_S2": ("fator de blindagem interna", "-"),
    "K_S3": ("fator das características da fiação interna", "-"),
    "K_S4": ("fator da tensão suportável de impulso (1/U_W)", "-"),
    "P_A": ("prob. de choque, descarga na estrutura", "-"),
    "P_C": ("prob. de falha de sistemas, descarga na estrutura", "-"),
    "P_M": ("prob. de falha de sistemas, descarga perto", "-"),
    "P_U": ("prob. de choque por linha", "-"),
    "P_V": ("prob. de dano físico por linha", "-"),
    "P_W": ("prob. de falha de sistemas por surto na linha", "-"),
    "P_Z": ("prob. de falha de sistemas por surto induzido", "-"),
    "P_MS": ("prob. de falha de sistemas internos (campo magnético)", "-"),
    "r_t": ("fator do tipo de superfície (redução de choque)", "-"),
    "r_p": ("fator das providências contra incêndio", "-"),
    "r_f": ("fator do risco de incêndio", "-"),
    "r_s": ("fator do tipo de construção", "-"),
    "L_T": ("perda relativa por choque (valor tipico)", "-"),
    "L_F": ("perda relativa por dano físico (valor tipico)", "-"),
    "L_O": ("perda relativa por falha de sistemas (valor tipico)", "-"),
    "presenca": ("fator de presença de pessoas na zona", "-"),
    "L_A": ("perda por choque (descarga na estrutura)", "-"),
    "L_B": ("perda por dano físico (descarga na estrutura)", "-"),
    "L_sis": ("perda por falha de sistemas internos", "-"),
    "L_B3": ("perda de patrimônio (L3)", "-"),
    "L4_A": ("perda econômica por choque (L4)", "-"),
    "L4_B": ("perda econômica por dano físico (L4)", "-"),
    "L4_sis": ("perda econômica por falha de sistemas (L4)", "-"),
    "R_A": ("componente de risco: choque (estrutura)", "1/ano"),
    "R_B": ("componente de risco: dano físico (estrutura)", "1/ano"),
    "R_C": ("componente de risco: falha de sistemas (estrutura)", "1/ano"),
    "R_M": ("componente de risco: falha de sistemas (perto)", "1/ano"),
    "R_U": ("componente de risco: choque (linha)", "1/ano"),
    "R_V": ("componente de risco: dano físico (linha)", "1/ano"),
    "R_W": ("componente de risco: falha de sistemas (linha)", "1/ano"),
    "R_Z": ("componente de risco: falha de sistemas (indução)", "1/ano"),
    "R_B3": ("componente de R3 (patrimônio)", "1/ano"),
    "R_V3": ("componente de R3 por linha", "1/ano"),
    "R4_total": ("risco econômico da zona (R4)", "1/ano"),
    "F_zona": ("frequência de danos da zona", "1/ano"),
    "R1": ("risco de vida humana", "1/ano"),
    "R3": ("risco de perda de patrimônio cultural", "1/ano"),
    "R4": ("risco de perda econômica", "1/ano"),
    "F": ("frequência de danos da estrutura", "1/ano"),
}

# eq -> (titulo, referencia)
_EQUACOES = {
    "A.1": ("Área de exposição A_D", "Anexo A"),
    "A.1/A.2": ("Área de exposição A_D (forma complexa)", "Anexo A"),
    "A.3": ("Número de eventos N_D", "Anexo A"),
    "A.4": ("Número de eventos N_DJ (adjacente)", "Anexo A"),
    "A.5": ("Número de eventos N_M", "Anexo A"),
    "A.6": ("Área A_M", "Anexo A"),
    "A.7": ("Número de eventos N_L", "Anexo A"),
    "A.8": ("Área da linha A_L", "Anexo A"),
    "A.9": ("Número de eventos N_I", "Anexo A"),
    "A.10": ("Área perto da linha A_I", "Anexo A"),
    "B.1": ("Probabilidade P_A", "Anexo B"),
    "B.2": ("Probabilidade P_C", "Anexo B"),
    "B.4": ("Probabilidade P_MS", "Anexo B"),
    "B.6": ("Probabilidade P_TU", "Anexo B"),
    "B.7": ("Probabilidade P_EB", "Anexo B"),
    "B.8": ("Probabilidade P_U / P_LD", "Anexo B"),
    "B.9": ("Probabilidade P_V / P_LI", "Anexo B"),
    "B.10": ("Probabilidade P_W", "Anexo B"),
    "B.11": ("Probabilidade P_Z", "Anexo B"),
    "C.1": ("Perda L_A", "Anexo C"),
    "C.3": ("Perda L_B", "Anexo C"),
    "C.4": ("Perda L_sis", "Anexo C"),
    "C.6": ("Fator de presença", "Anexo C"),
    "L3": ("Perda de patrimônio (L3)", "Seção 7"),
    "13.3": ("Perdas econômicas (L4)", "Seção 13"),
    "eq.3": ("Componente de risco R = N*P*L", "Seção 8"),
    "eq.4": ("Componente de risco R = N*P*L", "Seção 8"),
    "eq.5": ("Componente de risco R = N*P*L", "Seção 8"),
    "eq.6": ("Componente de risco R = N*P*L", "Seção 8"),
    "eq.8": ("Componente de linha R_U", "Seção 8"),
    "eq.9": ("Componente de linha R_V", "Seção 8"),
    "eq.10": ("Componente de linha R_W", "Seção 8"),
    "eq.11": ("Componente R_Z", "Seção 8"),
    "eq.12": ("Combinação de sistemas (P_C)", "Seção 8"),
    "eq.13": ("Combinação de sistemas (P_M)", "Seção 8"),
    "Seção 8": ("Riscos totais R1/R3/R4", "Seção 8"),
    "Seção 7": ("Frequência de danos F", "Seção 7 (Tabela 7)"),
}

# eq de coeficiente (lookup) -> nome da tabela. Indice de tabelas usa estas.
_TABELAS = {
    "Tabela A.1": "Tabela A.1 (C_D, localização)",
    "Tabela A.2": "Tabela A.2 (C_I, instalação)",
    "Tabela A.3": "Tabela A.3 (C_T, transformador)",
    "Tabela A.4": "Tabela A.4 (C_E, ambiente)",
    "Tabela B.1": "Tabela B.1 (P_TA)",
    "Tabela B.2": "Tabela B.2 (P_B)",
    "Tabela B.3": "Tabela B.3 (P_SPD)",
    "Tabela B.4": "Tabela B.4 (C_LD/C_LI)",
    "Tabela B.5": "Tabela B.5 (K_S3)",
    "Tabela B.6": "Tabela B.6 (P_TU)",
    "Tabela B.7": "Tabela B.7 (P_EB)",
    "Tabela B.8": "Tabela B.8 (P_LD)",
    "Tabela B.9": "Tabela B.9 (P_LI)",
    "Tabela C.7": "Tabela C.7 (r_s)",
    "Tabela C.3": "Tabela C.3 (r_t)",
    "Tabela C.4": "Tabela C.4 (r_p)",
    "Tabela C.5": "Tabela C.5 (r_f)",
}


def _coletar_operacoes(mem: Memoria) -> list[Operacao]:
    achados: list[Operacao] = []

    def visita(obj):
        if isinstance(obj, Operacao):
            achados.append(obj)
            return
        if isinstance(obj, dict):
            for v in obj.values():
                visita(v)
            return
        if isinstance(obj, (list, tuple)):
            for v in obj:
                visita(v)
            return
        campos = getattr(obj, "__dict__", None)
        if campos:
            for v in campos.values():
                visita(v)

    visita(mem)
    return achados


def simbolos_usados(mem: Memoria) -> list[tuple[str, str, str]]:
    """(simbolo, descricao, unidade) para cada simbolo presente, ordenado."""
    presentes = {op.simbolo for op in _coletar_operacoes(mem)}
    itens = []
    for simbolo in sorted(presentes):
        if simbolo in _GLOSSARIO:
            nome, unidade = _GLOSSARIO[simbolo]
            itens.append((simbolo, nome, unidade))
    return itens


def indice_equacoes(mem: Memoria) -> list[list[str]]:
    """(eq, titulo, referencia) para cada eq nao-tabela presente, ordenado."""
    eqs = {op.eq for op in _coletar_operacoes(mem)
           if not op.eq.startswith("Tabela")}
    linhas = []
    for eq in sorted(eqs):
        titulo, ref = _EQUACOES.get(eq, (eq, ""))
        linhas.append([eq, titulo, ref])
    return linhas


def indice_tabelas(mem: Memoria) -> list[list[str]]:
    """(tabela, coeficiente, referencia) para cada lookup de tabela presente."""
    vistos = {}
    for op in _coletar_operacoes(mem):
        if op.eq.startswith("Tabela") and op.eq not in vistos:
            vistos[op.eq] = op.simbolo
    linhas = []
    for eq in sorted(vistos):
        linhas.append([eq, vistos[eq], _TABELAS.get(eq, eq)])
    return linhas

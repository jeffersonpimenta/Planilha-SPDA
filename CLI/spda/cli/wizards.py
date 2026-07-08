"""Wizards: constroem modelos pydantic a partir de um Prompter (puro, sem I/O).

A ordem das perguntas do modo *criacao* (build_*) e fixa e deve ser mantida em
sincronia com os testes (FakePrompter alimenta respostas nessa ordem). Uma GUI
futura reusa estas funcoes injetando outro Prompter.

Os campos escalares de cada entidade sao extraidos em helpers `_campos_*` que
aceitam `atual` (o modelo em edicao) e pre-preenchem os `default=` dos prompts.
Com `atual=None` o comportamento e identico ao de criacao. As funcoes `editar_*`
reusam esses helpers, adicionam prompts de campos avancados (`_avancado_*`) que a
criacao deixa no default, e gerenciam colecoes aninhadas via `_gerenciar`.
Campos preservados (nao perguntados) sobrevivem via `model_copy(update=...)`.
"""
from __future__ import annotations

from spda.cli.prompts import Prompter
from spda.model.enums import (
    AmbienteLinha, CategoriaLinha, ClasseBlindagemRS, FiacaoInterna,
    InstalacaoLinha, Localizacao, NivelDPS, NivelProtecao, PerigoEspecial,
    ProtecaoToquePasso, ProvidenciaIncendio, RelevanciaAD, RiscoIncendio,
    TipoConstrucao, TipoLinha, TipoLinhaExterna, TipoOcupacao, TipoSuperficie,
    ZonaExplosao,
)
from spda.model.identificacao import Identificacao
from spda.model.projeto import (
    Estrutura, EstruturaAdjacente, Linha, Medidas, Projeto, SistemaInterno,
    Trecho, Zona,
)
from spda.tabelas import referencia as ref

# API publica: os builders de entidade + as funcoes de edicao. build_medidas/
# build_adjacente e os helpers _campos_*/_avancado_* sao auxiliares.
__all__ = [
    "build_trecho", "build_linha", "build_zona", "build_estrutura",
    "build_projeto",
    "editar_trecho", "editar_sistema", "editar_linha", "editar_zona",
    "editar_estrutura",
]


# ---------------------------------------------------------------------------
# Gerenciador generico de colecao aninhada (usado so na edicao)
# ---------------------------------------------------------------------------
def _gerenciar(p: Prompter, itens: list, nome_fn, editar_fn, criar_fn,
               singular: str, minimo: int = 0) -> list:
    """Sub-menu para adicionar/remover/editar itens de uma colecao.

    A propria lista de escolhas ja e a "listagem". Selecao por rotulo indexado
    ("1. nome") evita ambiguidade quando nomes se repetem. Muta e devolve
    `itens` (passe uma copia se nao quiser efeito colateral).
    """
    while True:
        rotulos = [f"{i + 1}. {nome_fn(x)}" for i, x in enumerate(itens)]
        opcoes = list(rotulos)
        opcoes.append(f"+ Adicionar {singular}")
        if len(itens) > minimo:
            opcoes.append(f"- Remover {singular}")
        opcoes.append("Concluir")
        esc = p.selecionar(f"Gerenciar {singular}(s)", opcoes)
        if esc == "Concluir":
            return itens
        if esc.startswith("+ "):
            itens.append(criar_fn(p))
        elif esc.startswith("- "):
            alvo = p.selecionar(f"Remover qual {singular}?", rotulos)
            del itens[rotulos.index(alvo)]
        else:
            idx = rotulos.index(esc)
            itens[idx] = editar_fn(p, itens[idx])


# ---------------------------------------------------------------------------
# Trecho
# ---------------------------------------------------------------------------
def _campos_trecho(p: Prompter, atual: Trecho | None = None) -> dict:
    L_L = p.numero("Comprimento do trecho L_L (m)",
                   default=atual.L_L if atual else 1000.0, minimo=0.001)
    tem_rho = atual is not None and atual.rho is not None
    if p.confirmar("Linha enterrada com resistividade do solo conhecida?", tem_rho):
        rho = p.numero("Resistividade rho (ohm*m)",
                       default=atual.rho if tem_rho else 500.0, minimo=0.001)
    else:
        rho = None
    return {"L_L": L_L, "rho": rho}


def _avancado_trecho(p: Prompter, atual: Trecho) -> dict:
    return {
        "instalacao": p.opcao_opcional(
            "Override de instalação do trecho (opcional)", InstalacaoLinha,
            atual.instalacao),
        "ambiente": p.opcao_opcional(
            "Override de ambiente do trecho (opcional)", AmbienteLinha,
            atual.ambiente),
        "tipo": p.opcao_opcional(
            "Override de tipo do trecho (opcional)", TipoLinha, atual.tipo),
    }


def build_trecho(p: Prompter) -> Trecho:
    return Trecho(**_campos_trecho(p))


def editar_trecho(p: Prompter, atual: Trecho) -> Trecho:
    return atual.model_copy(update={**_campos_trecho(p, atual),
                                    **_avancado_trecho(p, atual)})


# ---------------------------------------------------------------------------
# Sistema interno
# ---------------------------------------------------------------------------
def _campos_sistema(p: Prompter, atual: SistemaInterno | None = None) -> dict:
    nome = p.texto("Nome do sistema interno",
                   default=atual.nome if atual else "Sistema 1")
    # Travado nas colunas tabeladas de U_W (Tabela B.9): 1, 1.5, 2.5, 4, 6 kV.
    U_W = p.numero_tabelado("Tensão suportável de impulso U_W (kV)",
                            list(ref.COLUNAS_UW),
                            default=atual.U_W if (atual and atual.U_W is not None)
                            else 2.5,
                            tabela="Tabela B.8/B.9 - P_LD/P_LI por U_W")
    K_S1 = p.numero("Fator de blindagem K_S1 (interface ZPR0/1)",
                    default=atual.K_S1 if atual else 1.0, minimo=0)
    K_S2 = p.numero("Fator de blindagem interna K_S2",
                    default=atual.K_S2 if atual else 1.0, minimo=0)
    # K_S3 e armazenado ja resolvido; para o default da edicao fazemos o
    # lookup reverso na Tabela B.5 (None se nao casar exatamente).
    fiacao_default = FiacaoInterna.laco_grande
    if atual is not None:
        fiacao_default = next(
            (f for f in FiacaoInterna if ref.K_S3[f] == atual.K_S3),
            FiacaoInterna.laco_grande)
    fiacao = p.opcao("Fiação interna (K_S3)", FiacaoInterna, fiacao_default)
    dps = p.opcao_opcional(
        "NP do DPS coordenado deste sistema (P_SPD)", NivelDPS,
        atual.dps if atual else None,
        tabela="Tabela B.3 - Probabilidade P_SPD")
    em_zpr0a = p.confirmar(
        "Equipamento exposto em ZPR 0A (isolado/topo da estrutura)? Soma F_B "
        "na frequência de danos",
        atual.em_zpr0a if atual else False,
        tabela="Tabela 7, nota a - fator F_B")
    return {"nome": nome, "U_W": U_W, "K_S1": K_S1, "K_S2": K_S2,
            "K_S3": ref.K_S3[fiacao], "dps": dps, "em_zpr0a": em_zpr0a}


def _avancado_sistema(p: Prompter, atual: SistemaInterno) -> dict:
    tem = atual.K_S4 is not None
    if p.confirmar("Sobrepor fator K_S4 (senão derivado de U_W)?", tem):
        return {"K_S4": p.numero("Fator K_S4",
                                 default=atual.K_S4 if tem else 1.0, minimo=0)}
    return {"K_S4": None}


def build_sistema_interno(p: Prompter) -> SistemaInterno:
    return SistemaInterno(**_campos_sistema(p))


def editar_sistema(p: Prompter, atual: SistemaInterno) -> SistemaInterno:
    return atual.model_copy(update={**_campos_sistema(p, atual),
                                    **_avancado_sistema(p, atual)})


# ---------------------------------------------------------------------------
# Medidas / Estrutura adjacente
# ---------------------------------------------------------------------------
def build_medidas(p: Prompter, atual: Medidas | None = None) -> Medidas:
    tp = p.opcao("Proteção contra tensão de toque/passo (P_TA)",
                 ProtecaoToquePasso,
                 atual.protecao_toque_passo if atual else ProtecaoToquePasso.nenhuma,
                 tabela="Tabela B.1 - Probabilidade P_TA")
    return Medidas(protecao_toque_passo=tp)


def build_adjacente(p: Prompter,
                    atual: EstruturaAdjacente | None = None) -> EstruturaAdjacente:
    L_J = p.numero("L da estrutura adjacente (m)",
                   default=atual.L_J if atual else 10.0, minimo=0.001)
    W_J = p.numero("W da estrutura adjacente (m)",
                   default=atual.W_J if atual else 10.0, minimo=0.001)
    H_J = p.numero("H da estrutura adjacente (m)",
                   default=atual.H_J if atual else 3.0, minimo=0.001)
    loc = p.opcao("Localização da estrutura adjacente", Localizacao,
                  atual.localizacao_J if atual else Localizacao.isolada)
    return EstruturaAdjacente(L_J=L_J, W_J=W_J, H_J=H_J, localizacao_J=loc)


# ---------------------------------------------------------------------------
# Zona
# ---------------------------------------------------------------------------
def _campos_zona_basico(p: Prompter, atual: Zona | None = None) -> dict:
    nome = p.texto("Nome da zona", default=atual.nome if atual else "Zona 1")
    superficie = p.opcao("Tipo de superfície (r_t)", TipoSuperficie,
                         atual.superficie if atual else TipoSuperficie.terra_concreto)
    n_z = p.inteiro("Número de pessoas na zona (n_z)",
                    default=atual.n_z if atual else 1, minimo=0)
    t_z = p.numero("Horas/ano de presença (t_z)",
                   default=atual.t_z if atual else 8760.0, minimo=0, maximo=8760)
    medidas = build_medidas(p, atual.medidas if atual else None)
    return {"nome": nome, "superficie": superficie, "n_z": n_z, "t_z": t_z,
            "medidas": medidas}


def _campos_zona_patrimonio(p: Prompter, atual: Zona | None = None) -> dict:
    tem = atual is not None and atual.c_z is not None
    if not p.confirmar("Incluir dados de patrimônio/econômico (R3/R4)?", tem):
        return {"c_z": None, "c_a": None, "c_b": None, "c_c": None, "c_s": None}
    d = atual if tem else None
    return {
        "c_z": p.numero("Valor de patrimônio na zona c_z",
                        default=d.c_z if d else 0.0, minimo=0),
        "c_a": p.numero("Valor de animais/pessoas c_a",
                        default=d.c_a if (d and d.c_a is not None) else 0.0, minimo=0),
        "c_b": p.numero("Valor da edificação c_b",
                        default=d.c_b if (d and d.c_b is not None) else 0.0, minimo=0),
        "c_c": p.numero("Valor do conteúdo c_c",
                        default=d.c_c if (d and d.c_c is not None) else 0.0, minimo=0),
        "c_s": p.numero("Valor dos sistemas internos c_s",
                        default=d.c_s if (d and d.c_s is not None) else 0.0, minimo=0),
    }


def _avancado_zona(p: Prompter, atual: Zona) -> dict:
    # h_z NAO e altura: e o fator de perigo especial da Tabela C.6 (1/2/5/10).
    # Lookup reverso do valor atual para o default do enum (5 e ambiguo:
    # panico_medio vence, mas o valor resolvido e o mesmo).
    perigo_default = next(
        (pe for pe in PerigoEspecial if ref.H_Z[pe] == atual.h_z),
        PerigoEspecial.sem_perigo)
    perigo = p.opcao("Perigo especial da zona (h_z, Tabela C.6)",
                     PerigoEspecial, perigo_default)
    relevancia = p.opcao("Relevância da área de captação (relevancia_AD)",
                         RelevanciaAD, atual.relevancia_AD)
    return {"h_z": ref.H_Z[perigo], "relevancia_AD": relevancia}


def build_zona(p: Prompter) -> Zona:
    campos = _campos_zona_basico(p)
    sistemas = []
    # 1a pergunta default=sim: incentiva inserir >=1 sistema (risco R_C/R_M
    # existe mesmo sem linha). Repeticoes default=nao p/ nao forcar laco.
    primeiro = True
    while p.confirmar("Adicionar sistema interno (R_C/R_M/R_W/R_Z)?", primeiro):
        sistemas.append(build_sistema_interno(p))
        primeiro = False
    patrimonio = _campos_zona_patrimonio(p)
    return Zona(**campos, sistemas_internos=sistemas, **patrimonio)


def editar_zona(p: Prompter, atual: Zona) -> Zona:
    campos = {**_campos_zona_basico(p, atual),
              **_campos_zona_patrimonio(p, atual),
              **_avancado_zona(p, atual)}
    sistemas = _gerenciar(p, list(atual.sistemas_internos), lambda s: s.nome,
                          editar_sistema, build_sistema_interno, "sistema interno")
    return atual.model_copy(update={**campos, "sistemas_internos": sistemas})


# ---------------------------------------------------------------------------
# Linha
# ---------------------------------------------------------------------------
def _campos_linha(p: Prompter, atual: Linha | None = None) -> dict:
    tipo = p.opcao("Tipo de linha (C_T)", TipoLinha,
                   atual.tipo if atual else TipoLinha.bt_sinal)
    categoria = p.opcao("Categoria da linha (P_LI)", CategoriaLinha,
                        atual.categoria if atual else CategoriaLinha.energia)
    instalacao = p.opcao("Instalação da linha", InstalacaoLinha,
                         atual.instalacao if atual else InstalacaoLinha.aerea)
    ambiente = p.opcao("Ambiente da linha", AmbienteLinha,
                       atual.ambiente if atual else AmbienteLinha.rural)
    tipo_externa = p.opcao("Tipo de linha externa (define C_LD/C_LI)",
                           TipoLinhaExterna,
                           atual.tipo_externa if atual else TipoLinhaExterna.aerea_nao_blindada)
    classe_blindagem = p.opcao("Blindagem/RS do cabo (P_LD)", ClasseBlindagemRS,
                               atual.classe_blindagem if atual else ClasseBlindagemRS.nao_blindada)
    nivel_eb = p.opcao_opcional(
        "NP do DPS de equipotencialização na entrada (P_EB)", NivelDPS,
        atual.nivel_eb if atual else None,
        tabela="Tabela B.7 - Probabilidade P_EB")
    protecao_toque_entrada = p.opcao(
        "Proteção contra tensão de toque na entrada (P_TU)",
        ProtecaoToquePasso,
        atual.protecao_toque_entrada if atual else ProtecaoToquePasso.nenhuma,
        tabela="Tabela B.6 - Probabilidade P_TU")
    tem_adj = atual is not None and atual.adjacente is not None
    if p.confirmar("Esta linha conecta a uma estrutura adjacente?", tem_adj):
        adjacente = build_adjacente(p, atual.adjacente if tem_adj else None)
    else:
        adjacente = None
    return {"tipo": tipo, "categoria": categoria, "instalacao": instalacao,
            "ambiente": ambiente, "tipo_externa": tipo_externa,
            "classe_blindagem": classe_blindagem, "nivel_eb": nivel_eb,
            "protecao_toque_entrada": protecao_toque_entrada,
            "adjacente": adjacente}


def build_linha(p: Prompter) -> Linha:
    campos = _campos_linha(p)
    trechos = [build_trecho(p)]
    while p.confirmar("Adicionar outro trecho a esta linha?", False):
        trechos.append(build_trecho(p))
    return Linha(**campos, trechos=trechos)


def editar_linha(p: Prompter, atual: Linha) -> Linha:
    campos = _campos_linha(p, atual)
    trechos = _gerenciar(p, list(atual.trechos), lambda t: f"{t.L_L} m",
                         editar_trecho, build_trecho, "trecho", minimo=1)
    return atual.model_copy(update={**campos, "trechos": trechos})


# ---------------------------------------------------------------------------
# Estrutura
# ---------------------------------------------------------------------------
def _campos_estrutura(p: Prompter, atual: Estrutura | None = None) -> dict:
    nome = p.texto("Nome da estrutura", default=atual.nome if atual else "Estrutura 1")
    L = p.numero("Comprimento L (m)", default=atual.L if atual else 10.0, minimo=0.001)
    W = p.numero("Largura W (m)", default=atual.W if atual else 10.0, minimo=0.001)
    H = p.numero("Altura H (m)", default=atual.H if atual else 3.0, minimo=0.001)
    localizacao = p.opcao("Localização (C_D)", Localizacao,
                          atual.localizacao if atual else Localizacao.isolada)
    tipo_construcao = p.opcao(
        "Tipo de construção (r_s)", TipoConstrucao,
        atual.tipo_construcao if atual else TipoConstrucao.robusta)
    risco_incendio = p.opcao("Risco de incêndio (r_f)", RiscoIncendio,
                             atual.risco_incendio if atual else RiscoIncendio.normal)
    providencias = p.opcao("Providências contra incêndio (r_p)",
                           ProvidenciaIncendio,
                           atual.providencias_incendio if atual else ProvidenciaIncendio.nenhuma)
    ocupacao = p.opcao("Ocupação/uso da estrutura (L_F)", TipoOcupacao,
                       atual.ocupacao if atual else TipoOcupacao.outros)
    zona_explosao = p.opcao(
        "Zona de atmosfera explosiva (r_f; C.3.4 força r_p=1) -- nenhuma se "
        "não houver", ZonaExplosao,
        atual.zona_explosao if atual else ZonaExplosao.nenhuma)
    sistemas_criticos = p.confirmar("Há sistemas internos críticos?",
                                    atual.sistemas_criticos if atual else False)
    nivel_spda = p.opcao_opcional("Nível de SPDA existente (P_B)", NivelProtecao,
                                  atual.nivel_spda if atual else None)
    n_t = p.inteiro("Número total de pessoas na estrutura (n_t)",
                    default=atual.n_t if atual else 1, minimo=1)
    tem_ct = atual is not None and atual.c_t is not None
    if p.confirmar("Informar valor total c_t (necessário para R3/R4)?", tem_ct):
        c_t = p.numero("Valor total c_t", default=atual.c_t if tem_ct else 0.0,
                       minimo=0)
    else:
        c_t = None
    return {"nome": nome, "L": L, "W": W, "H": H, "localizacao": localizacao,
            "tipo_construcao": tipo_construcao, "risco_incendio": risco_incendio,
            "providencias_incendio": providencias, "ocupacao": ocupacao,
            "zona_explosao": zona_explosao, "sistemas_criticos": sistemas_criticos,
            "nivel_spda": nivel_spda, "c_t": c_t, "n_t": n_t}


def _avancado_estrutura(p: Prompter, atual: Estrutura) -> dict:
    tem = atual.H_min is not None
    if p.confirmar("Definir faixa de altura H_min/H_max (forma complexa)?", tem):
        H_min = p.numero("Altura mínima H_min (m)",
                         default=atual.H_min if tem else atual.H, minimo=0.001)
        H_max = p.numero("Altura máxima H_max (m)",
                         default=atual.H_max if atual.H_max is not None else atual.H,
                         minimo=0.001)
    else:
        H_min = H_max = None
    risco_explosao = p.confirmar("Risco de explosão (booleano)?",
                                 atual.risco_explosao)
    return {"H_min": H_min, "H_max": H_max, "risco_explosao": risco_explosao}


def build_estrutura(p: Prompter) -> Estrutura:
    campos = _campos_estrutura(p)
    zonas = [build_zona(p)]
    while p.confirmar("Adicionar outra zona?", False):
        zonas.append(build_zona(p))
    linhas = []
    while p.confirmar("Adicionar uma linha elétrica/sinal?", False):
        linhas.append(build_linha(p))
    return Estrutura(**campos, zonas=zonas, linhas=linhas)


def editar_estrutura(p: Prompter, atual: Estrutura) -> Estrutura:
    campos = {**_campos_estrutura(p, atual), **_avancado_estrutura(p, atual)}
    zonas = _gerenciar(p, list(atual.zonas), lambda z: z.nome,
                       editar_zona, build_zona, "zona", minimo=1)
    linhas = _gerenciar(p, list(atual.linhas), lambda l: l.nome,
                        editar_linha, build_linha, "linha")
    return atual.model_copy(update={**campos, "zonas": zonas, "linhas": linhas})


# ---------------------------------------------------------------------------
# Identificacao / Projeto
# ---------------------------------------------------------------------------
def build_identificacao(p: Prompter) -> Identificacao | None:
    if not p.confirmar("Preencher identificação do laudo (assinatura/ART)?",
                       False):
        return None
    return Identificacao(
        titulo=p.texto("Título do laudo", default="") or None,
        cliente=p.texto("Cliente", default="") or None,
        endereco=p.texto("Endereço", default="") or None,
        responsavel=p.texto("Responsável técnico", default="") or None,
        art=p.texto("Número da ART", default="") or None,
        registro=p.texto("Registro CREA (com UF)", default="") or None,
        data=p.texto("Data do laudo", default="") or None,
        observacoes=p.texto("Observações", default="") or None,
    )


def build_projeto(p: Prompter) -> Projeto:
    nome = p.texto("Nome do projeto", default="Projeto")
    cidade = p.texto("Cidade (município base do N_G)", default="")
    N_G = p.numero(
        "Densidade de descargas N_G (1/km2/ano)",
        default=1.0, minimo=0.001,
        tabela="Anexo E - densidade N_G por municipio")
    r4_representativo = p.confirmar(
        "Avaliar R4 com R_T representativo (1e-3)? "
        "Não = método detalhado do Anexo D (razões c/c_t).", False,
        tabela="Tabela 4 - risco tolerável R_T")
    identificacao = build_identificacao(p)
    estruturas = [build_estrutura(p)]
    while p.confirmar("Adicionar outra estrutura ao projeto?", False):
        estruturas.append(build_estrutura(p))
    return Projeto(nome=nome, cidade=cidade, N_G=N_G,
                   r4_representativo=r4_representativo, estruturas=estruturas,
                   identificacao=identificacao)

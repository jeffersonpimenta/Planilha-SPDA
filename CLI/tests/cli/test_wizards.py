from spda.cli.wizards import (
    build_trecho, build_linha, build_sistema_interno, build_zona,
    build_estrutura, build_projeto, build_identificacao,
    editar_trecho, editar_sistema, editar_zona,
)
from spda.model.enums import (
    Localizacao, TipoConstrucao, RiscoIncendio, ProvidenciaIncendio,
    TipoSuperficie, TipoLinha, InstalacaoLinha, AmbienteLinha,
    TipoLinhaExterna, ProtecaoToquePasso, NivelProtecao, NivelDPS,
    CategoriaLinha, ClasseBlindagemRS, FiacaoInterna, TipoOcupacao, ZonaExplosao,
    RelevanciaAD, PerigoEspecial,
)
from spda.model.projeto import Trecho, SistemaInterno, Zona
from tests.cli.fakes import FakePrompter


def test_build_trecho_sem_rho():
    p = FakePrompter([500.0, False])
    t = build_trecho(p)
    assert t.L_L == 500.0
    assert t.rho is None


def test_build_trecho_com_rho():
    p = FakePrompter([500.0, True, 600.0])
    t = build_trecho(p)
    assert t.rho == 600.0


def test_build_linha_um_trecho():
    p = FakePrompter([
        TipoLinha.bt_sinal, CategoriaLinha.energia, InstalacaoLinha.aerea,
        AmbienteLinha.rural, TipoLinhaExterna.aerea_nao_blindada,
        ClasseBlindagemRS.nao_blindada, None, ProtecaoToquePasso.nenhuma,
        False,                                  # conecta estrutura adjacente? nao
        1000.0, False,
        False,
    ])
    linha = build_linha(p)
    assert linha.tipo == TipoLinha.bt_sinal
    assert linha.categoria == CategoriaLinha.energia
    assert linha.classe_blindagem == ClasseBlindagemRS.nao_blindada
    assert linha.nivel_eb is None
    assert len(linha.trechos) == 1
    assert linha.trechos[0].L_L == 1000.0


def test_build_sistema_interno():
    p = FakePrompter([
        "Sis 1", 6.0, 1.0, 1.0, FiacaoInterna.blindado_conduto, None,
        False,                                  # equipamento em ZPR 0A? nao
    ])
    sis = build_sistema_interno(p)
    assert sis.U_W == 6.0
    assert sis.K_S3 == 0.0001          # lookup Tabela B.5
    assert sis.dps is None
    assert sis.em_zpr0a is False


def test_build_sistema_interno_em_zpr0a():
    # Tabela 7, nota a: equipamento em ZPR 0A soma F_B na frequencia de danos.
    p = FakePrompter([
        "Antena", 2.5, 1.0, 1.0, FiacaoInterna.laco_grande, None,
        True,                                   # equipamento em ZPR 0A? sim
    ])
    sis = build_sistema_interno(p)
    assert sis.em_zpr0a is True


def test_build_zona_sem_economico():
    p = FakePrompter([
        "Zona 1", TipoSuperficie.terra_concreto, 20, 8760.0,
        ProtecaoToquePasso.nenhuma,
        False,                                  # adicionar sistema interno? nao
        False,                                  # incluir economico? nao
    ])
    z = build_zona(p)
    assert z.nome == "Zona 1"
    assert z.n_z == 20
    assert z.sistemas_internos == []
    assert z.c_z is None


def test_build_zona_com_sistema_interno():
    p = FakePrompter([
        "Z", TipoSuperficie.terra_concreto, 5, 4000.0,
        ProtecaoToquePasso.nenhuma,
        True, "Sis", 2.5, 1.0, 1.0, FiacaoInterna.laco_grande, None,  # 1 sistema + dps
        False,                                  # em ZPR 0A? nao
        False,                                  # adicionar outro sistema? nao
        False,                                  # incluir economico? nao
    ])
    z = build_zona(p)
    assert len(z.sistemas_internos) == 1
    assert z.sistemas_internos[0].U_W == 2.5


def test_build_zona_com_economico():
    p = FakePrompter([
        "Z", TipoSuperficie.terra_concreto, 5, 4000.0,
        ProtecaoToquePasso.avisos,
        False,                                  # adicionar sistema interno? nao
        True,
        100.0, 50.0, 800.0, 40.0, 30.0,
    ])
    z = build_zona(p)
    assert z.medidas.protecao_toque_passo == ProtecaoToquePasso.avisos
    assert z.c_z == 100.0 and z.c_b == 800.0


def test_build_estrutura_minima():
    p = FakePrompter([
        "Edif A", 20.0, 10.0, 5.0,
        Localizacao.isolada, TipoConstrucao.robusta,
        RiscoIncendio.normal, ProvidenciaIncendio.nenhuma,
        TipoOcupacao.outros, ZonaExplosao.nenhuma,   # ocupacao, zona explosao
        False,                                        # sistemas criticos
        None,
        100,
        False,                                  # informar c_t? nao
        "Z1", TipoSuperficie.terra_concreto, 50, 8760.0,
        ProtecaoToquePasso.nenhuma,
        False,                                  # adicionar sistema interno? nao
        False,                                  # incluir economico? nao
        False,                                  # adicionar outra zona? nao
        False,                                  # adicionar linha? nao
    ])
    est = build_estrutura(p)
    assert est.nome == "Edif A"
    assert est.L == 20.0 and est.n_t == 100
    assert len(est.zonas) == 1 and est.linhas == []
    assert est.nivel_spda is None


def test_build_projeto_uma_estrutura():
    p = FakePrompter([
        "Projeto P", "Sao Paulo", 4.0,
        False,                  # R4 representativo? nao (metodo detalhado)
        False,                  # preencher identificacao? nao
        "E1", 20.0, 10.0, 5.0,
        Localizacao.isolada, TipoConstrucao.robusta,
        RiscoIncendio.normal, ProvidenciaIncendio.nenhuma,
        TipoOcupacao.outros, ZonaExplosao.nenhuma, False, None, 100, False,
        "Z1", TipoSuperficie.terra_concreto, 50, 8760.0,
        ProtecaoToquePasso.nenhuma,
        False,                  # adicionar sistema interno? nao
        False,                  # incluir economico? nao
        False, False,           # adicionar outra zona? nao; adicionar linha? nao
        False,                  # adicionar outra estrutura? nao
    ])
    proj = build_projeto(p)
    assert proj.nome == "Projeto P"
    assert proj.r4_representativo is False
    assert proj.cidade == "Sao Paulo"
    assert proj.N_G == 4.0
    assert len(proj.estruturas) == 1


def test_build_estrutura_completa_com_adjacente_e_lacos():
    # exercita: nivel_spda real, c_t, estrutura adjacente, 2 zonas, 1 linha
    # com 2 trechos. Cobre todos os ramos de laco/opcional do build_estrutura.
    p = FakePrompter([
        "Edif B", 30.0, 20.0, 10.0,
        Localizacao.topo_colina, TipoConstrucao.simples,
        RiscoIncendio.alto, ProvidenciaIncendio.extintor,
        TipoOcupacao.hotel, ZonaExplosao.zona_1_21,  # ocupacao, zona explosao
        True,                                    # sistemas criticos
        NivelProtecao.III,                       # nivel_spda real
        80,                                      # n_t
        True, 100000.0,                          # c_t? sim, valor
        # zona 1 (com 1 sistema interno + economico):
        "Z1", TipoSuperficie.marmore_ceramica, 40, 8000.0,
        ProtecaoToquePasso.isolacao,
        True, "Sis-Z1", 4.0, 1.0, 1.0, FiacaoInterna.laco_pequeno, None,  # sistema + dps
        False,                                   # em ZPR 0A? nao
        False,                                   # adicionar outro sistema? nao
        True, 100.0, 50.0, 800.0, 40.0, 30.0,    # economico
        True,                                    # adicionar outra zona? sim
        # zona 2 (sem sistema, sem economico):
        "Z2", TipoSuperficie.terra_concreto, 10, 2000.0,
        ProtecaoToquePasso.nenhuma,
        False,                                   # adicionar sistema interno? nao
        False,                                   # incluir economico? nao
        False,                                   # adicionar outra zona? nao
        True,                                    # adicionar linha? sim
        # linha 1 (conecta a estrutura adjacente):
        TipoLinha.at_trafo, CategoriaLinha.energia, InstalacaoLinha.enterrada,
        AmbienteLinha.urbano, TipoLinhaExterna.blindada_interligada,
        ClasseBlindagemRS.rs_ate_1, None, ProtecaoToquePasso.nenhuma,
        True, 15.0, 12.0, 6.0, Localizacao.isolada,  # adjacente? sim + build_adjacente
        800.0, False,                            # trecho 1
        True, 200.0, False,                      # trecho 2 (adicionar=True, L_L, rho?)
        False,                                   # adicionar outro trecho? nao
        False,                                   # adicionar outra linha? nao
    ])
    est = build_estrutura(p)
    assert est.nivel_spda == NivelProtecao.III
    assert est.c_t == 100000.0
    assert est.linhas[0].adjacente is not None
    assert est.linhas[0].adjacente.L_J == 15.0
    assert [z.nome for z in est.zonas] == ["Z1", "Z2"]
    assert est.zonas[0].c_b == 800.0 and est.zonas[1].c_z is None
    assert len(est.zonas[0].sistemas_internos) == 1
    assert est.zonas[0].sistemas_internos[0].U_W == 4.0
    assert len(est.linhas) == 1
    assert est.linhas[0].categoria == CategoriaLinha.energia
    assert est.linhas[0].classe_blindagem == ClasseBlindagemRS.rs_ate_1
    assert len(est.linhas[0].trechos) == 2
    assert est.linhas[0].trechos[1].L_L == 200.0


def test_build_identificacao_pulada():
    p = FakePrompter([False])  # nao preencher
    assert build_identificacao(p) is None


def test_build_identificacao_preenchida():
    p = FakePrompter([
        True,                                   # preencher? sim
        "Laudo A", "Cliente X", "Rua 1",        # titulo, cliente, endereco
        "Eng Fulano", "ART-123", "CREA-SP 456", # responsavel, art, registro
        "2026-07-01", "",                       # data, observacoes
    ])
    ident = build_identificacao(p)
    assert ident is not None
    assert ident.responsavel == "Eng Fulano"
    assert ident.art == "ART-123"
    assert ident.observacoes is None            # "" -> None


def test_build_sistema_interno_com_dps():
    p = FakePrompter([
        "Sis 1", 6.0, 1.0, 1.0, FiacaoInterna.blindado_conduto,
        NivelDPS.III,                           # dps coordenado
        False,                                  # em ZPR 0A? nao
    ])
    sis = build_sistema_interno(p)
    assert sis.dps == NivelDPS.III


def test_build_projeto_r4_representativo():
    p = FakePrompter([
        "Projeto P", "Sao Paulo", 4.0,
        True,                   # R4 representativo? sim
        False,                  # preencher identificacao? nao
        "E1", 20.0, 10.0, 5.0,
        Localizacao.isolada, TipoConstrucao.robusta,
        RiscoIncendio.normal, ProvidenciaIncendio.nenhuma,
        TipoOcupacao.outros, ZonaExplosao.nenhuma, False, None, 100, False,
        "Z1", TipoSuperficie.terra_concreto, 50, 8760.0,
        ProtecaoToquePasso.nenhuma,
        False, False, False, False, False,
    ])
    proj = build_projeto(p)
    assert proj.r4_representativo is True


def test_editar_trecho_altera_campos_e_override():
    atual = Trecho(L_L=1000.0)
    # L_L 1000->1500, sem rho, define override de instalacao
    p = FakePrompter([1500.0, False,
                      InstalacaoLinha.enterrada, None, None])
    t = editar_trecho(p, atual)
    assert t.L_L == 1500.0
    assert t.rho is None
    assert t.instalacao == InstalacaoLinha.enterrada


def test_editar_sistema_expoe_k_s4():
    atual = SistemaInterno(nome="S", U_W=2.5)
    assert atual.K_S4 is None
    # nome S->S2, sobrepoe K_S4=0.5
    p = FakePrompter(["S2", 2.5, 1.0, 1.0, FiacaoInterna.laco_grande, None,
                      False,                    # em ZPR 0A? nao
                      True, 0.5])
    s = editar_sistema(p, atual)
    assert s.nome == "S2"
    assert s.K_S4 == 0.5


def test_editar_zona_altera_avancados_preserva_nao_perguntado():
    atual = Zona(nome="Z1", superficie=TipoSuperficie.terra_concreto,
                 n_z=100, t_z=8760)
    # basico (n_z 100->150), sem patrimonio, avancado (h_z, relevancia),
    # gerenciar sistemas -> Concluir
    p = FakePrompter([
        "Z1", TipoSuperficie.terra_concreto, 150, 8760.0,
        ProtecaoToquePasso.nenhuma,
        False,                              # patrimonio? nao
        PerigoEspecial.panico_baixo,        # h_z via Tabela C.6 (= 2)
        RelevanciaAD.parte_hmax,            # relevancia_AD
        "Concluir",                         # gerenciar sistemas
    ])
    z = editar_zona(p, atual)
    assert z.n_z == 150
    assert z.h_z == 2.0                     # Tabela C.6: panico baixo -> h_z = 2
    assert z.relevancia_AD == RelevanciaAD.parte_hmax


def test_build_projeto_coleta_identificacao():
    p = FakePrompter([
        "Projeto P", "Campinas", 4.0,
        False,                                  # R4 representativo? nao
        False,                                  # preencher identificacao? nao
        "E1", 20.0, 10.0, 5.0,
        Localizacao.isolada, TipoConstrucao.robusta,
        RiscoIncendio.normal, ProvidenciaIncendio.nenhuma,
        TipoOcupacao.outros, ZonaExplosao.nenhuma, False, None, 100, False,
        "Z1", TipoSuperficie.terra_concreto, 50, 8760.0,
        ProtecaoToquePasso.nenhuma,
        False, False, False, False, False,
    ])
    proj = build_projeto(p)
    assert proj.identificacao is None
    assert proj.nome == "Projeto P"
    assert proj.cidade == "Campinas"

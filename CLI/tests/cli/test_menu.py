import io
from rich.console import Console

from spda.cli.menu import EstadoSessao, executar_acao, loop, ACOES
from spda.cli.persistencia import salvar_projeto
from spda.model.projeto import Projeto, Estrutura, Zona
from spda.model.enums import (
    Localizacao, TipoConstrucao, RiscoIncendio, ProvidenciaIncendio,
    TipoSuperficie, TipoOcupacao, ZonaExplosao, ProtecaoToquePasso,
    RelevanciaAD, PerigoEspecial,
)
from tests.cli.fakes import FakePrompter


def _proj(nome="P"):
    z = Zona(nome="Z1", superficie=TipoSuperficie.terra_concreto, n_z=100, t_z=8760)
    est = Estrutura(
        nome="A", L=50, W=30, H=20, localizacao=Localizacao.isolada,
        tipo_construcao=TipoConstrucao.simples, risco_incendio=RiscoIncendio.alto,
        providencias_incendio=ProvidenciaIncendio.nenhuma, n_t=200, zonas=[z],
    )
    return Projeto(nome=nome, N_G=4.0, estruturas=[est])


def _console():
    return Console(file=io.StringIO(), force_terminal=False)


def _saida():
    linhas = []
    return linhas, linhas.append


def test_acoes_inclui_sair():
    assert "Sair" in ACOES


def test_calcular_preenche_resultado():
    linhas, escrever = _saida()
    estado = EstadoSessao(projeto=_proj())
    novo = executar_acao("Calcular risco", estado, FakePrompter([]),
                         _console(), escrever)
    assert novo.resultado is not None
    assert novo.resultado.estruturas[0].R1 > 0


def test_calcular_sem_projeto_avisa():
    linhas, escrever = _saida()
    estado = EstadoSessao(projeto=None)
    novo = executar_acao("Calcular risco", estado, FakePrompter([]),
                         _console(), escrever)
    assert novo.resultado is None
    assert any("projeto" in s.lower() for s in linhas)


def test_remover_estrutura():
    estado = EstadoSessao(projeto=_proj())
    estado.projeto.estruturas.append(estado.projeto.estruturas[0].model_copy())
    estado.projeto.estruturas[1].nome = "B"
    p = FakePrompter(["B"])
    linhas, escrever = _saida()
    novo = executar_acao("Remover estrutura", estado, p, _console(), escrever)
    nomes = [e.nome for e in novo.projeto.estruturas]
    assert nomes == ["A"]


def test_editar_estrutura_drill_down_e_preserva_reservado():
    estado = EstadoSessao(projeto=_proj())
    # descida_natural nao e perguntado: deve sobreviver a edicao
    estado.projeto.estruturas[0].descida_natural = True
    p = FakePrompter([
        "1. A",                              # selecionar estrutura (rotulo idx)
        # _campos_estrutura:
        "A2", 50.0, 30.0, 25.0,              # nome, L, W, H
        Localizacao.isolada, TipoConstrucao.simples,
        RiscoIncendio.alto, ProvidenciaIncendio.nenhuma,
        TipoOcupacao.outros, ZonaExplosao.nenhuma,
        False,                               # sistemas criticos
        None,                                # nivel_spda
        200,                                 # n_t
        False,                               # informar c_t? nao
        # _avancado_estrutura:
        False,                               # faixa de altura? nao
        True,                                # risco_explosao? sim
        # gerenciar zonas -> editar "1. Z1":
        "1. Z1",
        "Z1", TipoSuperficie.terra_concreto, 150, 8760.0,
        ProtecaoToquePasso.nenhuma,
        False,                               # patrimonio? nao
        PerigoEspecial.sem_perigo,           # h_z via Tabela C.6 (= 1)
        RelevanciaAD.estrutura_inteira,      # relevancia
        "Concluir",                          # gerenciar sistemas da zona
        "Concluir",                          # gerenciar zonas
        "Concluir",                          # gerenciar linhas
    ])
    linhas, escrever = _saida()
    novo = executar_acao("Editar estrutura", estado, p, _console(), escrever)
    est = novo.projeto.estruturas[0]
    assert est.nome == "A2"
    assert est.H == 25.0
    assert est.risco_explosao is True
    assert est.zonas[0].n_z == 150
    assert est.descida_natural is True       # preservado (nao perguntado)
    assert novo.resultado is None


def test_estudo_de_solucao_gera_passos():
    linhas, escrever = _saida()
    estado = EstadoSessao(projeto=_proj())
    novo = executar_acao("Estudo de solucao", estado, FakePrompter([]),
                         _console(), escrever)
    assert any("Estudo" in s or "R1" in s for s in linhas)


def test_salvar_e_carregar_projeto(tmp_path):
    destino = tmp_path / "p.json"
    estado = EstadoSessao(projeto=_proj("Salvo"))
    executar_acao("Salvar projeto", estado, FakePrompter([str(destino)]),
                  _console(), (lambda s: None))
    assert destino.exists()
    vazio = EstadoSessao(projeto=None)
    novo = executar_acao("Carregar projeto", vazio,
                         FakePrompter([str(destino)]), _console(),
                         (lambda s: None))
    assert novo.projeto is not None and novo.projeto.nome == "Salvo"


import pytest


@pytest.mark.parametrize("acao", [
    "Adicionar estrutura", "Listar estruturas", "Editar estrutura",
    "Remover estrutura",
    "Calcular risco", "Estudo de solucao", "Gerar relatorio",
    "Salvar projeto",
])
def test_acoes_guardadas_tem_branch(acao):
    # Com projeto=None, toda acao guardada deve sair pelo guard sem estourar
    # (prova que ha branch de despacho; o else levanta AssertionError).
    linhas, escrever = _saida()
    estado = EstadoSessao(projeto=None)
    novo = executar_acao(acao, estado, FakePrompter([]), _console(), escrever)
    assert novo is estado


def test_acao_desconhecida_levanta_assertion():
    with pytest.raises(AssertionError):
        executar_acao("Inexistente", EstadoSessao(projeto=_proj()),
                      FakePrompter([]), _console(), (lambda s: None))


def test_gerar_relatorio_json(tmp_path):
    destino = tmp_path / "rel.json"
    estado = EstadoSessao(projeto=_proj())
    p = FakePrompter(["json", str(destino)])
    executar_acao("Gerar relatorio", estado, p, _console(), (lambda s: None))
    assert destino.exists()
    import json
    assert json.loads(destino.read_text(encoding="utf-8"))["projeto"] == "P"


def test_loop_continua_apos_erro_e_sai():
    # "Carregar projeto" com caminho inexistente -> FileNotFoundError capturado
    # pelo loop (escreve erro), depois "Sair" encerra sem crash.
    linhas, escrever = _saida()
    p = FakePrompter(["Carregar projeto", "/nao/existe.json", "Sair"])
    estado = loop(p, _console(), escrever, EstadoSessao())
    assert isinstance(estado, EstadoSessao)
    assert any("Erro" in s for s in linhas)


def test_salvar_caminho_vazio_nao_derruba_loop():
    # Enter sem digitar caminho -> ValueError capturado pelo loop, sem PermissionError.
    linhas, escrever = _saida()
    p = FakePrompter(["Salvar projeto", "", "Sair"])
    estado = loop(p, _console(), escrever, EstadoSessao(projeto=_proj()))
    assert isinstance(estado, EstadoSessao)
    assert any("Erro" in s for s in linhas)


def test_gerar_relatorio_markdown(tmp_path):
    destino = tmp_path / "rel.md"
    estado = EstadoSessao(projeto=_proj())
    p = FakePrompter(["markdown", str(destino)])
    executar_acao("Gerar relatorio", estado, p, _console(), (lambda s: None))
    assert destino.exists()
    assert "Relat" in destino.read_text(encoding="utf-8")


def test_gerar_relatorio_memorial_md(tmp_path):
    destino = tmp_path / "memorial.md"
    estado = EstadoSessao(projeto=_proj())
    p = FakePrompter(["memorial-md", str(destino)])
    executar_acao("Gerar relatorio", estado, p, _console(), (lambda s: None))
    assert destino.exists()
    texto = destino.read_text(encoding="utf-8")
    assert "## Notas tecnicas" in texto
    assert "## Diagnostico por estrutura" in texto


def test_gerar_relatorio_memorial_html(tmp_path):
    destino = tmp_path / "memorial.html"
    estado = EstadoSessao(projeto=_proj())
    p = FakePrompter(["memorial-html", str(destino)])
    executar_acao("Gerar relatorio", estado, p, _console(), (lambda s: None))
    assert destino.exists()
    texto = destino.read_text(encoding="utf-8")
    assert "<html" in texto.lower()
    assert "@media print" in texto

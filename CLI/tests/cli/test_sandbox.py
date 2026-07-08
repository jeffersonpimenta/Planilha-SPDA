from rich.console import Console

from spda.cli.sandbox import executar_sandbox
from spda.cli.menu import EstadoSessao
from spda.model.projeto import Projeto, Estrutura, Zona, Linha, Trecho
from spda.model.enums import (
    Localizacao, TipoConstrucao, RiscoIncendio, ProvidenciaIncendio,
    TipoSuperficie,
)
from tests.cli.fakes import FakePrompter


def _console():
    return Console(record=True, width=120)


def _saida():
    linhas: list[str] = []
    return linhas, linhas.append


def _projeto_arriscado():
    z = Zona(nome="Z1", superficie=TipoSuperficie.terra_concreto, n_z=100,
             t_z=8760)
    est = Estrutura(
        nome="A", L=50, W=30, H=20, localizacao=Localizacao.isolada,
        tipo_construcao=TipoConstrucao.simples, risco_incendio=RiscoIncendio.alto,
        providencias_incendio=ProvidenciaIncendio.nenhuma, n_t=200, zonas=[z],
        linhas=[Linha(trechos=[Trecho(L_L=1000)])],
    )
    return Projeto(nome="P", N_G=4.0, estruturas=[est])


def test_sandbox_voltar_imediato():
    linhas, escrever = _saida()
    estado = EstadoSessao(projeto=_projeto_arriscado())
    executar_sandbox(estado, FakePrompter(["Voltar"]), _console(), escrever)
    assert estado.projeto.solucao is None  # nada salvo


def test_sandbox_ajustar_e_salvar(tmp_path):
    linhas, escrever = _saida()
    p = _projeto_arriscado()
    estado = EstadoSessao(projeto=p)
    destino = str(tmp_path / "p.json")
    # roteiro: estrutura A -> Ajustar -> medida SPDA -> degrau "III"
    #          -> Salvar no projeto (caminho) -> Voltar painel -> Voltar
    respostas = [
        "1. A (R1 EXCEDE | F ok)",                 # selecionar estrutura
        "Ajustar medida",
        "SPDA (nível de proteção I-IV)",           # descricao da medida
        "Estrutura protegida por SPDA nível III",  # rotulo do degrau
        "Salvar no projeto",
        destino,                                   # texto: caminho
        "Voltar",                                  # sai do painel
        "Voltar",                                  # sai da selecao
    ]
    executar_sandbox(estado, FakePrompter(respostas), _console(), escrever)
    assert p.solucao is not None
    assert p.solucao.estruturas["A"].medidas["spda"] == "III"
    assert (tmp_path / "p.json").exists()


def test_sandbox_sugerir_preenche():
    linhas, escrever = _saida()
    p = _projeto_arriscado()
    estado = EstadoSessao(projeto=p)
    respostas = [
        "1. A (R1 EXCEDE | F ok)",
        "Sugerir",
        "Voltar",
        "Voltar",
    ]
    executar_sandbox(estado, FakePrompter(respostas), _console(), escrever)
    # sugestao fica no rascunho; sem salvar, projeto.solucao segue None
    assert p.solucao is None
    assert any("Sugestão aplicada" in s for s in linhas)

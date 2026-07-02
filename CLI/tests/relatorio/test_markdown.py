from spda.app import analisar
from spda.solucao.estudo import estudo_solucao
from spda.relatorio.markdown import gerar_markdown
from spda.model.projeto import Projeto, Estrutura, Zona, Linha, Trecho
from spda.model.enums import (
    Localizacao, TipoConstrucao, RiscoIncendio, ProvidenciaIncendio,
    TipoSuperficie,
)
from tests.test_app import _projeto


def test_markdown_tem_secoes_principais():
    md = gerar_markdown(analisar(_projeto()))
    assert "# Relatório de Análise de Risco" in md
    assert "P1" in md
    assert "R1" in md and "R3" in md and "R4" in md
    assert "Edif A" in md            # nome da estrutura
    assert "Z1" in md                # nome da zona


def test_markdown_marca_status_excede():
    z = Zona(nome="Z1", superficie=TipoSuperficie.terra_concreto, n_z=100, t_z=8760)
    est = Estrutura(
        nome="A", L=50, W=30, H=20, localizacao=Localizacao.isolada,
        tipo_construcao=TipoConstrucao.simples, risco_incendio=RiscoIncendio.alto,
        providencias_incendio=ProvidenciaIncendio.nenhuma, n_t=200, zonas=[z],
        linhas=[Linha(trechos=[Trecho(L_L=1000)])],
    )
    p = Projeto(nome="P", N_G=4.0, estruturas=[est])
    md = gerar_markdown(analisar(p))
    assert "EXCEDE" in md


def test_markdown_inclui_estudo_quando_passado():
    z = Zona(nome="Z1", superficie=TipoSuperficie.terra_concreto, n_z=100, t_z=8760)
    est = Estrutura(
        nome="A", L=50, W=30, H=20, localizacao=Localizacao.isolada,
        tipo_construcao=TipoConstrucao.simples, risco_incendio=RiscoIncendio.alto,
        providencias_incendio=ProvidenciaIncendio.nenhuma, n_t=200, zonas=[z],
        linhas=[Linha(trechos=[Trecho(L_L=1000)])],
    )
    p = Projeto(nome="P", N_G=4.0, estruturas=[est])
    md = gerar_markdown(analisar(p), estudo=estudo_solucao(p))
    assert "Estudo de Solução" in md
    assert "→" in md  # de -> para nos passos

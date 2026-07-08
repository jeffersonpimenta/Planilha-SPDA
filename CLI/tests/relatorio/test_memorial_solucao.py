from spda.model.projeto import Projeto, Estrutura, Zona, Linha, Trecho
from spda.model.enums import (
    Localizacao, TipoConstrucao, RiscoIncendio, ProvidenciaIncendio,
    TipoSuperficie,
)
from spda.model.solucao import Solucao, SolucaoEstrutura
from spda.relatorio.memorial_solucao import (
    gerar_memorial_solucao_markdown, gerar_memorial_solucao_html,
)


def _projeto_com_solucao():
    z = Zona(nome="Z1", superficie=TipoSuperficie.terra_concreto, n_z=100,
             t_z=8760)
    est = Estrutura(
        nome="A", L=50, W=30, H=20, localizacao=Localizacao.isolada,
        tipo_construcao=TipoConstrucao.simples, risco_incendio=RiscoIncendio.alto,
        providencias_incendio=ProvidenciaIncendio.nenhuma, n_t=200, zonas=[z],
        linhas=[Linha(trechos=[Trecho(L_L=1000)])],
    )
    p = Projeto(nome="P", N_G=4.0, estruturas=[est])
    p.solucao = Solucao(estruturas={"A": SolucaoEstrutura(
        medidas={"spda": "II", "incendio": "fixo_automatico"})})
    return p


def test_markdown_tem_comparacao_e_memorial():
    md = gerar_memorial_solucao_markdown(_projeto_com_solucao())
    assert "Estudo de Soluções" in md
    assert "Instalado" in md and "Adotado" in md      # tabela de medidas
    assert "R1" in md and "antes" in md.lower()
    assert "Número de eventos" in md                   # memorial completo
    assert "Glossário" in md
    # documento unico: memorial primeiro, secao de solucao antes do glossario
    assert (md.index("Análise de Risco")
            < md.index("Estudo de Soluções")
            < md.index("Glossário"))


def test_secao_solucao_recalcula_risco():
    md = gerar_memorial_solucao_markdown(_projeto_com_solucao())
    ini = md.index("Estudo de Soluções")
    fim = md.index("Glossário")
    secao = md[ini:fim]
    # recalculo do estado proposto dentro da secao de solucao
    assert "Recálculo do risco" in secao
    assert "Componentes de risco da zona" in secao       # componentes
    assert "Presença e perdas" in secao                  # perdas (r_p -> L_B)
    assert "Probabilidades agregadas" in secao           # P_A/P_C/P_M
    assert "Agregação de riscos (estado proposto)" in secao
    # eventos nao se repetem (nao dependem das medidas)
    assert "Número de eventos" not in secao
    assert "N_D =" not in secao and "N_M =" not in secao


def test_html_gera_documento():
    html = gerar_memorial_solucao_html(_projeto_com_solucao())
    assert "<html" in html.lower()
    assert "Estudo de Soluções" in html


def test_sem_solucao_ainda_gera_com_nota():
    p = _projeto_com_solucao()
    p.solucao = None
    md = gerar_memorial_solucao_markdown(p)
    assert "Nenhuma medida adotada" in md

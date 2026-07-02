from spda.app import analisar_memoria
from spda.model.enums import (
    Localizacao, NivelDPS, ProvidenciaIncendio, RiscoIncendio, TipoConstrucao,
    TipoSuperficie,
)
from spda.model.identificacao import Identificacao
from spda.model.projeto import (
    Estrutura, Linha, Projeto, SistemaInterno, Zona,
)
from spda.relatorio.memorial import (
    gerar_documento, gerar_memorial_html, gerar_memorial_markdown,
)


def _memoria():
    sis = SistemaInterno(nome="forca", U_W=2.5, dps=NivelDPS.II)
    zona = Zona(nome="Z1", superficie=TipoSuperficie.terra_concreto, n_z=2,
                t_z=8760.0, sistemas_internos=[sis])
    est = Estrutura(
        nome="Predio A", L=20, W=10, H=6, localizacao=Localizacao.isolada,
        tipo_construcao=TipoConstrucao.robusta, risco_incendio=RiscoIncendio.normal,
        providencias_incendio=ProvidenciaIncendio.nenhuma, sistemas_criticos=True,
        n_t=5, zonas=[zona], linhas=[Linha(nome="energia")])
    ident = Identificacao(responsavel="Eng. X", art="1/2026", registro="CREA-MG 1")
    return analisar_memoria(
        Projeto(nome="Proj", N_G=1.5, estruturas=[est], identificacao=ident))


def test_documento_tem_secoes_principais():
    md = gerar_memorial_markdown(_memoria())
    assert "# " in md
    assert "Predio A" in md
    assert "N_D" in md
    assert "Z1" in md
    assert "Eng. X" in md
    assert "R1" in md


def test_memorial_substituicao_aparece():
    md = gerar_memorial_markdown(_memoria())
    assert "N_D = N_G*A_D*C_D*1e-6" in md
    assert "    = " in md


def test_memorial_html_standalone():
    html = gerar_memorial_html(_memoria())
    assert html.lstrip().startswith("<!DOCTYPE html>")
    assert "@media print" in html
    assert "Predio A" in html


def test_gerar_documento_retorna_documento():
    from spda.relatorio.documento import Documento
    doc = gerar_documento(_memoria())
    assert isinstance(doc, Documento)
    assert len(doc.blocos) > 5


def test_memorial_inclui_notas_e_diagnostico():
    from spda.app import analisar_memoria
    from spda.model.projeto import Estrutura, Projeto, Zona
    from spda.model.enums import (
        Localizacao, TipoConstrucao, RiscoIncendio, ProvidenciaIncendio,
        TipoSuperficie,
    )
    from spda.relatorio.memorial import gerar_memorial_markdown

    zona = Zona(nome="Z1", superficie=TipoSuperficie.terra_concreto,
                n_z=100, t_z=8760)
    est = Estrutura(nome="A", L=50, W=30, H=20, localizacao=Localizacao.isolada,
                    tipo_construcao=TipoConstrucao.simples,
                    risco_incendio=RiscoIncendio.alto,
                    providencias_incendio=ProvidenciaIncendio.nenhuma,
                    n_t=200, zonas=[zona])
    proj = Projeto(nome="P", N_G=4.0, estruturas=[est])  # sem identificacao
    mem = analisar_memoria(proj)
    md = gerar_memorial_markdown(mem)

    assert "## Notas tecnicas" in md
    assert "## Diagnostico por estrutura" in md
    assert "AVISO:" in md      # sem identificacao -> aviso de assinatura
    assert "CRITICO:" in md    # R1 desta estrutura excede

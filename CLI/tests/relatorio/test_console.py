from spda.app import analisar
from spda.relatorio.console import linhas_resumo, imprimir_resumo
from tests.test_app import _projeto


def test_linhas_resumo_uma_por_estrutura():
    r = analisar(_projeto())
    linhas = linhas_resumo(r)
    assert len(linhas) == 1
    ln = linhas[0]
    assert ln["estrutura"] == "Edif A"
    assert "R1" in ln and "status_R1" in ln
    assert ln["status_R1"] in ("OK", "EXCEDE")
    assert ln["status_R1"] == ("EXCEDE" if r.estruturas[0].excede_R1 else "OK")


def test_imprimir_resumo_nao_quebra():
    # smoke: render rich nao deve lancar excecao
    imprimir_resumo(analisar(_projeto()))

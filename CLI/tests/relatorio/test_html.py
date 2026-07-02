from spda.relatorio.documento import (
    Documento, Equacao, Nota, Tabela, Titulo,
)
from spda.relatorio.html import para_html


def test_documento_html_standalone():
    html = para_html(Documento([Titulo(1, "Relatorio")]), titulo="Laudo")
    assert html.lstrip().startswith("<!DOCTYPE html>")
    assert "<title>Laudo</title>" in html
    assert "@media print" in html
    assert "<h1>Relatorio</h1>" in html


def test_html_escapa_texto():
    html = para_html(Documento([Titulo(1, "A & B <x>")]), titulo="t")
    assert "A &amp; B &lt;x&gt;" in html


def test_html_equacao_e_nota():
    doc = Documento([
        Equacao("N_D", "A.2", "N_D = N_G*A_D", "1.5*1000", "1.500e+03"),
        Nota("aviso", "cuidado"),
    ])
    html = para_html(doc, titulo="t")
    assert "class=\"equacao\"" in html
    assert "class=\"nota aviso\"" in html
    assert "AVISO" in html


def test_html_tabela():
    html = para_html(Documento([Tabela(["A", "B"], [["1", "2"]])]), titulo="t")
    assert "<table>" in html
    assert "<th>A</th>" in html
    assert "<td>1</td>" in html

from spda.relatorio.documento import (
    Documento, Equacao, Glossario, Lista, Nota, Paragrafo, QuebraPagina,
    Tabela, Titulo, para_markdown,
)


def test_titulo_e_paragrafo():
    doc = Documento([Titulo(1, "Relatorio"), Paragrafo("Conforme **norma**.")])
    md = para_markdown(doc)
    assert "# Relatorio" in md
    assert "Conforme **norma**." in md


def test_equacao_com_substituicao():
    eq = Equacao(simbolo="N_D", eq="A.2",
                 forma_simbolica="N_D = N_G*A_D*C_D*1e-6",
                 substituicao="1.5*1000*0.5*1e-6", resultado="7.500e-04")
    md = para_markdown(Documento([eq]))
    assert "**N_D** (eq. A.2)" in md
    assert "N_D = N_G*A_D*C_D*1e-6" in md
    assert "= 1.5*1000*0.5*1e-6" in md
    assert "= 7.500e-04" in md


def test_equacao_lookup_sem_substituicao():
    eq = Equacao(simbolo="C_D", eq="Tabela A.1", forma_simbolica=None,
                 substituicao=None, resultado="0.5", origem="isolada")
    md = para_markdown(Documento([eq]))
    assert "**C_D** = 0.5" in md
    assert "Tabela A.1" in md
    assert "isolada" in md


def test_tabela():
    t = Tabela(cabecalho=["Risco", "Valor"], linhas=[["R1", "1e-5"], ["R3", "1e-3"]])
    md = para_markdown(Documento([t]))
    assert "| Risco | Valor |" in md
    assert "| R1 | 1e-5 |" in md


def test_nota_niveis():
    md = para_markdown(Documento([Nota("aviso", "cuidado")]))
    assert "> AVISO: cuidado" in md


def test_lista_e_glossario():
    doc = Documento([
        Lista(["a", "b"], ordenada=False),
        Glossario([("N_D", "descargas na estrutura", "1/ano")]),
    ])
    md = para_markdown(doc)
    assert "- a" in md
    assert "N_D" in md and "descargas na estrutura" in md


def test_quebra_pagina_ignora_em_markdown():
    md = para_markdown(Documento([Paragrafo("x"), QuebraPagina(), Paragrafo("y")]))
    assert "x" in md and "y" in md

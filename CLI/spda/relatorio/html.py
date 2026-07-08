# spda/relatorio/html.py
"""Serializador HTML auto-contido e imprimivel (print CSS embutido).

Mesmo documento de blocos do Markdown; aqui vira um HTML standalone que o usuario
imprime para PDF pelo navegador. CSS com @media print: margens A4, evita quebra de
pagina dentro de equacoes e tabelas. Sem dependencia externa, sem emoji.
"""
from __future__ import annotations

from html import escape

from spda.relatorio.documento import (
    Documento, Equacao, Glossario, Lista, Nota, Paragrafo, QuebraPagina,
    Tabela, Titulo,
)

_PREFIXO_NOTA = {"info": "NOTA", "aviso": "AVISO", "critico": "CRÍTICO"}

_CSS = """
:root { --tinta: #1a1a1a; --borda: #888; --aviso: #b35900; --critico: #a40000; }
* { box-sizing: border-box; }
body { font-family: Georgia, 'Times New Roman', serif; color: var(--tinta);
       max-width: 820px; margin: 24px auto; padding: 0 16px; line-height: 1.5; }
h1, h2, h3, h4 { font-family: Arial, Helvetica, sans-serif; line-height: 1.25; }
h1 { font-size: 1.6rem; border-bottom: 2px solid var(--tinta); padding-bottom: 4px; }
h2 { font-size: 1.3rem; margin-top: 1.6em; }
h3 { font-size: 1.1rem; }
table { border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 0.95rem; }
th, td { border: 1px solid var(--borda); padding: 4px 8px; text-align: left;
         vertical-align: top; }
th { background: #f0f0f0; }
.equacao { font-family: 'Courier New', monospace; background: #f7f7f7;
           border-left: 3px solid var(--borda); padding: 8px 12px; margin: 10px 0;
           white-space: pre; overflow-x: auto; }
.equacao .rotulo { font-family: Arial, sans-serif; font-weight: bold; color: #333; }
.nota { border: 1px solid var(--borda); border-left-width: 5px; padding: 6px 10px;
        margin: 10px 0; }
.nota.aviso { border-left-color: var(--aviso); }
.nota.critico { border-left-color: var(--critico); }
.assinatura { margin-top: 48px; }
@media print {
  body { margin: 0; max-width: none; font-size: 11pt; }
  h2, h3, h4 { page-break-after: avoid; }
  .equacao, table, .nota { page-break-inside: avoid; }
  .quebra { page-break-before: always; }
  @page { margin: 18mm 16mm; }
}
"""


def _esc(s: str) -> str:
    return escape(str(s), quote=False)


def _html_equacao(e: Equacao) -> str:
    if e.substituicao is not None and e.forma_simbolica is not None:
        corpo = (f'<span class="rotulo">{_esc(e.simbolo)} (eq. {_esc(e.eq)})</span>\n'
                 f"{_esc(e.forma_simbolica)}\n"
                 f"    = {_esc(e.substituicao)}\n"
                 f"    = {_esc(e.resultado)}")
        return f'<div class="equacao">{corpo}</div>'
    sufixo = _esc(e.eq)
    if e.origem:
        sufixo += "; " + _esc(e.origem)
    return (f'<p><span class="rotulo">{_esc(e.simbolo)}</span> = '
            f"{_esc(e.resultado)} ({sufixo})</p>")


def _html_tabela(t: Tabela) -> str:
    cab = "".join(f"<th>{_esc(c)}</th>" for c in t.cabecalho)
    linhas = "".join(
        "<tr>" + "".join(f"<td>{_esc(v)}</td>" for v in lin) + "</tr>"
        for lin in t.linhas)
    return f"<table><thead><tr>{cab}</tr></thead><tbody>{linhas}</tbody></table>"


def _html_bloco(b) -> str:
    if isinstance(b, Titulo):
        n = min(max(b.nivel, 1), 4)
        return f"<h{n}>{_esc(b.texto)}</h{n}>"
    if isinstance(b, Paragrafo):
        return f"<p>{_inline(b.texto)}</p>"
    if isinstance(b, Equacao):
        return _html_equacao(b)
    if isinstance(b, Tabela):
        return _html_tabela(b)
    if isinstance(b, Nota):
        return (f'<div class="nota {_esc(b.nivel)}"><strong>'
                f"{_PREFIXO_NOTA[b.nivel]}:</strong> {_esc(b.texto)}</div>")
    if isinstance(b, Lista):
        tag = "ol" if b.ordenada else "ul"
        itens = "".join(f"<li>{_esc(i)}</li>" for i in b.itens)
        return f"<{tag}>{itens}</{tag}>"
    if isinstance(b, Glossario):
        linhas = "".join(
            f"<tr><td>{_esc(s)}</td><td>{_esc(n)}</td><td>{_esc(u)}</td></tr>"
            for s, n, u in b.itens)
        return ("<table><thead><tr><th>Símbolo</th><th>Descrição</th>"
                f"<th>Unidade</th></tr></thead><tbody>{linhas}</tbody></table>")
    if isinstance(b, QuebraPagina):
        return '<div class="quebra"></div>'
    return ""


def _inline(texto: str) -> str:
    """Escapa e converte **negrito** e `codigo` simples para HTML."""
    import re
    s = _esc(texto)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    return s


def para_html(doc: Documento, titulo: str) -> str:
    corpo = "\n".join(_html_bloco(b) for b in doc.blocos)
    return (
        "<!DOCTYPE html>\n"
        '<html lang="pt-br">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{_esc(titulo)}</title>\n<style>{_CSS}</style>\n"
        f"</head>\n<body>\n{corpo}\n</body>\n</html>\n"
    )

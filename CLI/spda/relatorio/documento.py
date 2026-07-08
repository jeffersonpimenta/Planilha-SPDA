# spda/relatorio/documento.py
"""Documento abstrato de blocos + serializador Markdown.

Fonte unica de conteudo: os blocos sao serializados para Markdown (aqui) e para
HTML (html.py), sem duplicar a logica de montagem (memorial.py). Os blocos sao
dataclasses simples (sem validacao -- sao view-models prontos).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Union


@dataclass
class Titulo:
    nivel: int
    texto: str


@dataclass
class Paragrafo:
    texto: str


@dataclass
class Equacao:
    simbolo: str
    eq: str
    forma_simbolica: str | None
    substituicao: str | None
    resultado: str
    origem: str | None = None


@dataclass
class Tabela:
    cabecalho: list[str]
    linhas: list[list[str]]
    alinhamento: list[str] | None = None


@dataclass
class Nota:
    nivel: str            # info | aviso | critico
    texto: str


@dataclass
class Lista:
    itens: list[str]
    ordenada: bool = False


@dataclass
class Glossario:
    itens: list[tuple[str, str, str]]   # (simbolo, nome, unidade)


@dataclass
class QuebraPagina:
    pass


Bloco = Union[Titulo, Paragrafo, Equacao, Tabela, Nota, Lista, Glossario,
              QuebraPagina]


@dataclass
class Documento:
    blocos: list[Bloco] = field(default_factory=list)


_PREFIXO_NOTA = {"info": "NOTA", "aviso": "AVISO", "critico": "CRÍTICO"}


def _md_equacao(e: Equacao) -> list[str]:
    if e.substituicao is not None and e.forma_simbolica is not None:
        return [
            f"**{e.simbolo}** (eq. {e.eq})",
            "",
            "```",
            e.forma_simbolica,
            f"    = {e.substituicao}",
            f"    = {e.resultado}",
            "```",
            "",
        ]
    sufixo = e.eq
    if e.origem:
        sufixo += f"; {e.origem}"
    return [f"**{e.simbolo}** = {e.resultado}  ({sufixo})", ""]


def _md_tabela(t: Tabela) -> list[str]:
    linhas = ["| " + " | ".join(t.cabecalho) + " |",
              "|" + "|".join(["---"] * len(t.cabecalho)) + "|"]
    for lin in t.linhas:
        linhas.append("| " + " | ".join(lin) + " |")
    linhas.append("")
    return linhas


def para_markdown(doc: Documento) -> str:
    out: list[str] = []
    for b in doc.blocos:
        if isinstance(b, Titulo):
            out += ["#" * b.nivel + " " + b.texto, ""]
        elif isinstance(b, Paragrafo):
            out += [b.texto, ""]
        elif isinstance(b, Equacao):
            out += _md_equacao(b)
        elif isinstance(b, Tabela):
            out += _md_tabela(b)
        elif isinstance(b, Nota):
            out += [f"> {_PREFIXO_NOTA[b.nivel]}: {b.texto}", ""]
        elif isinstance(b, Lista):
            marcador = (lambda i: f"{i}.") if b.ordenada else (lambda i: "-")
            for i, item in enumerate(b.itens, 1):
                out.append(f"{marcador(i)} {item}")
            out.append("")
        elif isinstance(b, Glossario):
            out += ["| Símbolo | Descrição | Unidade |", "|---|---|---|"]
            for simbolo, nome, unidade in b.itens:
                out.append(f"| {simbolo} | {nome} | {unidade} |")
            out.append("")
        elif isinstance(b, QuebraPagina):
            continue
    return "\n".join(out).rstrip() + "\n"

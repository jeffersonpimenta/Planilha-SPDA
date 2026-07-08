"""Menu construtor: estado de sessao + despacho de acoes (camada de I/O).

executar_acao recebe um Prompter, um rich.Console e um callback `escrever`
(texto simples), o que torna cada acao testavel sem terminal interativo.
main() monta os objetos reais e roda o laco.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from pydantic import ValidationError

from spda.app import analisar, analisar_memoria
from spda.cli import persistencia
from spda.cli.prompts import Prompter, QuestionaryPrompter
from spda.cli.sandbox import executar_sandbox
from spda.cli.wizards import build_estrutura, build_projeto, editar_estrutura
from spda.model.projeto import Projeto
from spda.model.resultado import Resultado
from spda.relatorio import json_out, markdown
from spda.relatorio.console import imprimir_resumo
from spda.relatorio.memorial import gerar_memorial_html, gerar_memorial_markdown
from spda.relatorio.memorial_solucao import (
    gerar_memorial_solucao_html, gerar_memorial_solucao_markdown,
)
from spda.solucao.estudo import estudo_solucao

ACOES = [
    "Novo projeto",
    "Adicionar estrutura",
    "Listar estruturas",
    "Editar estrutura",
    "Remover estrutura",
    "Calcular risco",
    "Estudo de solução",
    "Gerar relatório",
    "Salvar projeto",
    "Carregar projeto",
    "Sair",
]


@dataclass
class EstadoSessao:
    projeto: Projeto | None = None
    resultado: Resultado | None = None
    config: str | None = None


def _exige_projeto(estado: EstadoSessao, escrever: Callable[[str], None]) -> bool:
    if estado.projeto is None:
        escrever("Nenhum projeto carregado. Use 'Novo projeto' ou 'Carregar projeto'.")
        return False
    return True


def executar_acao(acao: str, estado: EstadoSessao, prompter: Prompter,
                  console, escrever: Callable[[str], None]) -> EstadoSessao:
    if acao == "Novo projeto":
        estado.projeto = build_projeto(prompter)
        estado.resultado = None
        escrever(f"Projeto '{estado.projeto.nome}' criado.")

    elif acao == "Adicionar estrutura":
        if _exige_projeto(estado, escrever):
            estado.projeto.estruturas.append(build_estrutura(prompter))
            estado.resultado = None
            escrever("Estrutura adicionada.")

    elif acao == "Listar estruturas":
        if _exige_projeto(estado, escrever):
            for i, e in enumerate(estado.projeto.estruturas, 1):
                escrever(f"{i}. {e.nome} ({len(e.zonas)} zona(s), "
                         f"{len(e.linhas)} linha(s))")

    elif acao == "Editar estrutura":
        if _exige_projeto(estado, escrever):
            ests = estado.projeto.estruturas
            if not ests:
                escrever("Não há estruturas para editar.")
            else:
                # rotulo indexado "i. nome" -> selecao unica (nomes podem repetir)
                rotulos = [f"{i + 1}. {e.nome}" for i, e in enumerate(ests)]
                alvo = prompter.selecionar("Editar qual estrutura?", rotulos)
                idx = rotulos.index(alvo)
                ests[idx] = editar_estrutura(prompter, ests[idx])
                estado.resultado = None
                escrever(f"Estrutura '{ests[idx].nome}' atualizada.")

    elif acao == "Remover estrutura":
        if _exige_projeto(estado, escrever):
            nomes = [e.nome for e in estado.projeto.estruturas]
            if not nomes:
                escrever("Não há estruturas para remover.")
            else:
                alvo = prompter.selecionar("Remover qual estrutura?", nomes)
                # remove apenas a PRIMEIRA com esse nome (nomes podem repetir)
                idx = nomes.index(alvo)
                estado.projeto.estruturas = [
                    e for i, e in enumerate(estado.projeto.estruturas) if i != idx
                ]
                estado.resultado = None
                escrever(f"Estrutura '{alvo}' removida.")

    elif acao == "Calcular risco":
        if _exige_projeto(estado, escrever):
            estado.resultado = analisar(estado.projeto, estado.config)
            imprimir_resumo(estado.resultado, console)

    elif acao == "Estudo de solução":
        if _exige_projeto(estado, escrever):
            executar_sandbox(estado, prompter, console, escrever)

    elif acao == "Gerar relatório":
        if _exige_projeto(estado, escrever):
            res = estado.resultado or analisar(estado.projeto, estado.config)
            estado.resultado = res
            formatos = ["markdown", "json", "memorial-md", "memorial-html"]
            fmt = prompter.selecionar("Formato do relatório", formatos)
            sufixos = {"markdown": ".md", "json": ".json",
                       "memorial-md": ".md", "memorial-html": ".html"}
            caminho = persistencia.validar_caminho(
                prompter.texto("Caminho do arquivo de saída"),
                sufixo_padrao=sufixos[fmt])
            caminho.parent.mkdir(parents=True, exist_ok=True)
            if fmt == "json":
                json_out.salvar_json(res, caminho)
            elif fmt == "markdown":
                est = estudo_solucao(estado.projeto, estado.config)
                caminho.write_text(markdown.gerar_markdown(res, estudo=est),
                                   encoding="utf-8")
            else:  # memorial-md | memorial-html
                if estado.projeto.solucao is not None:
                    # Documento unico: memorial instalado + secao de solucao.
                    texto = (gerar_memorial_solucao_markdown(estado.projeto,
                                                             estado.config)
                             if fmt == "memorial-md"
                             else gerar_memorial_solucao_html(estado.projeto,
                                                              estado.config))
                else:
                    mem = analisar_memoria(estado.projeto, estado.config)
                    est = estudo_solucao(estado.projeto, estado.config)
                    texto = (gerar_memorial_markdown(mem, estudo=est)
                             if fmt == "memorial-md"
                             else gerar_memorial_html(mem, estudo=est))
                caminho.write_text(texto, encoding="utf-8")
            escrever(f"Relatório salvo em {caminho}.")

    elif acao == "Salvar projeto":
        if _exige_projeto(estado, escrever):
            caminho = prompter.texto("Caminho para salvar o projeto (.json)")
            destino = persistencia.salvar_projeto(estado.projeto, caminho)
            escrever(f"Projeto salvo em {destino}.")

    elif acao == "Carregar projeto":
        caminho = prompter.texto("Caminho do projeto (.json)")
        estado.projeto = persistencia.carregar_projeto(caminho)
        estado.resultado = None
        escrever(f"Projeto '{estado.projeto.nome}' carregado.")

    else:
        # Rede de seguranca para divergencia ACOES<->branches. AssertionError
        # (e nao ValueError) para NAO ser engolida pelo except do loop, que
        # trata erros de usuario -- aqui e erro de programacao, deve estourar.
        raise AssertionError(f"Ação sem branch de despacho: {acao}")

    return estado


def loop(prompter: Prompter, console, escrever: Callable[[str], None],
         estado: EstadoSessao | None = None) -> EstadoSessao:
    estado = estado or EstadoSessao()
    while True:
        acao = prompter.selecionar("Ação", ACOES)
        if acao == "Sair":
            return estado
        try:
            estado = executar_acao(acao, estado, prompter, console, escrever)
        except KeyboardInterrupt:
            escrever("Ação cancelada.")
        except (OSError, ValueError, ValidationError) as e:
            # OSError cobre FileNotFoundError, PermissionError, IsADirectoryError
            # (ex.: caminho de arquivo invalido) sem derrubar a CLI.
            escrever(f"Erro: {e}")


def main() -> None:  # pragma: no cover
    from rich.console import Console
    console = Console()
    loop(QuestionaryPrompter(), console, lambda s: console.print(s))

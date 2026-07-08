"""Sandbox interativo do Estudo de Solucoes (Secao 11).

O engenheiro parte da edificacao como esta (instalado), adota degraus de
medidas do catalogo, ve R1/F recalculados ao vivo, pede sugestao (greedy) e
salva o resultado como overlay no proprio Projeto (Projeto.solucao)."""
from __future__ import annotations

from typing import Callable

from rich.table import Table

from spda.app import analisar
from spda.cli import persistencia
from spda.cli.prompts import Prompter
from spda.model.solucao import Solucao, SolucaoEstrutura
from spda.relatorio.formato import fmt
from spda.solucao.aplicar import aplicar_solucao
from spda.solucao.catalogo import MEDIDAS
from spda.solucao.estudo import sugerir_solucao

_VOLTAR = "Voltar"
_SEM_ADOCAO = "—"


def executar_sandbox(estado, prompter: Prompter, console,
                     escrever: Callable[[str], None]) -> None:
    projeto = estado.projeto
    sol = (projeto.solucao or Solucao()).model_copy(deep=True)
    while True:
        res = analisar(projeto, estado.config)
        rotulos = [
            f"{i + 1}. {re.nome} "
            f"(R1 {'EXCEDE' if re.excede_R1 else 'ok'} | "
            f"F {'EXCEDE' if re.excede_F else 'ok'})"
            for i, re in enumerate(res.estruturas)
        ]
        alvo = prompter.selecionar("Estrutura para o estudo",
                                   rotulos + [_VOLTAR])
        if alvo == _VOLTAR:
            return
        idx = rotulos.index(alvo)
        _painel(projeto, idx, sol, estado, prompter, console, escrever)


def _painel(projeto, idx: int, sol: Solucao, estado, prompter: Prompter,
            console, escrever: Callable[[str], None]) -> None:
    est_base = projeto.estruturas[idx]
    nome = est_base.nome
    while True:
        se = sol.estruturas.get(nome, SolucaoEstrutura())
        aplicado, avisos = aplicar_solucao(projeto, sol)
        for a in avisos:
            escrever(f"AVISO: {a}")
        res = analisar(aplicado, estado.config)
        re = res.estruturas[idx]
        escrever(
            f"{nome}: R1 {fmt(re.R1)} / RT {fmt(res.rt['R1'])} "
            f"[{'EXCEDE' if re.excede_R1 else 'ok'}] | "
            f"F {fmt(re.F)} / FT {fmt(re.ft)} "
            f"[{'EXCEDE' if re.excede_F else 'ok'}]")
        console.print(_tabela_medidas(est_base, se))

        acao = prompter.selecionar("Sandbox", [
            "Ajustar medida", "Sugerir", "Limpar tudo",
            "Salvar no projeto", "Gerar memorial", _VOLTAR,
        ])
        if acao == _VOLTAR:
            return
        if acao == "Ajustar medida":
            _ajustar(est_base, nome, sol, prompter, escrever)
        elif acao == "Sugerir":
            sugestao = sugerir_solucao(projeto, nome,
                                       se if se.medidas else None,
                                       estado.config)
            if sugestao.medidas:
                sol.estruturas[nome] = sugestao
                escrever(f"Sugestão aplicada: {len(sugestao.medidas)} "
                         f"medida(s) sugerida(s).")
            else:
                travadas = [m.descricao for m in MEDIDAS
                            if m.indice_atual(est_base) is None]
                escrever("Nenhuma sugestão possível. Medidas não avançáveis: "
                         + ("; ".join(travadas) if travadas else "nenhuma")
                         + ".")
        elif acao == "Limpar tudo":
            sol.estruturas.pop(nome, None)
            escrever("Adoções desta estrutura removidas.")
        elif acao == "Salvar no projeto":
            projeto.solucao = sol.model_copy(deep=True)
            caminho = prompter.texto("Caminho para salvar o projeto (.json)")
            destino = persistencia.salvar_projeto(projeto, caminho)
            escrever(f"Solução salva no projeto: {destino}.")
        elif acao == "Gerar memorial":
            _memorial(projeto, sol, estado, prompter, escrever)


def _tabela_medidas(est_base, se: SolucaoEstrutura) -> Table:
    t = Table(title="Medidas de proteção")
    t.add_column("Medida")
    t.add_column("Instalado")
    t.add_column("Adotado")
    t.add_column("Componentes")
    for m in MEDIDAS:
        degrau = se.medidas.get(m.id)
        if degrau is None:
            adotado = _SEM_ADOCAO
        else:
            i = m.indice_de_degrau_str(degrau)
            adotado = m.rotulo_degrau(i) if i is not None else degrau
        t.add_row(m.descricao, m.nivel_atual(est_base), adotado,
                  ", ".join(m.componentes))
    return t


def _ajustar(est_base, nome: str, sol: Solucao, prompter: Prompter,
             escrever: Callable[[str], None]) -> None:
    aplicaveis = [m for m in MEDIDAS if m.indice_atual(est_base) is not None]
    travadas = [m for m in MEDIDAS if m.indice_atual(est_base) is None]
    if travadas:
        escrever("Não avançáveis (fora da escada ou sem elemento): "
                 + "; ".join(m.descricao for m in travadas) + ".")
    if not aplicaveis:
        escrever("Nenhuma medida ajustável nesta estrutura.")
        return
    rotulo_m = prompter.selecionar(
        "Qual medida?", [m.descricao for m in aplicaveis] + [_VOLTAR])
    if rotulo_m == _VOLTAR:
        return
    m = next(x for x in aplicaveis if x.descricao == rotulo_m)
    atual = m.indice_atual(est_base)
    opcoes = [f"{m.rotulo_degrau(i)}"
              + (" (instalado)" if i == atual else "")
              for i in range(atual, len(m.escada))]
    escolha = prompter.selecionar(f"Degrau de '{m.descricao}'", opcoes)
    i = atual + opcoes.index(escolha)
    se = sol.estruturas.setdefault(nome, SolucaoEstrutura())
    if i == atual:
        se.medidas.pop(m.id, None)   # voltar ao instalado
        if not se.medidas:
            sol.estruturas.pop(nome, None)
    else:
        se.medidas[m.id] = m.degrau_str(i)


def _memorial(projeto, sol: Solucao, estado, prompter: Prompter,
              escrever: Callable[[str], None]) -> None:
    from spda.relatorio.memorial_solucao import (
        gerar_memorial_solucao_html, gerar_memorial_solucao_markdown,
    )
    fmt_doc = prompter.selecionar("Formato do memorial",
                                  ["markdown", "html"])
    sufixo = ".md" if fmt_doc == "markdown" else ".html"
    caminho = persistencia.validar_caminho(
        prompter.texto("Caminho do arquivo de saída"), sufixo_padrao=sufixo)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    # rascunho atual do sandbox, mesmo sem "Salvar no projeto"
    tmp = projeto.model_copy(deep=True)
    tmp.solucao = sol.model_copy(deep=True)
    texto = (gerar_memorial_solucao_markdown(tmp, estado.config)
             if fmt_doc == "markdown"
             else gerar_memorial_solucao_html(tmp, estado.config))
    caminho.write_text(texto, encoding="utf-8")
    escrever(f"Memorial salvo em {caminho}.")

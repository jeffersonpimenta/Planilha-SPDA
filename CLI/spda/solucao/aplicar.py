"""Aplica o overlay de Solucao a um Projeto (funcao pura, devolve copia).

Regras:
- degrau adotado NUNCA abaixo do instalado (instalado e realidade fisica);
- estrutura/medida/degrau desconhecidos geram aviso e sao ignorados
  (arquivo pode ter sido editado a mao); nunca quebra o carregamento.
"""
from __future__ import annotations

from spda.model.projeto import Projeto
from spda.model.solucao import Solucao
from spda.solucao.catalogo import por_id


def aplicar_solucao(projeto: Projeto,
                    solucao: Solucao | None = None) -> tuple[Projeto, list[str]]:
    """(projeto com medidas adotadas aplicadas, avisos). Original intacto.

    `solucao` sobrepoe `projeto.solucao` quando fornecida (sandbox usa o
    rascunho ainda nao salvo).
    """
    sol = solucao if solucao is not None else projeto.solucao
    p = projeto.model_copy(deep=True)
    avisos: list[str] = []
    if sol is None:
        return p, avisos

    medidas = por_id()
    indices: dict[str, int] = {}
    for i, est in enumerate(p.estruturas):
        indices.setdefault(est.nome, i)  # primeira ocorrencia

    for nome, se in sol.estruturas.items():
        if nome not in indices:
            avisos.append(f"Solução ignora estrutura inexistente: '{nome}'.")
            continue
        idx = indices[nome]
        est = p.estruturas[idx]
        for mid, degrau in se.medidas.items():
            m = medidas.get(mid)
            if m is None:
                avisos.append(f"'{nome}': medida desconhecida '{mid}' ignorada.")
                continue
            alvo = m.indice_de_degrau_str(degrau)
            if alvo is None:
                avisos.append(
                    f"'{nome}': degrau '{degrau}' inválido para '{mid}'.")
                continue
            atual = m.indice_atual(est)
            if atual is None:
                avisos.append(
                    f"'{nome}': '{m.descricao}' não aplicável "
                    f"(valor fora da escada ou sem elemento).")
                continue
            if alvo < atual:
                avisos.append(
                    f"'{nome}': '{m.descricao}' adotado ({degrau}) abaixo do "
                    f"instalado; prevalece o instalado.")
                continue
            if alvo == atual:
                continue  # sem efeito
            est = m.definir_nivel(est, alvo)
        p.estruturas[idx] = est
    return p, avisos

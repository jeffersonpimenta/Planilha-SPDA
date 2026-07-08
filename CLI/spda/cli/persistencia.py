"""Salvar/carregar o Projeto (modelo de entrada) como JSON via pydantic."""
from __future__ import annotations

from pathlib import Path

from spda.model.projeto import Projeto


def validar_caminho(caminho: str | Path, *, sufixo_padrao: str | None = None) -> Path:
    """Normaliza e valida um caminho de arquivo informado pelo usuario.

    Tolera os erros comuns de digitacao/colagem:
    - aspas em volta do caminho (colar do Explorer) -> removidas;
    - `~` -> diretorio do usuario (expanduser);
    - sem extensao -> aplica `sufixo_padrao` (se informado);
    - vazio / sem nome de arquivo -> ValueError (capturado pelo loop da CLI),
      em vez de PermissionError ao tentar escrever em '.'.
    """
    bruto = str(caminho).strip().strip('"').strip("'").strip()
    if not bruto:
        raise ValueError(
            "Caminho vazio. Informe um arquivo, ex.: projeto.json "
            "ou C:\\Users\\voce\\Desktop\\projeto.json")
    p = Path(bruto).expanduser()
    if not p.name:
        raise ValueError("Caminho inválido (sem nome de arquivo). Ex.: projeto.json")
    if sufixo_padrao and not p.suffix:
        p = p.with_suffix(sufixo_padrao)
    return p


def salvar_projeto(projeto: Projeto, caminho: str | Path) -> Path:
    """Salva o Projeto em JSON. Cria as pastas que faltarem. Devolve o caminho final."""
    p = validar_caminho(caminho, sufixo_padrao=".json")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(projeto.model_dump_json(indent=2), encoding="utf-8")
    return p


def carregar_projeto(caminho: str | Path) -> Projeto:
    texto = validar_caminho(caminho).read_text(encoding="utf-8")
    return Projeto.model_validate_json(texto)

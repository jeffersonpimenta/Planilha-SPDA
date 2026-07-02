from spda.app import analisar_memoria
from spda.model.enums import (
    Localizacao, NivelDPS, ProvidenciaIncendio, RiscoIncendio, TipoConstrucao,
    TipoSuperficie,
)
from spda.model.projeto import (
    Estrutura, Linha, Projeto, SistemaInterno, Zona,
)
from spda.relatorio.glossario import (
    indice_equacoes, indice_tabelas, simbolos_usados,
)


def _memoria():
    sis = SistemaInterno(nome="s", U_W=2.5, dps=NivelDPS.II)
    zona = Zona(nome="Z", superficie=TipoSuperficie.terra_concreto, n_z=1,
                t_z=8760.0, sistemas_internos=[sis])
    est = Estrutura(
        nome="E", L=20, W=10, H=6, localizacao=Localizacao.isolada,
        tipo_construcao=TipoConstrucao.robusta, risco_incendio=RiscoIncendio.normal,
        providencias_incendio=ProvidenciaIncendio.nenhuma, sistemas_criticos=True,
        n_t=1, zonas=[zona], linhas=[Linha()])
    return analisar_memoria(Projeto(nome="P", N_G=1.5, estruturas=[est]))


def test_simbolos_usados_inclui_basicos_e_ordenado():
    itens = simbolos_usados(_memoria())
    simbolos = [s for s, _, _ in itens]
    assert "N_D" in simbolos
    assert "P_SPD" in simbolos
    assert len(simbolos) == len(set(simbolos))
    assert simbolos == sorted(simbolos)


def test_indice_equacoes_tem_referencia():
    linhas = indice_equacoes(_memoria())
    eqs = [e for e, _, _ in linhas]
    assert "A.3" in eqs               # N_D (A.2 e a saliencia A'_D)
    assert all(len(l) == 3 for l in linhas)


def test_indice_tabelas_lista_coeficientes_usados():
    linhas = indice_tabelas(_memoria())
    nomes = [n for _, n, _ in linhas]
    assert "C_D" in nomes

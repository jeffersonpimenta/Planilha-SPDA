from spda.cli.persistencia import salvar_projeto, carregar_projeto
from spda.model.projeto import Projeto, Estrutura, Zona
from spda.model.enums import (
    Localizacao, TipoConstrucao, RiscoIncendio, ProvidenciaIncendio,
    TipoSuperficie,
)


def _projeto():
    z = Zona(nome="Z1", superficie=TipoSuperficie.terra_concreto, n_z=10, t_z=8760)
    est = Estrutura(
        nome="A", L=20, W=10, H=5, localizacao=Localizacao.isolada,
        tipo_construcao=TipoConstrucao.robusta, risco_incendio=RiscoIncendio.normal,
        providencias_incendio=ProvidenciaIncendio.nenhuma, n_t=100, zonas=[z],
    )
    return Projeto(nome="Proj X", N_G=4.0, estruturas=[est])


def test_salvar_e_carregar_roundtrip(tmp_path):
    p = _projeto()
    destino = tmp_path / "proj.json"
    salvar_projeto(p, destino)
    assert destino.exists()
    p2 = carregar_projeto(destino)
    assert p2.nome == "Proj X"
    assert p2.estruturas[0].zonas[0].superficie == TipoSuperficie.terra_concreto
    assert p2 == p


def test_carregar_aceita_str_e_path(tmp_path):
    p = _projeto()
    destino = tmp_path / "p.json"
    salvar_projeto(p, str(destino))
    assert carregar_projeto(str(destino)).nome == "Proj X"


def test_salvar_caminho_vazio_da_valueerror():
    import pytest
    with pytest.raises(ValueError):
        salvar_projeto(_projeto(), "")
    with pytest.raises(ValueError):
        salvar_projeto(_projeto(), "   ")


def test_salvar_cria_pastas_faltantes(tmp_path):
    destino = tmp_path / "sub" / "dir" / "p.json"
    salvar_projeto(_projeto(), destino)        # nao deve dar FileNotFoundError
    assert destino.exists()


def test_salvar_aplica_extensao_json(tmp_path):
    destino = salvar_projeto(_projeto(), str(tmp_path / "semext"))
    assert destino.suffix == ".json" and destino.exists()


def test_validar_caminho_remove_aspas(tmp_path):
    from spda.cli.persistencia import validar_caminho
    alvo = tmp_path / "x.json"
    assert validar_caminho(f'"{alvo}"') == alvo      # colado com aspas

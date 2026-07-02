from spda.app import analisar
from spda.model.enums import (
    Localizacao,
    NivelDPS,
    ProvidenciaIncendio,
    RiscoIncendio,
    TipoConstrucao,
    TipoSuperficie,
)
from spda.model.projeto import (
    Estrutura,
    Linha,
    Medidas,
    Projeto,
    SistemaInterno,
    Zona,
)


def test_sistema_interno_aceita_dps():
    s = SistemaInterno(nome="forca", U_W=2.5, dps=NivelDPS.II)
    assert s.dps is NivelDPS.II


def test_sistema_interno_dps_default_none():
    s = SistemaInterno(nome="dados", U_W=4.0)
    assert s.dps is None


def _projeto_um_sistema(dps_forca, dps_dados):
    sistemas = [
        SistemaInterno(nome="forca", U_W=2.5, dps=dps_forca),
        SistemaInterno(nome="dados", U_W=2.5, dps=dps_dados),
    ]
    zona = Zona(nome="Z", superficie=TipoSuperficie.terra_concreto, n_z=1,
                t_z=8760.0, sistemas_internos=sistemas)
    est = Estrutura(
        nome="E", L=20, W=10, H=6, localizacao=Localizacao.isolada,
        tipo_construcao=TipoConstrucao.robusta, risco_incendio=RiscoIncendio.normal,
        providencias_incendio=ProvidenciaIncendio.nenhuma,
        sistemas_criticos=True,  # D3 ativo para R_C/R_M entrarem em R1
        n_t=1, zonas=[zona], linhas=[Linha()],
    )
    return Projeto(nome="P", N_G=1.0, estruturas=[est])


def test_dps_por_sistema_distingue_forca_dados():
    forte = analisar(_projeto_um_sistema(NivelDPS.I, NivelDPS.I))
    fraco = analisar(_projeto_um_sistema(NivelDPS.IV, NivelDPS.IV))
    assert forte.estruturas[0].R1 < fraco.estruturas[0].R1


def test_rw_rz_zero_sem_sistemas():
    zona = Zona(nome="Z", superficie=TipoSuperficie.terra_concreto, n_z=1,
                t_z=8760.0, sistemas_internos=[])
    est = Estrutura(
        nome="E", L=20, W=10, H=6, localizacao=Localizacao.isolada,
        tipo_construcao=TipoConstrucao.robusta, risco_incendio=RiscoIncendio.normal,
        providencias_incendio=ProvidenciaIncendio.nenhuma,
        sistemas_criticos=True, n_t=1, zonas=[zona], linhas=[Linha()],
    )
    res = analisar(Projeto(nome="P", N_G=1.0, estruturas=[est]))
    z = res.estruturas[0].zonas[0]
    assert z.R_W == 0.0 and z.R_Z == 0.0 and z.R_C == 0.0 and z.R_M == 0.0


def test_medidas_nao_tem_dps_coordenado():
    assert "dps_coordenado" not in Medidas.model_fields

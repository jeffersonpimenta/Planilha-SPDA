import math

from spda.app import analisar, analisar_memoria
from spda.model.enums import (
    Localizacao, NivelDPS, ProvidenciaIncendio, RiscoIncendio, TipoConstrucao,
    TipoSuperficie, rotulo,
)
from spda.model.projeto import (
    Estrutura, Linha, Projeto, SistemaInterno, Zona,
)


def _projeto():
    sis = SistemaInterno(nome="forca", U_W=2.5, dps=NivelDPS.II)
    zona = Zona(nome="Z", superficie=TipoSuperficie.terra_concreto, n_z=2,
                t_z=8760.0, sistemas_internos=[sis])
    est = Estrutura(
        nome="E", L=20, W=10, H=6, localizacao=Localizacao.isolada,
        tipo_construcao=TipoConstrucao.robusta, risco_incendio=RiscoIncendio.normal,
        providencias_incendio=ProvidenciaIncendio.nenhuma, sistemas_criticos=True,
        n_t=5, zonas=[zona], linhas=[Linha()],
    )
    return Projeto(nome="P", N_G=1.5, estruturas=[est])


def test_memoria_captura_intermediarios():
    m = analisar_memoria(_projeto())
    me = m.estruturas[0]
    assert set(me.N_D.operandos) == {"N_G", "A_D", "C_D"}
    assert me.N_D.operandos["N_G"] == 1.5
    o = me.N_D.operandos
    assert math.isclose(me.N_D.resultado, o["N_G"] * o["A_D"] * o["C_D"] * 1e-6,
                        rel_tol=1e-12)
    mz = me.zonas[0]
    assert mz.sistemas[0].dps == rotulo(NivelDPS.II)
    assert mz.sistemas[0].P_SPD.resultado == 0.02


def test_resultado_projetado_bate_com_memoria():
    p = _projeto()
    res = analisar(p)
    mem = analisar_memoria(p)
    rz_res = res.estruturas[0].zonas[0]
    rz_mem = mem.estruturas[0].zonas[0]
    for comp in ("R_A", "R_B", "R_C", "R_M", "R_U", "R_V", "R_W", "R_Z"):
        assert math.isclose(getattr(rz_res, comp),
                            getattr(rz_mem, comp).resultado, rel_tol=1e-12)
    assert math.isclose(res.estruturas[0].R1, mem.estruturas[0].R1.resultado,
                        rel_tol=1e-12)


def test_p_ms_forcado_quando_uw_none_sem_operandos():
    # sistema sem U_W e com K_S3 < 1 (fiacao): P_MS forcado a 1.0, sem operandos.
    sis = SistemaInterno(nome="s", U_W=None, K_S3=0.2)
    zona = Zona(nome="Z", superficie=TipoSuperficie.terra_concreto, n_z=1,
                t_z=8760.0, sistemas_internos=[sis])
    est = Estrutura(nome="E", L=20, W=10, H=6, localizacao=Localizacao.isolada,
                    tipo_construcao=TipoConstrucao.robusta,
                    risco_incendio=RiscoIncendio.normal,
                    providencias_incendio=ProvidenciaIncendio.nenhuma,
                    sistemas_criticos=True, n_t=1, zonas=[zona], linhas=[Linha()])
    mem = analisar_memoria(Projeto(nome="P", N_G=1.5, estruturas=[est]))
    p_ms = mem.estruturas[0].zonas[0].sistemas[0].P_MS_i
    assert p_ms.resultado == 1.0
    assert p_ms.operandos == {}        # forcado: sem substituicao no memorial
    assert p_ms.origem is not None

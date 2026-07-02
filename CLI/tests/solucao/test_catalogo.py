from spda.solucao.catalogo import MEDIDAS, Medida
from spda.model.projeto import Estrutura, Zona, Medidas, SistemaInterno
from spda.model.enums import (
    Localizacao, TipoConstrucao, RiscoIncendio, ProvidenciaIncendio,
    TipoSuperficie, NivelProtecao, NivelDPS, ProtecaoToquePasso, rotulo,
)


def _est():
    z = Zona(nome="Z1", superficie=TipoSuperficie.terra_concreto, n_z=10, t_z=8760)
    return Estrutura(
        nome="A", L=20, W=10, H=5, localizacao=Localizacao.isolada,
        tipo_construcao=TipoConstrucao.robusta, risco_incendio=RiscoIncendio.normal,
        providencias_incendio=ProvidenciaIncendio.nenhuma, n_t=100, zonas=[z],
    )


def test_medidas_tem_quatro_escadas():
    ids = {m.id for m in MEDIDAS}
    assert ids == {"spda", "toque_passo", "dps", "incendio"}


def test_proximo_degrau_spda_sobe_um_nivel():
    spda = next(m for m in MEDIDAS if m.id == "spda")
    est = _est()
    assert spda.nivel_atual(est) == rotulo(None)
    novo = spda.aplicar_proximo(est)
    assert novo is not None
    est2, de, para = novo
    assert de == rotulo(None) and para == rotulo(NivelProtecao.IV)
    assert est2.nivel_spda == NivelProtecao.IV
    # original intacto (copia profunda)
    assert est.nivel_spda is None


def test_proximo_degrau_no_topo_retorna_none():
    spda = next(m for m in MEDIDAS if m.id == "spda")
    est = _est()
    est.nivel_spda = NivelProtecao.I
    assert spda.aplicar_proximo(est) is None


def test_dps_aplica_em_todas_as_zonas():
    dps = next(m for m in MEDIDAS if m.id == "dps")
    est = _est()
    est.zonas[0].sistemas_internos = [SistemaInterno(nome="S1", U_W=2.5)]
    est.zonas.append(Zona(nome="Z2", superficie=TipoSuperficie.terra_concreto,
                          n_z=5, t_z=8760,
                          sistemas_internos=[SistemaInterno(nome="S2", U_W=2.5)]))
    est2, de, para = dps.aplicar_proximo(est)
    assert para == rotulo(NivelDPS.IV)
    assert all(s.dps == NivelDPS.IV
               for z in est2.zonas for s in z.sistemas_internos)


def test_valor_fora_da_escada_nao_quebra_estrutura():
    # nivel_spda fora da escada discreta (I_descida_natural) -> sem crash;
    # nivel_atual mostra o valor real e aplicar_proximo nao avanca.
    spda = next(m for m in MEDIDAS if m.id == "spda")
    est = _est()
    est.nivel_spda = NivelProtecao.I_descida_natural
    assert spda.nivel_atual(est) == rotulo(NivelProtecao.I_descida_natural)
    assert spda.aplicar_proximo(est) is None


def test_nivel_spda_nenhum_e_sinonimo_de_None():
    # NivelProtecao.nenhum (P_B=1.0) deve ser tratado como degrau base ->
    # a medida SPDA ainda e proposta (sobe para IV).
    spda = next(m for m in MEDIDAS if m.id == "spda")
    est = _est()
    est.nivel_spda = NivelProtecao.nenhum
    assert spda.nivel_atual(est) == rotulo(None)
    novo = spda.aplicar_proximo(est)
    assert novo is not None
    est2, de, para = novo
    assert de == rotulo(None) and para == rotulo(NivelProtecao.IV)
    assert est2.nivel_spda == NivelProtecao.IV


def test_valor_fora_da_escada_nao_quebra_zona():
    # zona com medida fora da escada (malha_equipotencial) -> sem crash e
    # nao sobrescreve cegamente todas as zonas.
    tp = next(m for m in MEDIDAS if m.id == "toque_passo")
    est = _est()
    est.zonas[0].medidas.protecao_toque_passo = ProtecaoToquePasso.malha_equipotencial
    assert tp.nivel_atual(est) == rotulo(ProtecaoToquePasso.malha_equipotencial)
    assert tp.aplicar_proximo(est) is None

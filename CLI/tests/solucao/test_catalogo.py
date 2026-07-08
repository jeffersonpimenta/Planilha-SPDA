import pytest

from spda.solucao.catalogo import MEDIDAS, Medida, por_id
from spda.model.projeto import Estrutura, Zona, Medidas, SistemaInterno, Linha, Trecho
from spda.model.enums import (
    ClasseBlindagemRS, Localizacao, NivelDPS, NivelProtecao, ProvidenciaIncendio,
    ProtecaoToquePasso, RiscoIncendio, TipoConstrucao, TipoLinhaExterna,
    TipoSuperficie, rotulo,
)


def _est():
    z = Zona(nome="Z1", superficie=TipoSuperficie.terra_concreto, n_z=10, t_z=8760)
    return Estrutura(
        nome="A", L=20, W=10, H=5, localizacao=Localizacao.isolada,
        tipo_construcao=TipoConstrucao.robusta, risco_incendio=RiscoIncendio.normal,
        providencias_incendio=ProvidenciaIncendio.nenhuma, n_t=100, zonas=[z],
    )


def test_medidas_tem_nove_escadas():
    ids = {m.id for m in MEDIDAS}
    assert ids == {
        "spda", "toque_passo", "dps", "incendio",
        "ligacao_eq", "toque_entrada", "blindagem_linha",
        "fiacao", "blindagem_espacial",
    }


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


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def estrutura_sem_spda():
    z = Zona(nome="Z1", superficie=TipoSuperficie.terra_concreto, n_z=10, t_z=8760)
    return Estrutura(
        nome="A", L=20, W=10, H=6, localizacao=Localizacao.isolada,
        tipo_construcao=TipoConstrucao.simples, risco_incendio=RiscoIncendio.normal,
        providencias_incendio=ProvidenciaIncendio.nenhuma, n_t=20, zonas=[z],
    )


# ---------------------------------------------------------------------------
# Novos testes (Task 2)
# ---------------------------------------------------------------------------

def _medida(mid):
    return por_id()[mid]


def test_por_id_tem_medidas_basicas():
    ids = set(por_id())
    assert {"spda", "toque_passo", "dps", "incendio"} <= ids


def test_definir_nivel_spda_pula_degraus(estrutura_sem_spda):
    m = _medida("spda")
    assert m.indice_atual(estrutura_sem_spda) == 0
    est2 = m.definir_nivel(estrutura_sem_spda, 3)  # nenhum -> II direto
    assert est2.nivel_spda == NivelProtecao.II
    assert estrutura_sem_spda.nivel_spda is None  # original intacto


def test_degrau_str_roundtrip():
    for m in MEDIDAS:
        for i in range(len(m.escada)):
            assert m.indice_de_degrau_str(m.degrau_str(i)) == i


def test_rotulos_escada_tem_um_por_degrau():
    for m in MEDIDAS:
        assert len(m.rotulos_escada()) == len(m.escada)


def test_toque_passo_componentes_so_R_A():
    assert _medida("toque_passo").componentes == ("R_A",)


# ---------------------------------------------------------------------------
# Helpers compartilhados (Tasks 3-5)
# ---------------------------------------------------------------------------

def _com_linha(est, **kw):
    est = est.model_copy(deep=True)
    est.linhas = [Linha(trechos=[Trecho(L_L=500)], **kw)]
    return est


def _com_sistema(est, **kw):
    est = est.model_copy(deep=True)
    est.zonas[0].sistemas_internos = [SistemaInterno(nome="S", U_W=2.5, **kw)]
    return est


# ---------------------------------------------------------------------------
# Task 3 — ligacao_eq (P_EB) e toque_entrada (P_TU)
# ---------------------------------------------------------------------------

def test_ligacao_eq_avanca_nivel_eb(estrutura_sem_spda):
    m = _medida("ligacao_eq")
    est = _com_linha(estrutura_sem_spda)          # nivel_eb=None -> degrau 0
    assert m.indice_atual(est) == 0
    est2 = m.definir_nivel(est, 2)                # None -> III
    assert est2.linhas[0].nivel_eb == NivelDPS.III


def test_ligacao_eq_sem_linhas_nao_aplicavel(estrutura_sem_spda):
    assert _medida("ligacao_eq").indice_atual(estrutura_sem_spda) is None


def test_toque_entrada_avanca(estrutura_sem_spda):
    m = _medida("toque_entrada")
    est = _com_linha(estrutura_sem_spda)
    assert m.indice_atual(est) == 0
    est2 = m.definir_nivel(est, 1)
    assert est2.linhas[0].protecao_toque_entrada == ProtecaoToquePasso.avisos


def test_toque_entrada_fora_da_escada(estrutura_sem_spda):
    est = _com_linha(
        estrutura_sem_spda,
        protecao_toque_entrada=ProtecaoToquePasso.malha_equipotencial)
    assert _medida("toque_entrada").indice_atual(est) is None


# ---------------------------------------------------------------------------
# Task 4 — blindagem_linha (P_LD/C_LI)
# ---------------------------------------------------------------------------

def test_blindagem_linha_avanca_par(estrutura_sem_spda):
    m = _medida("blindagem_linha")
    est = _com_linha(estrutura_sem_spda)  # aerea_nao_blindada / nao_blindada
    assert m.indice_atual(est) == 0
    est2 = m.definir_nivel(est, 3)
    li = est2.linhas[0]
    assert li.tipo_externa == TipoLinhaExterna.blindada_interligada
    assert li.classe_blindagem == ClasseBlindagemRS.rs_ate_1


def test_blindagem_linha_fibra_fica_intocada(estrutura_sem_spda):
    est = _com_linha(estrutura_sem_spda,
                     tipo_externa=TipoLinhaExterna.fibra_optica)
    m = _medida("blindagem_linha")
    assert m.indice_atual(est) is None  # unica linha ja e melhor que a escada


def test_blindagem_linha_par_inconsistente_fora_da_escada(estrutura_sem_spda):
    # classe RS indica blindagem interligada, mas tipo_externa nao e
    # blindada_interligada -> par inconsistente, fora da escada (nao
    # sobrescreve cegamente).
    est = _com_linha(estrutura_sem_spda,
                     classe_blindagem=ClasseBlindagemRS.rs_1_5)
    assert _medida("blindagem_linha").indice_atual(est) is None


def test_blindagem_linha_downgrade_reseta_par(estrutura_sem_spda):
    # definir_nivel(0) apos upgrade deve voltar a um par consistente
    # (sem blindagem E sem credito de C_LI).
    m = _medida("blindagem_linha")
    est = _com_linha(estrutura_sem_spda)
    est2 = m.definir_nivel(est, 3)
    est3 = m.definir_nivel(est2, 0)
    li = est3.linhas[0]
    assert li.tipo_externa == TipoLinhaExterna.aerea_nao_blindada
    assert li.classe_blindagem == ClasseBlindagemRS.nao_blindada


def test_blindagem_linha_mista_preserva_fibra(estrutura_sem_spda):
    est = estrutura_sem_spda.model_copy(deep=True)
    est.linhas = [
        Linha(trechos=[Trecho(L_L=500)]),
        Linha(trechos=[Trecho(L_L=500)],
              tipo_externa=TipoLinhaExterna.fibra_optica),
    ]
    m = _medida("blindagem_linha")
    assert m.indice_atual(est) == 0     # so a linha comum conta
    est2 = m.definir_nivel(est, 1)
    assert est2.linhas[0].classe_blindagem == ClasseBlindagemRS.rs_5_20
    assert est2.linhas[1].tipo_externa == TipoLinhaExterna.fibra_optica


# ---------------------------------------------------------------------------
# Task 5 — fiacao (K_S3) e blindagem_espacial (K_S2)
# ---------------------------------------------------------------------------

def test_fiacao_avanca_ks3(estrutura_sem_spda):
    m = _medida("fiacao")
    est = _com_sistema(estrutura_sem_spda)        # K_S3 = 1.0 -> degrau 0
    assert m.indice_atual(est) == 0
    est2 = m.definir_nivel(est, 2)
    assert est2.zonas[0].sistemas_internos[0].K_S3 == 0.2


def test_fiacao_valor_custom_fora_da_escada(estrutura_sem_spda):
    est = _com_sistema(estrutura_sem_spda, K_S3=0.37)
    assert _medida("fiacao").indice_atual(est) is None


def test_fiacao_sem_sistemas_nao_aplicavel(estrutura_sem_spda):
    assert _medida("fiacao").indice_atual(estrutura_sem_spda) is None


def test_blindagem_espacial_avanca_ks2(estrutura_sem_spda):
    m = _medida("blindagem_espacial")
    est = _com_sistema(estrutura_sem_spda)        # K_S2 = 1.0 -> degrau 0
    assert m.indice_atual(est) == 0
    est2 = m.definir_nivel(est, 1)
    assert est2.zonas[0].sistemas_internos[0].K_S2 == 0.24


def test_degrau_str_float():
    m = _medida("fiacao")
    assert m.degrau_str(2) == "0.2"
    assert m.indice_de_degrau_str("0.2") == 2
    assert m.degrau_str(4) == "0.0001"

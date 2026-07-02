from spda.calc import economico as eco


def test_custo_perdas_d8():
    # D.8: C_L = R4 x c_t (com medidas: C_RL = R'4 x c_t, eq. D.10).
    assert eco.custo_perdas(R4=3e-4, c_t=1_000_000) == 3e-4 * 1_000_000


def test_custo_medidas_d11():
    # D.11: C_PM = C_P x (i + a + m).
    v = eco.custo_medidas(C_P=10_000, i=0.05, a=0.05, m=0.01)
    assert abs(v - 10_000 * 0.11) < 1e-9


def test_poupanca_d12():
    # D.12: S_M = C_L - (C_PM + C_RL).
    assert eco.poupanca(C_L=1000, C_PM=300, C_RL=200) == 500


def test_viabilidade_justificada():
    # Protecao justificada se S_M > 0 (D.12).
    assert eco.viabilidade(C_L=1000, C_RL=200, C_PM=300) is True


def test_viabilidade_nao_justificada():
    assert eco.viabilidade(C_L=400, C_RL=200, C_PM=300) is False


def test_viabilidade_empate_nao_justifica():
    # S_M = 0 nao justifica (D.12 exige S_M > 0 estrito).
    assert eco.viabilidade(C_L=500, C_RL=200, C_PM=300) is False

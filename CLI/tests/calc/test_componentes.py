from spda.calc import componentes as comp


def test_componente_generico():
    # R = N * P * L
    assert comp.componente(N=2.0, P=0.5, L=0.1) == 2.0 * 0.5 * 0.1


def test_R_linha_soma_trechos():
    # cada trecho contribui (N+N_DJ)*P*L; soma sobre trechos
    trechos = [(0.16, 0.0), (0.08, 0.0)]  # (N_L, N_DJ) por trecho
    r = comp.R_linha(trechos, P=0.05, L=0.1)
    esperado = (0.16 * 0.05 * 0.1) + (0.08 * 0.05 * 0.1)
    assert abs(r - esperado) < 1e-18


def test_R_linha_com_NDJ():
    trechos = [(0.16, 0.02)]
    r = comp.R_linha(trechos, P=0.05, L=0.1)
    assert abs(r - ((0.16 + 0.02) * 0.05 * 0.1)) < 1e-18

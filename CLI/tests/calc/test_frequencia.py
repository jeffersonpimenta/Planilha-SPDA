from spda.calc import frequencia as freq


def test_F_B():
    assert freq.F_B(N_D=0.01, P_B=0.05) == 0.01 * 0.05


def test_F_C():
    assert freq.F_C(N_D=0.01, P_C=0.02) == 0.01 * 0.02


def test_F_M():
    assert freq.F_M(N_M=3.0, P_M=0.0625) == 3.0 * 0.0625


def test_F_V():
    # Tabela 7: F_V = (N_L + N_DJ) x P_EB (S3, corrente impulsiva direta).
    assert freq.F_V(N_L_total=0.16, P_EB=0.05) == 0.16 * 0.05


def test_F_zona_soma():
    v = freq.F_zona(F_C=1e-3, F_M=2e-3, F_V=1e-4, F_W=1e-4, F_Z=1e-4)
    assert abs(v - (1e-3 + 2e-3 + 1e-4 + 1e-4 + 1e-4)) < 1e-18

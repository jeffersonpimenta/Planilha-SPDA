from spda.calc import probabilidades as pr


def test_pior_caso_retorna_o_maior():
    # 6.9.1.2a / 7.4.1.2a: R_W/R_Z e F_W/F_Z usam o valor unico mais restritivo.
    assert pr.pior_caso([0.02, 0.05, 0.01]) == 0.05


def test_pior_caso_vazio_e_zero():
    # Sem sistemas internos -> componente nula (consistente com combinar_sistemas).
    assert pr.pior_caso([]) == 0.0


def test_P_A():
    assert pr.P_A(P_TA=0.1, P_B=0.05) == 0.1 * 0.05


def test_P_C():
    assert pr.P_C(P_SPD=0.05, C_LD=1) == 0.05


def test_P_MS():
    # (0.5 * 0.5 * 1 * 1)^2 = 0.0625
    assert pr.P_MS(0.5, 0.5, 1, 1) == 0.0625


def test_P_U():
    assert pr.P_U(P_TU=1, P_EB=0.05, P_LD=1, C_LD=1) == 0.05


def test_P_V():
    # PV = PEB * PLD * CLD (eq. B.9)
    assert pr.P_V(P_EB=0.05, P_LD=0.8, C_LD=1) == 0.05 * 0.8 * 1


def test_fator_KS4():
    assert pr.fator_KS4(2.5) == 0.4          # 1/2.5
    assert pr.fator_KS4(0.5) == 1.0          # cap em 1.0 para U_W < 1 kV


def test_P_W():
    assert pr.P_W(P_SPD=0.05, P_LD=1, C_LD=1) == 0.05


def test_P_Z():
    assert pr.P_Z(P_SPD=0.05, P_LI=1, C_LI=0.2) == 0.05 * 1 * 0.2


def test_combinar_sistemas():
    # 1 - (1-0.1)(1-0.1) = 0.19
    assert abs(pr.combinar_sistemas([0.1, 0.1]) - 0.19) < 1e-12


def test_combinar_vazio_eh_zero():
    assert pr.combinar_sistemas([]) == 0.0

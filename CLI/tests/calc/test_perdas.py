from spda.calc import perdas


def test_L_choque_D1():
    # r_t*L_T*(n_z/n_t)*(t_z/8760)*r_s
    v = perdas.L_choque(r_t=1e-2, L_T=1e-2, n_z=50, n_t=100, t_z=8760, r_s=1)
    assert abs(v - (1e-2 * 1e-2 * 0.5 * 1 * 1)) < 1e-18


def test_L_fisico_D2():
    v = perdas.L_fisico(r_p=1, r_f=0.1, h_z=1, L_F=1e-2, n_z=50, n_t=100,
                        t_z=8760, r_s=1)
    assert abs(v - (1 * 0.1 * 1 * 1e-2 * 0.5 * 1 * 1)) < 1e-18


def test_L_sistemas_D3():
    v = perdas.L_sistemas(L_O=1e-3, n_z=50, n_t=100, t_z=8760, r_s=1)
    assert abs(v - (1e-3 * 0.5 * 1 * 1)) < 1e-18


def test_L3_patrimonio():
    # C.7: L_B = r_p*r_f*L_F*(c_z/c_t), limitado a 1 (sem h_z).
    v = perdas.L3_patrimonio(r_p=1, r_f=0.1, L_F=0.1, c_z=200, c_t=1000)
    assert abs(v - (1 * 0.1 * 0.1 * 0.2)) < 1e-18


def test_L3_limitada_a_um():
    v = perdas.L3_patrimonio(r_p=1, r_f=1, L_F=1, c_z=5000, c_t=1000)
    assert v == 1.0


def test_L4_choque():
    # D.1: L_A = r_t * L_T * (c_a / c_t).
    v = perdas.L4_choque(r_t=1e-2, L_T=1e-2, c_a=100, c_t=1000)
    assert abs(v - (1e-2 * 1e-2 * 0.1)) < 1e-18


def test_L4_fisico():
    # D.3: L_B = r_p*r_f*L_F*(c_a+c_b+c_c+c_s)/c_t (sem h_z).
    v = perdas.L4_fisico(r_p=1, r_f=0.1, L_F=1e-2, c_a=0, c_b=300, c_c=200,
                         c_s=0, c_t=1000)
    assert abs(v - (1 * 0.1 * 1e-2 * 0.5)) < 1e-18


def test_L4_sistemas():
    # D.4: L_C = L_O * (c_s / c_t).
    v = perdas.L4_sistemas(L_O=1e-3, c_s=200, c_t=1000)
    assert abs(v - (1e-3 * 0.2)) < 1e-18


def test_L4_sistemas_ct_zero():
    assert perdas.L4_sistemas(L_O=1e-3, c_s=200, c_t=0) == 0.0


# Nota das Eqs D.1-D.4 (norma:2635): com R_T representativo, as razoes c/c_t = 1.

def test_L4_choque_representativo_ignora_razao():
    v = perdas.L4_choque(r_t=1e-2, L_T=1e-2, c_a=100, c_t=1000, representativo=True)
    assert abs(v - (1e-2 * 1e-2)) < 1e-18


def test_L4_choque_representativo_sem_animais_e_zero():
    # Tabela C.12: L_T so se aplica onde ha animais; sem animais, D1 nao contribui.
    v = perdas.L4_choque(r_t=1e-2, L_T=1e-2, representativo=True, animais=False)
    assert v == 0.0


def test_L4_fisico_representativo_ignora_razao():
    v = perdas.L4_fisico(r_p=1, r_f=0.1, L_F=1e-2, c_a=0, c_b=300, c_c=200, c_s=0,
                         c_t=1000, representativo=True)
    assert abs(v - (1 * 0.1 * 1e-2)) < 1e-18


def test_L4_sistemas_representativo_ignora_razao():
    v = perdas.L4_sistemas(L_O=1e-3, c_s=200, c_t=1000, representativo=True)
    assert abs(v - 1e-3) < 1e-18

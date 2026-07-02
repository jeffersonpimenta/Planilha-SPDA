import math
from spda.calc import eventos


def test_area_AD():
    # L=20, W=10, H=5 -> 200 + 6*5*30 + 9*pi*25
    esperado = 200 + 6 * 5 * 30 + 9 * math.pi * 25
    assert eventos.area_AD(20, 10, 5) == esperado


def test_area_AD_complexa_saliencia_domina():
    # A.2.1.3.2: maior entre A_D(H_min) (eq. A.1) e A'_D = pi*(3*H_P)^2 (eq. A.2).
    a = eventos.area_AD_complexa(20, 10, H_min=3, H_max=8)
    assert a == max(eventos.area_AD(20, 10, 3), math.pi * (3 * 8) ** 2)
    assert a == math.pi * (3 * 8) ** 2  # aqui o circulo da saliencia domina


def test_area_AD_complexa_hmin_domina():
    # Estrutura larga e baixa: A_D(H_min) pela eq. A.1 supera o circulo da saliencia.
    a = eventos.area_AD_complexa(500, 400, H_min=10, H_max=12)
    assert a == eventos.area_AD(500, 400, 10)


def test_N_D():
    a = eventos.area_AD(20, 10, 5)
    assert eventos.N_D(N_G=4, A_D=a, C_D=1) == 4 * a * 1e-6


def test_N_DJ_aplica_C_T():
    a = eventos.area_AD(20, 10, 5)
    # com trafo AT/BT (C_T=0.2) o N_DJ e 1/5 do caso BT/sinal (C_T=1).
    assert eventos.N_DJ(N_G=4, A_DJ=a, C_DJ=1, C_T=0.2) == 4 * a * 1 * 0.2 * 1e-6


def test_area_AM():
    esperado = 1000 * (20 + 10) + math.pi * 500 ** 2
    assert eventos.area_AM(20, 10) == esperado


def test_area_AL_aerea():
    assert eventos.area_AL(1000) == 40 * 1000


def test_area_AL_solo_resistivo():
    # rho=900 (>400) -> 0.6*sqrt(900)*L_L = 0.6*30*1000
    assert eventos.area_AL(1000, rho=900) == 0.6 * math.sqrt(900) * 1000


def test_area_AL_solo_baixo_nao_altera():
    # rho<=400 mantem 40*L_L
    assert eventos.area_AL(1000, rho=200) == 40 * 1000


def test_N_L():
    a = eventos.area_AL(1000)
    assert eventos.N_L(4, a, C_I=1, C_E=1, C_T=1) == 4 * a * 1e-6


def test_area_AI_e_N_I():
    assert eventos.area_AI(1000) == 4000 * 1000
    a = eventos.area_AI(1000)
    assert eventos.N_I(4, a, C_I=0.5, C_E=0.1, C_T=1) == 4 * a * 0.5 * 0.1 * 1 * 1e-6

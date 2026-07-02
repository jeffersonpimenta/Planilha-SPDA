from spda.relatorio.formato import fmt, substituir


def test_fmt_zero():
    assert fmt(0) == "0"


def test_fmt_cientifico_para_pequeno():
    assert fmt(1.25e-5) == "1.250e-05"


def test_fmt_cientifico_para_grande():
    assert fmt(123456.0) == "1.235e+05"


def test_fmt_decimal_intermediario():
    assert fmt(0.5) == "0.5"
    assert fmt(2.5) == "2.5"


def test_substituir_troca_nomes_por_valores():
    forma = "N_G*A_D*C_D*1e-6"
    out = substituir(forma, {"N_G": 1.5, "A_D": 1000.0, "C_D": 0.5})
    assert out == "1.5*1000*0.5*1e-6"


def test_substituir_nao_confunde_prefixos():
    forma = "P_EB*P_LD*C_LD"
    out = substituir(forma, {"P_EB": 0.05, "P_LD": 0.9, "C_LD": 1.0})
    assert out == "0.05*0.9*1"


def test_substituir_sem_operandos_retorna_forma():
    assert substituir("40*L_L", {}) == "40*L_L"

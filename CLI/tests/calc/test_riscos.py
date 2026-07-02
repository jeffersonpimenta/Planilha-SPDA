from spda.calc import riscos
from spda.model.resultado import ResultadoZona


def _zona(**kw):
    base = dict(nome="z", R_A=1e-6, R_B=2e-6, R_C=0, R_M=0, R_U=1e-6,
               R_V=1e-6, R_W=0, R_Z=0, R_B3=0.1, R_V3=0.05, R4_total=3e-4)
    base.update(kw)
    return ResultadoZona(**base)


def test_R1_soma_componentes_sem_flags():
    z = _zona()
    # sem flags: ignora R_C, R_M, R_W, R_Z
    r1 = riscos.R1([z], incluir_d3_vida=False)
    assert abs(r1 - (1e-6 + 2e-6 + 1e-6 + 1e-6)) < 1e-18


def test_R1_com_flags_inclui_d3():
    z = _zona(R_C=5e-7, R_M=5e-7, R_W=0, R_Z=0)
    r1 = riscos.R1([z], incluir_d3_vida=True)
    assert abs(r1 - (1e-6 + 2e-6 + 5e-7 + 5e-7 + 1e-6 + 1e-6)) < 1e-18


def test_R3():
    z = _zona()
    assert abs(riscos.R3([z]) - (0.1 + 0.05)) < 1e-18


def test_R4():
    z = _zona()
    assert abs(riscos.R4([z]) - 3e-4) < 1e-18


def test_excede():
    assert riscos.excede(2e-5, 1e-5) is True
    assert riscos.excede(5e-6, 1e-5) is False


def test_dominantes_ordena_desc():
    z = _zona(R_A=1e-6, R_B=5e-6, R_U=2e-6)
    dom = riscos.dominantes_R1([z], incluir_d3_vida=False)
    assert dom[0][0] == "R_B"
    assert dom[0][1] == 5e-6
    assert [n for n, _ in dom][:3] == ["R_B", "R_U", "R_A"]

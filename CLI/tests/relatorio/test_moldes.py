import math

from spda.app import analisar_memoria
from spda.model.enums import (
    Localizacao, NivelDPS, ProvidenciaIncendio, RiscoIncendio, TipoConstrucao,
    TipoSuperficie,
)
from spda.model.memoria import Operacao
from spda.model.projeto import (
    Estrutura, EstruturaAdjacente, Linha, Projeto, SistemaInterno, Trecho, Zona,
)
from spda.relatorio.moldes import MOLDES, EVAL_GLOBAIS, renderizar_operacao


def _memoria_rica():
    sis = SistemaInterno(nome="forca", U_W=2.5, dps=NivelDPS.II)
    # 2o sistema sem U_W e com K_S3<1: P_MS e forcado a 1 (sem operandos) -- a
    # consistencia deve pula-lo, nao tratar como formula.
    sis2 = SistemaInterno(nome="dados", U_W=None, K_S3=0.2)
    zona = Zona(nome="Z", superficie=TipoSuperficie.terra_concreto, n_z=2,
                t_z=4000.0, sistemas_internos=[sis, sis2],
                c_z=1000.0, c_a=10.0, c_b=500.0, c_c=400.0, c_s=90.0)
    linha = Linha(adjacente=EstruturaAdjacente(L_J=10, W_J=10, H_J=3),
                  trechos=[Trecho(L_L=800.0), Trecho(L_L=500.0, rho=600.0)])
    est = Estrutura(
        nome="E", L=20, W=10, H=6, localizacao=Localizacao.isolada,
        tipo_construcao=TipoConstrucao.robusta, risco_incendio=RiscoIncendio.normal,
        providencias_incendio=ProvidenciaIncendio.nenhuma, sistemas_criticos=True,
        c_t=2000.0, n_t=5, zonas=[zona], linhas=[linha])
    return analisar_memoria(Projeto(nome="P", N_G=1.5, estruturas=[est]))


def _todas_operacoes(mem):
    achados = []

    def visita(obj):
        if isinstance(obj, Operacao):
            achados.append(obj)
            return
        if isinstance(obj, dict):
            for v in obj.values():
                visita(v)
            return
        if isinstance(obj, (list, tuple)):
            for v in obj:
                visita(v)
            return
        campos = getattr(obj, "__dict__", None)
        if campos:
            for v in campos.values():
                visita(v)

    visita(mem)
    return achados


def _memoria_representativa():
    zona = Zona(nome="Z", superficie=TipoSuperficie.terra_concreto, n_z=2,
                t_z=4000.0, c_a=10.0, c_b=500.0, c_c=400.0, c_s=90.0)
    est = Estrutura(
        nome="E", L=20, W=10, H=6, localizacao=Localizacao.isolada,
        tipo_construcao=TipoConstrucao.robusta, risco_incendio=RiscoIncendio.normal,
        providencias_incendio=ProvidenciaIncendio.nenhuma, c_t=2000.0, n_t=5,
        zonas=[zona], linhas=[Linha()])
    return analisar_memoria(
        Projeto(nome="P", N_G=1.5, estruturas=[est], r4_representativo=True))


def _checar_consistencia(mem):
    checados = 0
    for op in _todas_operacoes(mem):
        if op.simbolo in MOLDES and op.operandos:
            forma = MOLDES[op.simbolo](op.operandos)
            valor = eval(forma, dict(EVAL_GLOBAIS), dict(op.operandos))
            assert math.isclose(valor, op.resultado, rel_tol=1e-9, abs_tol=1e-18), (
                f"{op.simbolo}: forma={forma} valor={valor} != {op.resultado}")
            checados += 1
    return checados


def test_consistencia_moldes_reproduz_resultado():
    assert _checar_consistencia(_memoria_rica()) >= 10


def test_consistencia_moldes_r4_representativo():
    # Com razoes = 1, os moldes L4 caem para o produto sem c/c_t e ainda batem.
    assert _checar_consistencia(_memoria_representativa()) >= 10


def test_renderizar_operacao_com_substituicao():
    op = Operacao(simbolo="N_D", eq="A.2",
                  operandos={"N_G": 1.5, "A_D": 1000.0, "C_D": 0.5},
                  resultado=7.5e-4)
    eqb = renderizar_operacao(op)
    assert eqb.forma_simbolica == "N_D = N_G*A_D*C_D*1e-6"
    assert eqb.substituicao == "1.5*1000*0.5*1e-6"
    assert eqb.resultado == "7.500e-04"


def test_renderizar_operacao_lookup_sem_molde():
    op = Operacao(simbolo="C_D", eq="Tabela A.1", operandos={}, resultado=0.5,
                  origem="isolada")
    eqb = renderizar_operacao(op)
    assert eqb.forma_simbolica is None
    assert eqb.substituicao is None
    assert eqb.resultado == "0.5"
    assert eqb.origem == "isolada"

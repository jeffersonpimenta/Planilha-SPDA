from spda.model.memoria import (
    Memoria, MemoriaEstrutura, MemoriaZona, Operacao,
)


def test_operacao_guarda_operandos_e_resultado():
    op = Operacao(simbolo="N_D", eq="A.2",
                  operandos={"N_G": 2.5, "A_D": 1000.0, "C_D": 0.5},
                  resultado=1.25e-3)
    assert op.simbolo == "N_D"
    assert op.operandos["A_D"] == 1000.0
    assert op.resultado == 1.25e-3
    assert op.origem is None


def test_operacao_lookup_com_origem():
    op = Operacao(simbolo="C_D", eq="Tabela A.1", operandos={}, resultado=0.5,
                  origem="isolada")
    assert op.origem == "isolada"


def test_memoria_aninha_estrutura_zona():
    z = MemoriaZona(nome="Z", n_z=1, t_z=8760.0)
    e = MemoriaEstrutura(nome="E", entradas={"L": 20.0}, zonas=[z])
    m = Memoria(projeto="P", rt={"R1": 1e-5}, estruturas=[e])
    assert m.estruturas[0].zonas[0].nome == "Z"

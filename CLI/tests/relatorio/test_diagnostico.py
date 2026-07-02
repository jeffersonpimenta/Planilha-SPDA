from spda.model.memoria import Memoria, MemoriaEstrutura, Operacao
from spda.relatorio.diagnostico import gerar_diagnostico
from spda.relatorio.documento import Paragrafo, Titulo


def _op(simbolo, resultado):
    return Operacao(eq="X", simbolo=simbolo, resultado=resultado)


def _mem(nome="E1", r1=1e-6, dominantes=None):
    me = MemoriaEstrutura(nome=nome, R1=_op("R1", r1),
                          dominantes=dominantes or [])
    return Memoria(projeto="P", rt={"R1": 1e-5, "R3": 1e-4, "R4": 1e-3},
                   ft=1.0, estruturas=[me])


def test_diagnostico_tem_titulo_de_secao():
    blocos = gerar_diagnostico(_mem())
    assert isinstance(blocos[0], Titulo) and blocos[0].nivel == 2


def test_estrutura_adequada_quando_r1_abaixo_do_limite():
    blocos = gerar_diagnostico(_mem(r1=1e-6))
    texto = " ".join(b.texto for b in blocos if isinstance(b, Paragrafo))
    assert "ADEQUADA" in texto and "INADEQUADA" not in texto


def test_estrutura_inadequada_quando_r1_excede():
    blocos = gerar_diagnostico(_mem(r1=1e-3))
    texto = " ".join(b.texto for b in blocos if isinstance(b, Paragrafo))
    assert "INADEQUADA" in texto


def test_dominantes_sugerem_onde_atuar():
    blocos = gerar_diagnostico(_mem(r1=1e-3, dominantes=[("R_B", 9e-4),
                                                         ("R_A", 1e-4)]))
    texto = " ".join(b.texto for b in blocos if isinstance(b, Paragrafo))
    assert "R_B" in texto and "SPDA" in texto

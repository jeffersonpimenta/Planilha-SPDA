from spda.model.identificacao import Identificacao
from spda.model.memoria import (
    Memoria, MemoriaEstrutura, MemoriaZona, MemoriaSistemaInterno, Operacao,
)
from spda.relatorio.notas import gerar_notas


def _op(simbolo, resultado):
    return Operacao(eq="X", simbolo=simbolo, resultado=resultado)


def _est(nome="E1", r1=1e-6, r3=0.0, r4=0.0, f=0.0, sistemas=None):
    zona = MemoriaZona(nome="Z1", sistemas=sistemas or [])
    return MemoriaEstrutura(
        nome=nome, R1=_op("R1", r1), R3=_op("R3", r3),
        R4=_op("R4", r4), F=_op("F", f), zonas=[zona],
    )


def _mem(estruturas, identificacao=None, cidade="Cidade X"):
    return Memoria(
        projeto="P", cidade=cidade, identificacao=identificacao,
        rt={"R1": 1e-5, "R3": 1e-4, "R4": 1e-3},
        estruturas=estruturas,
    )


def test_sem_identificacao_gera_aviso():
    notas = gerar_notas(_mem([_est()]))
    assert any(n.nivel == "aviso" and "identificacao" in n.texto.lower()
               for n in notas)


def test_identificacao_incompleta_lista_campos_faltantes():
    ident = Identificacao(responsavel="Eng", art="123")  # falta registro/data
    notas = gerar_notas(_mem([_est()], identificacao=ident))
    aviso = next(n for n in notas if n.nivel == "aviso" and "assinatura" in n.texto)
    assert "registro CREA" in aviso.texto
    assert "data" in aviso.texto


def test_identificacao_completa_nao_gera_aviso_de_assinatura():
    ident = Identificacao(responsavel="Eng", art="123", registro="CREA-SP 1",
                          data="2026-07-01")
    notas = gerar_notas(_mem([_est()], identificacao=ident))
    assert not any(n.nivel == "aviso" for n in notas)


def test_cidade_ausente_gera_aviso():
    notas = gerar_notas(_mem([_est()], cidade=""))
    assert any(n.nivel == "aviso" and "Cidade" in n.texto for n in notas)


def test_r1_excedido_gera_critico():
    notas = gerar_notas(_mem([_est(r1=1e-3)]))  # > rt 1e-5
    assert any(n.nivel == "critico" and "R1" in n.texto for n in notas)


def test_nenhum_risco_excede_gera_info():
    notas = gerar_notas(_mem([_est()]))
    assert any(n.nivel == "info" and "limites" in n.texto for n in notas)


def test_uw_e_dps_ausentes_geram_info():
    sis = MemoriaSistemaInterno(nome="Sis", U_W=None, dps=None)
    notas = gerar_notas(_mem([_est(sistemas=[sis])]))
    textos = [n.texto for n in notas if n.nivel == "info"]
    assert any("U_W desconhecido" in t for t in textos)
    assert any("sem DPS coordenado" in t for t in textos)


def test_r4_metodo_representativo_gera_info():
    mem = _mem([_est(r4=5e-4)])
    mem.r4_representativo = True
    textos = [n.texto for n in gerar_notas(mem) if n.nivel == "info"]
    assert any("representativo" in t.lower() for t in textos)


def test_r4_metodo_detalhado_gera_info():
    # Default (detalhado): cita Anexo D e que o gate R4 e indicativo.
    textos = [n.texto for n in gerar_notas(_mem([_est(r4=5e-4)]))
              if n.nivel == "info"]
    assert any("Anexo D" in t for t in textos)


def test_r4_ausente_nao_gera_nota_de_metodo():
    # Sem R4 (=0), nao ha nota sobre metodo de R4.
    textos = [n.texto for n in gerar_notas(_mem([_est(r4=0.0)]))]
    assert not any("Anexo D" in t or "representativo" in t.lower() for t in textos)

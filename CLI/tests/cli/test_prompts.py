from spda.cli.prompts import Prompter, QuestionaryPrompter
from spda.model.enums import TipoSuperficie
from tests.cli.fakes import FakePrompter


def test_fakeprompter_satisfaz_protocolo():
    p: Prompter = FakePrompter([])
    assert isinstance(p, Prompter)  # runtime_checkable: verifica os metodos


def test_fakeprompter_consome_em_ordem():
    p = FakePrompter(["nome", 3.0, TipoSuperficie.terra_concreto, True])
    assert p.texto("nome?") == "nome"
    assert p.numero("n?") == 3.0
    assert p.opcao("s?", TipoSuperficie) == TipoSuperficie.terra_concreto
    assert p.confirmar("c?") is True


def test_questionary_prompter_existe_e_tem_metodos():
    p = QuestionaryPrompter()
    for m in ("texto", "numero", "numero_tabelado", "inteiro", "confirmar",
              "opcao", "opcao_opcional", "selecionar"):
        assert callable(getattr(p, m))

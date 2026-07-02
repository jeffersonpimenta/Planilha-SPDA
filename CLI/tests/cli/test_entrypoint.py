import io
from rich.console import Console

from spda.cli.menu import loop, EstadoSessao
from tests.cli.fakes import FakePrompter


def test_loop_sai_imediatamente():
    p = FakePrompter(["Sair"])
    console = Console(file=io.StringIO(), force_terminal=False)
    estado = loop(p, console, (lambda s: None), EstadoSessao())
    assert isinstance(estado, EstadoSessao)


def test_main_importavel():
    import spda.__main__ as m
    assert hasattr(m, "main") and callable(m.main)

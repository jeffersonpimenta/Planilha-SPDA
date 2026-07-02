from pathlib import Path
import enxugar_norma as en


def test_load_splits_lines(tmp_path):
    f = tmp_path / "in.txt"
    f.write_text("a\nb\nc", encoding="utf-8")
    assert en.load(str(f)) == ["a", "b", "c"]


def test_write_joins_lines(tmp_path):
    f = tmp_path / "out.md"
    en.write(["x", "y"], str(f))
    assert f.read_text(encoding="utf-8") == "x\ny"


def test_strip_boilerplate_removes_page_and_header_noise():
    raw = [
        "--- PÁGINA 30 ---",
        "18",
        "ABNT NBR",
        "",
        "5419-2:2026",
        "K",
        "Fator relevante",
        "© ABNT 2026",
        "   ",
    ]
    assert en.strip_boilerplate(raw) == ["K", "Fator relevante"]


def test_rejoin_subscripts_merges_symbol_and_subscript():
    raw = ["L", "A", "Perda relacionada aos ferimentos", "K", "S4", "Fator relevante"]
    assert en.rejoin_subscripts(raw) == [
        "L_A", "Perda relacionada aos ferimentos", "K_S4", "Fator relevante",
    ]


def test_rejoin_subscripts_ignores_normal_prose():
    raw = ["Comprimento da estrutura", "Perda em uma estrutura"]
    assert en.rejoin_subscripts(raw) == raw


def test_detect_tables_fences_long_short_runs():
    raw = ["MG", "14", "SP", "16", "RS", "12", "BA", "18"]  # 8 curtas
    out = en.detect_tables(raw, min_run=6)
    assert out[0] == "```"
    assert out[-1] == "```"
    assert out[1:-1] == raw


def test_detect_tables_leaves_prose():
    raw = ["Perda em uma estrutura relacionada a danos", "MG", "14"]
    assert en.detect_tables(raw, min_run=6) == raw  # run curto demais


def test_reflow_joins_wrapped_sentence():
    raw = ["Perda relacionada aos ferimentos em seres vivos", "na estrutura"]
    assert en.reflow_prose(raw) == ["Perda relacionada aos ferimentos em seres vivos na estrutura"]


def test_reflow_keeps_new_block_after_period():
    raw = ["Comprimento da estrutura.", "Perda em uma estrutura"]
    assert en.reflow_prose(raw) == ["Comprimento da estrutura.", "Perda em uma estrutura"]


def test_reflow_keeps_heading_separate():
    raw = ["texto anterior", "5.1", "Procedimento básico"]
    assert en.reflow_prose(raw) == ["texto anterior", "5.1", "Procedimento básico"]


def test_reflow_never_touches_fenced_table():
    raw = ["```", "MG", "14", "```"]
    assert en.reflow_prose(raw) == raw


def test_detect_tables_ignores_formula_fragments():
    # letras soltas e pontuacao de formula explodida NAO sao tabela
    raw = ["D", ",", "A", "M", ",", "A", "I", ",", "A", "L", ")"]
    assert en.detect_tables(raw, min_run=6) == raw


def test_detect_tables_fences_numeric_run():
    raw = ["10", "14", "16", "12", "18", "10", "14", "20"]  # 8 numeros
    out = en.detect_tables(raw, min_run=6)
    assert out[0] == "```" and out[-1] == "```" and out[1:-1] == raw


def test_drop_ng_appendix_removes_municipios():
    # estrutura pré-reflow: Nome / UF / Ng em linhas separadas
    raw = (
        ["Texto da metodologia."]
        + ["Município UF", "N_G"]
        + [x for i in range(60) for x in (f"Cidade{i}", "SP", "14")]
        + ["Bibliografia [1] ABNT NBR 5410"]
    )
    out = en.drop_ng_appendix(raw, min_entries=50)
    assert "Texto da metodologia." in out
    assert "Bibliografia [1] ABNT NBR 5410" in out
    assert not any("Cidade" in l for l in out)
    assert "Município UF" not in out and "N_G" not in out
    assert any("omitid" in l for l in out)  # placeholder presente


def test_drop_ng_appendix_noop_when_few():
    raw = ["Rio de Janeiro", "RJ", "14", "Texto normal"]
    assert en.drop_ng_appendix(raw, min_entries=50) == raw


def test_pipeline_end_to_end_small():
    raw = [
        "--- PÁGINA 30 ---", "18", "ABNT NBR", "", "5419-2:2026",
        "L", "A", "Perda relacionada aos ferimentos em seres vivos",
        "na estrutura",
        "MG", "14", "SP", "16", "RS", "12", "BA", "18", "PR", "10",
    ]
    out = en.pipeline(raw)
    assert "L_A" in out
    assert "Perda relacionada aos ferimentos em seres vivos na estrutura" in out
    assert out.count("```") == 2
    assert "--- PÁGINA 30 ---" not in out

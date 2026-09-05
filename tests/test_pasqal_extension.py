from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_pasqal_extension_is_loaded_by_all_views():
    themes = (ROOT / "app/styles/themes.css").read_text(encoding="utf-8")
    index = (ROOT / "app/index.html").read_text(encoding="utf-8")
    printing = (ROOT / "app/print.html").read_text(encoding="utf-8")
    assert '@import url("./pasqal.css")' in themes
    assert 'styles/themes.css' in index
    assert 'styles/themes.css' in printing


def test_pasqal_assets_exist():
    assert (ROOT / "app/styles/pasqal.css").is_file()
    assert (ROOT / "app/assets/pasqal-logo-light.svg").is_file()


def test_pasqal_fixture_exercises_native_families():
    deck = (ROOT / "examples/pasqal-golden/deck.md").read_text(encoding="utf-8")
    for token in (
        "#pasqal-front",
        "#pasqal-agenda",
        "#pasqal-content-1",
        "#pasqal-focus-1",
        "#pasqal-section-1",
        "#pasqal-dark-1",
        "#pasqal-closing",
    ):
        assert token in deck


def test_pasqal_print_colors_are_forced():
    css = (ROOT / "app/styles/pasqal.css").read_text(encoding="utf-8")
    assert "print-color-adjust:exact" in css.replace(" ", "")
    assert "#0F1E23" in css
    assert "#00C887" in css
    assert "#E1F6E9" in css

import pytest
from click.testing import CliRunner

from auto_compose import BlockExtractor, main


@pytest.mark.parametrize(
    "input,expected_matches,expected_spans",
    [
        ("IDEA: some match", ["some match"], [(6, 16)]),
        ("IDEA: with IDEA: nested", ["with IDEA: nested"], [(6, 23)]),
        ("no match", [], []),
        ("* IDEA: bullet", ["bullet"], [(8, 14)]),
        ("some text\n* IDEA: bullet", ["bullet"], [(18, 24)]),
        ("* IDEA: first\n* IDEA: second", ["first", "second"], [(8, 13), (22, 28)]),
    ],
)
def test_iter_matches(input, expected_matches, expected_spans):
    matches = list(BlockExtractor("", "IDEA:").iter_matches(input))
    assert [m.text for m in matches] == expected_matches
    assert [m.text_span for m in matches] == expected_spans


@pytest.mark.parametrize(
    "text,path,expected",
    [
        ("some text", "some/path", "[[some/path|some text]]"),
        ("more text", "another/path", "[[another/path|more text]]"),
    ],
)
def test_text_to_link(text, path, expected):
    linkified = BlockExtractor("", "").text_to_link(text, path)
    assert linkified == expected


@pytest.mark.parametrize(
    "original,match,replacement,span,expected",
    [
        (
            "This is a test.\n* IDEA: first idea\nSome more text",
            ["first idea"],
            ["[[path/to/first|first idea]]"],
            [(24, 34)],
            "This is a test.\n* IDEA: [[path/to/first|first idea]]\nSome more text",
        ),
        (
            "* IDEA: first idea\n* IDEA: second idea",
            ["first idea", "second idea"],
            ["[[path/to/first|first idea]]", "[[path/to/second|second idea]]"],
            [(8, 18), (27, 38)],
            (
                "* IDEA: [[path/to/first|first idea]]\n"
                "* IDEA: [[path/to/second|second idea]]"
            ),
        ),
        (
            "No matches here.",
            [],
            [],
            [],
            "No matches here.",
        ),
        (
            "* IDEA: nested IDEA: example",
            ["nested IDEA: example"],
            ["[[path/to/nested|nested IDEA: example]]"],
            [(8, 30)],
            "* IDEA: [[path/to/nested|nested IDEA: example]]",
        ),
        (
            "IDEA: duplicate idea\nIDEA: duplicate idea",
            ["duplicate idea", "duplicate idea"],
            ["[[path/to/dup|duplicate idea]]", "[[path/to/dup|duplicate idea]]"],
            [(6, 20), (27, 42)],
            (
                "IDEA: [[path/to/dup|duplicate idea]]\n"
                "IDEA: [[path/to/dup|duplicate idea]]"
            ),
        ),
    ],
)
def test_update_content(original, match, replacement, span, expected):
    exractor = BlockExtractor("", "")
    updated = exractor.update_content(original, match, replacement, span)
    assert updated == expected


def test_main():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("test.md", "w") as f:
            f.write("* IDEA: first\n* IDEA: second")

        result = runner.invoke(main, ["-i", "IDEA:", "test.md", "."])

        assert result.exit_code == 0
        assert "Found 2 ideas" in result.output


def test_main_with_logging():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("test.md", "w") as f:
            f.write("* IDEA: first\n* IDEA: second")

        result = runner.invoke(
            main, ["-i", "IDEA:", "-l", "DEBUG", "-f", "test.log", "test.md", "."]
        )

        assert result.exit_code == 0
        assert "Found 2 ideas" in result.output

        with open("test.log", "r") as log_file:
            log_content = log_file.read()
            assert "Processing file: test.md" in log_content
            assert "File content length: 28 characters" in log_content
            assert "Match 1: first" in log_content
            assert "Match 2: second" in log_content

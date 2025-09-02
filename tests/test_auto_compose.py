import pytest
from click.testing import CliRunner

from auto_compose import BlockExtractor, main


@pytest.mark.parametrize(
    "input,expected",
    [
        ("IDEA: some match", ["some match"]),
        ("IDEA: with IDEA: nested", ["with IDEA: nested"]),
        ("no match", []),
        ("* IDEA: bullet", ["bullet"]),
        ("some text\n* IDEA: bullet", ["bullet"]),
        ("* IDEA: first\n* IDEA: second", ["first", "second"]),
    ],
)
def test_get_matches(input, expected):
    matches = BlockExtractor("", "IDEA:").get_matches(input)
    assert matches == expected


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
    "original,match,replacement,expected",
    [
        (
            "This is a test.\n* IDEA: first idea\nSome more text",
            ["first idea"],
            ["[[path/to/first|first idea]]"],
            "This is a test.\n* IDEA: [[path/to/first|first idea]]\nSome more text",
        ),
        (
            "* IDEA: first idea\n* IDEA: second idea",
            ["first idea", "second idea"],
            ["[[path/to/first|first idea]]", "[[path/to/second|second idea]]"],
            (
                "* IDEA: [[path/to/first|first idea]]\n"
                "* IDEA: [[path/to/second|second idea]]"
            ),
        ),
        (
            "No matches here.",
            [],
            [],
            "No matches here.",
        ),
        (
            "* IDEA: nested IDEA: example",
            ["nested IDEA: example"],
            ["[[path/to/nested|nested IDEA: example]]"],
            "* IDEA: [[path/to/nested|nested IDEA: example]]",
        ),
        (
            "IDEA: duplicate idea\nIDEA: duplicate idea",
            ["duplicate idea", "duplicate idea"],
            ["[[path/to/dup|duplicate idea]]", "[[path/to/dup|duplicate idea]]"],
            (
                "IDEA: [[path/to/dup|duplicate idea]]\n"
                "IDEA: [[path/to/dup|duplicate idea]]"
            ),
        ),
    ],
)
def test_update_content(original, match, replacement, expected):
    exractor = BlockExtractor("", "")
    updated = exractor.update_content(original, match, replacement)
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
            assert "Raw matches found: 2" in log_content
            assert "Match 1: first" in log_content
            assert "Match 2: second" in log_content

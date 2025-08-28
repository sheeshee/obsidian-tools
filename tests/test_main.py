import pytest

from main import BlockExtractor, main
from click.testing import CliRunner


@pytest.mark.parametrize(
    "input,expected",
    [
        ("IDEA: some match", ["some match"]),
        ("IDEA: with IDEA: nested", ["with IDEA: nested"]),
        ("no match", []),
        ("* IDEA: bullet", ["bullet"]),
        ("some text\n* IDEA: bullet", ["bullet"]),
        ("* IDEA: first\n* IDEA: second", ["first", "second"])
    ]
)
def test_get_matches(input, expected):
    matches = BlockExtractor('', 'IDEA:').get_matches(input)

    assert matches == expected


def test_main():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("test.md", "w") as f:
            f.write("* IDEA: first\n* IDEA: second")

        result = runner.invoke(main, ["-i", "IDEA:", "test.md", "."])

        assert result.exit_code == 0
        assert "Found 2 ideas" in result.output

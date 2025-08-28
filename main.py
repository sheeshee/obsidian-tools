import re
from dataclasses import dataclass
from pathlib import Path

import click


@dataclass
class BlockExtractor:
    output_dir: Path|str
    indicator: str

    _indicator_base = r"^\*?\s*(%s\s*)(.*?)(?=\n|$)"

    def get_indicator(self) -> str:
        return self._indicator_base % self.indicator

    def ensure_is_path(self, filepath: Path | str) -> Path:
        return Path(filepath)

    def get_matches(self, content: str) -> list:
        matches = re.findall(self.get_indicator(), content, flags=re.MULTILINE)
        return [match[1] for match in matches]

    def extract_from_file(self, filepath) -> None:
        with open(filepath, "r") as file:
            content = file.read()
            matches = self.get_matches(content)

        print(f"Found {len(matches)} ideas")


@click.command()
@click.option(
    "--indicator", "-i",
    help="indicator to look for"
)
@click.argument(
    "input_filepath",
    type=click.Path(exists=True, dir_okay=False, writable=True)
)
@click.argument(
    "output_dir",
    type=click.Path()
)
def main(input_filepath, output_dir, indicator) -> None:
    extractor = BlockExtractor(output_dir, indicator)
    extractor.extract_from_file(input_filepath)



if __name__ == "__main__":
    main()

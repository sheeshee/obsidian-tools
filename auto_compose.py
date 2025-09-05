import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import click


def _make_default_logger():
    return logging.getLogger(os.path.basename(__file__))


def make_logger(log_level, log_file):
    # Configure logging
    logger = _make_default_logger()
    logger.setLevel(getattr(logging, log_level.upper()))

    # Create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")

    # Configure handler (file or stdout)
    if log_file:
        handler = logging.FileHandler(log_file)
        logger.info("Logging to file: %s", log_file)
    else:
        handler = logging.StreamHandler()

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


@dataclass
class BlockExtractor:
    output_dir: Path | str
    indicator: str
    logger: logging.Logger = field(default_factory=_make_default_logger)
    _indicator_base = r"^\s*[\*\-]?\s*(%s\s*)(?!\s*\[\[)(.*?)(?=\n|$)"

    @dataclass
    class Block:
        text: str
        text_span: tuple[int, int]
        full_block: str
        full_block_span: tuple[int, int]

    def get_indicator(self) -> str:
        return self._indicator_base % self.indicator

    def ensure_is_path(self, filepath: Path | str) -> Path:
        return Path(filepath)

    def iter_matches(self, content: str) -> Iterable[Block]:
        self.logger.debug("Searching for pattern: %s", self.get_indicator())
        match_groups = re.finditer(self.get_indicator(), content, flags=re.MULTILINE)
        for i, match in enumerate(match_groups):
            self.logger.debug(
                "Match %i: %s",
                i + 1,
                match.group(2)[:50] + ("..." if len(match.group(2)) > 50 else ""),
            )
            yield self.Block(
                match.group(2), match.span(2), match.group(0), match.span(0)
            )

    def text_to_link(self, text: str, path: Path | str) -> str:
        path = self.ensure_is_path(path)
        link = f"[[{path.as_posix()}|{text}]]"
        self.logger.debug("Linkified text: %s -> %s", text, link)
        return link

    def update_content(
        self,
        content: str,
        matches: list[str],
        replacements: list[str],
        spans: list[tuple[int, int]],
    ) -> str:
        new_content = []
        previous_end = 0
        iterator = zip(matches, replacements, spans)

        for i, (match, replacement, span) in enumerate(iterator):
            pre = content[previous_end : span[0]]
            previous_end = span[1]
            new_content.extend([pre, replacement])
            self.logger.debug(
                "(%i) Replacing '%s' with '%s'",
                i,
                content[span[0] : span[1]],
                replacement,
            )
            assert content[span[0] : span[1]] == match, (
                "Span does not match the expected text"
            )
        new_content.append(content[previous_end:])
        return "".join(new_content)

    def extract_from_file(self, filepath) -> None:
        self.logger.debug("Processing file: %s", filepath)

        with open(filepath, "r") as file:
            content = file.read()
            self.logger.debug("File content length: %s characters", len(content))
            matches = list(self.iter_matches(content))

        new_content = self.update_content(
            content,
            [m.text for m in matches],
            [
                self.text_to_link(m.text, Path(self.output_dir) / f"idea_{i + 1}.md")
                for i, m in enumerate(matches)
            ],
            [m.text_span for m in matches],
        )

        with open(filepath, "w") as file:
            file.write(new_content)
            self.logger.debug("Updated file written: %s", filepath)


@click.command()
@click.option("--indicator", "-i", help="indicator to look for")
@click.option(
    "--log-level",
    "-l",
    type=click.Choice(
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False
    ),
    default="CRITICAL",
    help="Set the logging level",
)
@click.option(
    "--log-file",
    "-f",
    type=click.Path(),
    help="Log file path (if not specified, logs go to stdout)",
)
@click.argument(
    "input_filepath", type=click.Path(exists=True, dir_okay=False, writable=True)
)
@click.argument("output_dir", type=click.Path())
def main(input_filepath, output_dir, indicator, log_level, log_file) -> None:
    logger = make_logger(log_level, log_file)
    logger.debug("Starting auto_compose with indicator: %s", indicator)
    logger.debug("Input file: %s", input_filepath)
    logger.debug("Output directory: %s", output_dir)

    extractor = BlockExtractor(output_dir, indicator, logger)
    extractor.extract_from_file(input_filepath)


if __name__ == "__main__":
    main()

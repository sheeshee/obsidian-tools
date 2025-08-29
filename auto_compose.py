import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

import click


class SilentLogger(logging.Logger):
    def __init__(self):
        super().__init__(name="silent_logger")

    def debug(self, *args, **kwargs):
        pass

    def info(self, *args, **kwargs):
        pass

    def warning(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass

    def critical(self, *args, **kwargs):
        pass


def make_logger(log_level, log_file):
    # Configure logging
    logger = logging.getLogger(os.path.basename(__file__))
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
    logger: logging.Logger = field(default_factory=SilentLogger)

    _indicator_base = r"^\*?\s*(%s\s*)(.*?)(?=\n|$)"

    def get_indicator(self) -> str:
        return self._indicator_base % self.indicator

    def ensure_is_path(self, filepath: Path | str) -> Path:
        return Path(filepath)

    def get_matches(self, content: str) -> list:
        self.logger.debug("Searching for pattern: %s", self.get_indicator())

        match_groups = re.findall(self.get_indicator(), content, flags=re.MULTILINE)

        self.logger.debug("Raw matches found: %i", len(match_groups))
        matches = [match[1] for match in match_groups]
        for i, match in enumerate(matches):
            self.logger.debug(
                "Match %i: %s", i + 1, match[:50] + ("..." if len(match) > 50 else "")
            )
        return matches

    def extract_from_file(self, filepath) -> None:
        self.logger.debug("Processing file: %s", filepath)

        with open(filepath, "r") as file:
            content = file.read()
            self.logger.debug("File content length: %s characters", len(content))
            matches = self.get_matches(content)

        self.logger.info("Found %i ideas", len(matches))
        print(f"Found {len(matches)} ideas")


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

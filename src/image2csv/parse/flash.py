"""
Class to parse bank statement prints from `Flash Benefits` company.
"""

import re
import warnings

from datetime import datetime, timedelta
from typing import List, TypedDict

from image2csv.format import BasicLinesFormatter
from image2csv.parse.base import BaseParser


class FlashEntry(TypedDict):
    """
    Parsed Flash bank statement entry.

    Attributes:
        - date: Date as string in brazilian date format `dd/mm/yyyy`.
        - description: Transaction description.
        - value: Transaction value (float as string).
    """

    date: str
    description: str
    value: str


class FlashBenefitsParser(BaseParser):
    """
    Class to parse bank statement prints from `Flash Benefits` company.
    """

    def __init__(self, images_path: str) -> None:
        """
        Initialize the parser.

        Args:
            images_path: Path to the images to be parsed.
        """

        warnings.warn(
            "FlashBenefitsParser infer `today` and `yesterday` dates from the current "
            "date of the execution of the script. Ensure the print screens were taken "
            "on the same day of the execution of the script.",
            category=UserWarning,
        )

        super().__init__(
            images_path,
            formatter=BasicLinesFormatter(
                remove_before_match="^Extrato",
                remove_after_match="^Extrato",
                replace_occurrences={
                    "hoje": datetime.today().strftime("%d/%m"),
                    "ontem": (datetime.today() - timedelta(days=1)).strftime("%d/%m"),
                    "...": "",
                },
            ),
        )

    def parse_text_lines(self, input_text_lines: List[str]) -> List[FlashEntry]:
        """
        Parse the lines of text extracted from the images.

        Args:
            input_text_lines: Lines of text extracted from the images.

        Returns:
            List of dictionaries with the parsed data.
        """

        regex = re.compile(
            "(?P<description>.+) (?P<date>[\d]{2}/[\d]{2})\n(?:.+)[$S]\s*"
            "(?P<value>[.\d]+,[\d]{2}) (?P<hour>[\d]{2}:[\d]{2})?"
        )

        parsed_text = [
            match.groupdict()
            for match in regex.finditer("\n".join(input_text_lines))
        ]

        for entry in parsed_text:
            entry["date"] = f"{entry['date']}/{datetime.today().year}"
            entry["value"] = entry["value"].replace(".", "").replace(",", ".")
            entry["description"] = " ".join(entry["description"].split(" ")[1:]).strip()
            entry["description"] = re.compile("\s+").sub(" ", entry["description"])

        return [FlashEntry(**entry) for entry in parsed_text]

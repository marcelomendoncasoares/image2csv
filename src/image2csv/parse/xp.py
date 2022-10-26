"""
Class to parse bank statement prints from `XP Card`.
"""

import re
import warnings

from datetime import datetime
from typing import Dict, List, TypedDict, Union

from image2csv.format import BasicLinesFormatter
from image2csv.parse.base import BaseParser


class XPCardEntry(TypedDict):
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


class XPCardNotificationsParser(BaseParser):
    """
    Class to parse notifications of the XP app to extract card payment entries.
    """

    def __init__(self, images_path: Union[str, List[str]]) -> None:
        """
        Initialize the parser.

        Args:
            images_path: Path to the images to be parsed.
        """

        warnings.warn(
            "XPCardNotificationsParser is not yet ready for usage. The regex parsing "
            "still require revision and accurate testing, as many lines are being lost "
            "in the current development stage. Use at your own risk.",
            category=UserWarning,
        )

        super().__init__(
            images_path,
            formatter=BasicLinesFormatter(
                remove_after_match="^Acessar",
                split_char=None,
            ),
        )

    def parse_text_lines(self, input_text_lines: List[str]) -> List[XPCardEntry]:
        """
        Parse the lines of text extracted from the images.

        Args:
            input_text_lines: Lines of text extracted from the images.

        Returns:
            List of dictionaries with the parsed data.
        """

        regex = re.compile(
            "Cartão XP (?P<date>[\d]{2}/?[\d]{2})\nCompra\sde\sR\$\s(?P<value>.+)\s"
            "APROVADA\sem\s(?P<description>.+\n?.+)\svia\scartão"
        )

        parsed_text: List[Dict[str, str]] = []

        for row in input_text_lines:
            parsed_row = [
                match.groupdict()
                for match in regex.finditer(row)
            ]
            parsed_text.extend(parsed_row)

        year = datetime.today().year
        for entry in parsed_text:
            entry['date'] = f"{entry['date'][:2]}/{entry['date'][-2:]}/{year}"
            entry['value'] = entry['value'].replace(".", "").replace(",", ".")
            entry['description'] = entry['description'].replace("\n", " ")

        return [XPCardEntry(**entry) for entry in parsed_text]

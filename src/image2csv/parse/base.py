"""
Classes to extract, format and parse the text from images into CSV tables.
"""

import pandas as pd

from abc import ABCMeta
from functools import lru_cache
from itertools import chain as flatten
from typing import Any, Dict, List

from image2csv.extract import OCRExtractor
from image2csv.format import BaseLinesFormatter, BasicLinesFormatter


class BaseParser(metaclass=ABCMeta):
    """
    Base class for image parsers. Can be extended for specific parsers based on rules of
    the intended image type that should be converted to CSV.
    """

    def __init__(
        self,
        images_path: str,
        *,
        extractor: OCRExtractor = OCRExtractor(),
        formatter: BaseLinesFormatter = BasicLinesFormatter(),
    ) -> None:
        """
        Initialize the parser.

        Args:
            images_path: Path to the images to be parsed.
            extractor: Extractor to be used to extract the text from the images.
            formatter: Formatter to be used to format the text extracted from the images.
        """

        self.images_path = images_path
        self.extractor = extractor
        self.formatter = formatter

    def parse_text_lines(self, input_text_lines: List[str]) -> List[Dict[str, Any]]:
        """
        Parse the lines of text extracted from the images.

        Args:
            input_text_lines: Lines of text extracted from the images.

        Returns:
            List of dictionaries with the parsed data.
        """
        raise NotImplementedError("Method `parse_text_lines` must be implemented.")

    @property
    @lru_cache(maxsize=1)
    def images(self) -> List[str]:
        """
        List of image paths.
        """
        return self.extractor(self.images_path)

    @property
    @lru_cache(maxsize=1)
    def input_text(self) -> List[str]:
        """
        Text extracted from the images.
        """
        return list(flatten(*map(self.formatter.format, self.images)))

    @property
    @lru_cache(maxsize=1)
    def parsed_text(self) -> List[Dict[str, Any]]:
        """
        Parsed text from the images.
        """
        return self.parse_text_lines(self.input_text)

    def to_df(self) -> pd.DataFrame:
        """
        Convert the text from the images to a pandas DataFrame.
        """
        return pd.DataFrame(self.parsed_text)

    def to_csv(self, output_path: str) -> None:
        """
        Save the parsed text from the images to a CSV file.
        """
        self.to_df().to_csv(output_path, index=False)

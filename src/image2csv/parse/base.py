"""
Classes to extract, format and parse the text from images into CSV tables.
"""

import pandas as pd

from abc import ABCMeta
from csv import QUOTE_NONNUMERIC
from functools import lru_cache
from itertools import chain as flatten
from typing import Any, Dict, List, Union

from image2csv.extract import OCRExtractor
from image2csv.format import BaseLinesFormatter, BasicLinesFormatter


class EmptyResults(Exception):
    """
    Exception raised when the parser returns no results.
    """


class BaseParser(metaclass=ABCMeta):
    """
    Base class for image parsers. Can be extended for specific parsers based on rules of
    the intended image type that should be converted to CSV.
    """

    def __init__(
        self,
        images_path: Union[str, List[str]],
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
        parsed_text = self.parse_text_lines(self.input_text)
        if len(parsed_text) == 0:
            raise EmptyResults("No results after image conversion.")
        return parsed_text

    def to_df(self, drop_duplicates: bool = False) -> pd.DataFrame:
        """
        Convert the text from the images to a pandas DataFrame.
        """
        df = pd.DataFrame(self.parsed_text)
        if drop_duplicates:
            df.drop_duplicates(inplace=True)
        return df

    def to_csv(
        self,
        output_path: str,
        drop_duplicates: bool = False,
        separator: str = ",",
        encoding: str = "utf-8",
    ) -> None:
        """
        Save the parsed text from the images to a CSV file.
        """
        self.to_df(drop_duplicates).to_csv(
            output_path,
            index=False,
            sep=separator,
            quotechar='"',
            quoting=QUOTE_NONNUMERIC,
            encoding=encoding,
        )

"""
Classes for formatting data extracted from images before parsing.
"""

import re

from abc import ABCMeta, abstractmethod
from typing import Callable, Dict, List, Optional


class BaseLinesFormatter(metaclass=ABCMeta):
    """
    Class to format the text extracted from the image.
    """

    @abstractmethod
    def format(self, text: str) -> List[str]:
        """
        Format the text lines.

        Args:
            text: Text to be formatted.

        Returns:
            List of formatted lines.
        """

    def __call__(self, text: str) -> List[str]:
        """
        Shortcut to `format` method, which is the main class API.
        """
        return self.format(text)


class BasicLinesFormatter(BaseLinesFormatter):
    """
    Class to format the text extracted from the image.
    """

    def __init__(
        self,
        min_chars: int = 3,
        remove_before_match: Optional[str] = None,
        remove_after_match: Optional[str] = None,
        remove_multiple_newlines: bool = True,
        replace_occurrences: Optional[Dict[str, str]] = None,
        split_char: Optional[str] = "\n",
    ) -> None:
        """
        Args:
            min_chars: Minimum number of characters to consider a line relevant.
            remove_before_match: String to be removed from the lines before the match.
            remove_after_match: String to be removed from the lines after the match.
            remove_multiple_newlines: Whether to remove multiple newline occurrences.
            replace_occurrences: Dictionary of strings to be replaced in the lines.
            split_char: Character to split the lines.
        """

        self.min_chars = min_chars
        self.remove_before_match = remove_before_match
        self.remove_after_match = remove_after_match
        self.remove_multiple_newlines = remove_multiple_newlines
        self.replace_occurrences = replace_occurrences
        self.split_char = split_char

    def _get_index_match(
        self,
        pattern: re.Pattern,
        lines: List[str],
        comp: Callable = min,
    ) -> Optional[int]:
        """
        Get the index of the line that matches the pattern.

        Args:
            pattern: Pattern to be matched.
            lines: List of lines to search for match.
            comp: Comparison mode, either `min` or `max` python functions.

        Returns:
            Index of the line that matches the pattern, or None if not found.
        """
        matches = [i for i, line in enumerate(lines) if re.match(pattern, line)]
        if matches:
            return comp(matches)
        return None

    def format(self, text: str) -> List[str]:
        """
        Format the text lines.

        Args:
            text: Text to be formatted.

        Returns:
            List of formatted lines.
        """

        if self.remove_multiple_newlines:
            text = re.compile(r"\n+").sub(r"\n", text)

        lines = [text] if self.split_char is None else text.split(self.split_char)

        if self.remove_before_match:
            ix_begin = self._get_index_match(self.remove_before_match, lines, min)
            if ix_begin is not None:
                lines = lines[ix_begin + 1 :]

        if self.remove_after_match:
            ix_end = self._get_index_match(self.remove_after_match, lines, max)
            if ix_end is not None:
                lines = lines[:ix_end]

        lines = [line for line in lines if len(line) >= self.min_chars]

        if self.replace_occurrences:
            for i, row in enumerate(lines):
                for k, v in self.replace_occurrences.items():
                    row = row.replace(k, v)
                lines[i] = row

        return lines

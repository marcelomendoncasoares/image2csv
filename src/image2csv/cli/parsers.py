"""
Get all parsers available for the CLI interface.
"""

import re

from importlib import import_module
from inspect import isclass
from pathlib import Path
from pkgutil import iter_modules
from typing import Dict, Type

from image2csv import parse
from image2csv.parse.base import BaseParser


def to_snake_case(name: str) -> str:
    """
    Convert a string to snake case.
    """

    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    name = re.sub("__([A-Z])", r"_\1", name)
    name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", name)
    return name.lower()


def _import_parser_classes_from_module(module_name: str) -> None:
    """
    Import all parser classes from a module.
    """

    return {
        to_snake_case(name).replace("_parser", ""): value
        for name, value in import_module(module_name).__dict__.items()
        if isclass(value) and issubclass(value, BaseParser) and value is not BaseParser
    }


def _get_all_parser_classes() -> Dict[str, Type[BaseParser]]:
    """
    Get all available parser classes on the package.

    Returns:
        Dictionary with the parser classes available on the package. The name of the
            key will be the name of the parser class in snake case and without the
            "Parser" or "_parser" suffixes.
    """

    available_classes = {}
    for module in iter_modules([Path(parse.__file__).parent]):
        if module.ispkg or module.name in ["__init__", "base"]:
            continue
        import_name = f"{parse.__name__}.{module.name}"
        available_classes.update(_import_parser_classes_from_module(import_name))
    return available_classes


available_parser_classes = _get_all_parser_classes()

"""
Test all available parsers.
"""

import json
import warnings

import pandas as pd
import pytest

from datetime import datetime, timedelta  # Might be used inside eval
from pathlib import Path
from typing import Dict, List, Type, TypedDict

from pandas.testing import assert_frame_equal

from image2csv.cli.parsers import available_parser_classes
from image2csv.parse.base import BaseParser


TEST_IMAGES_ROOT_PATH = "tests/images"


class ExpectedResultsConfig(TypedDict):
    """
    Expected results configuration.
    """
    must_match: List[str]
    partial_match: List[str]
    optional_match: List[str]
    replacements: Dict[str, str]
    expected_results: List[Dict[str, str]]


def _get_expected_results(file_dirname: Path) -> ExpectedResultsConfig:
    """
    Get the expected results for the parser.
    """

    config_file_path = file_dirname / "__expected_results__.json"
    with config_file_path.open(encoding='utf-8') as config_file:
        expected_results_config = json.load(config_file)

    expected_results_config["replacements"] = {
        placeholder: eval(replacement)
        for placeholder, replacement in expected_results_config["replacements"].items()
    }

    return ExpectedResultsConfig(**expected_results_config)


@pytest.mark.parametrize(
    ["parser_name", "parser_class"],
    available_parser_classes.items(),
)
def test_parser(parser_name: str, parser_class: Type[BaseParser]):
    """
    Test any parser with images in the `TEST_IMAGES_ROOT_PATH` folder.
    """

    test_images_path = Path(TEST_IMAGES_ROOT_PATH) / parser_name
    if not test_images_path.glob('*'):
        pytest.skip(f"No images found for parser '{parser_name}'")

    try:
        expected_results_config = _get_expected_results(test_images_path)
    except FileNotFoundError:
        pytest.skip(f"No expected results configured for parser '{parser_name}'.")

    must_match = expected_results_config["must_match"]
    partial_match = expected_results_config["partial_match"]
    replacements = expected_results_config["replacements"]
    expected_results = expected_results_config["expected_results"]

    parser = parser_class(test_images_path)

    assert len(expected_results) == len(parser.parsed_text)
    assert len(expected_results) == len(parser.to_df(drop_duplicates=True))

    expected_df = pd.DataFrame(expected_results).replace(replacements)
    results_df = parser.to_df()

    assert_frame_equal(expected_df[must_match], results_df[must_match])

    if not expected_df[partial_match].equals(results_df[partial_match]):
        diff = expected_df[partial_match]._values != results_df[partial_match]._values
        diff_percent = diff.astype(int).sum() * 100.0 / len(expected_df[partial_match])
        warnings.warn(
            f"Partial match for parser '{parser_name}' on columns {partial_match}. "
            f"Values are {round(diff_percent, 2)}% different from expected."
        )

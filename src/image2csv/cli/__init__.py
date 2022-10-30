"""
Image2CSV CLI interface to parse images and save directly from command line.
"""

import warnings

import click

from datetime import datetime
from typing import Callable, List

from click_default_group import DefaultGroup

from image2csv.cli.parsers import available_parser_classes
from image2csv.parse.base import EmptyResults


@click.group(
    cls=DefaultGroup,
    default='convert',
    default_if_no_args=True,
    context_settings=dict(help_option_names=['-h', '--help'])
)
def cli() -> None:
    """
    The `Image2CSV` CLI interface.
    """


def parser_options(command_func: Callable) -> Callable:
    """
    Dynamically add parser options to the command function. Will add one flag for each
    engine name for a faster way to choose the engine.
    """

    for flag, parser_class in available_parser_classes.items():
        option = click.option(
            f"--{flag}",
            is_flag=True,
            default=False,
            help=parser_class.__doc__,
        )
        command_func = option(command_func)

    return command_func


@cli.command()
@click.option(
    "--output_path",
    "-o",
    default='',
    is_eager=True,
    help="Output path to save the resulting CSV file.",
)
@click.option(
    "--drop_duplicates",
    "-d",
    is_flag=True,
    default=False,
    help="Whether to drop duplicate entries from the resulting CSV.",
)
@click.option(
    "--parser",
    "-p",
    type=click.Choice(available_parser_classes, case_sensitive=False),
    prompt=False,
    help="The parser engine to extract data from the image to save as CSV.",
)
@click.option(
    "--separator",
    "--sep",
    "-s",
    type=str,
    default=",",
    help="The separator to use in the resulting CSV file.",
)
@click.option(
    "--encoding",
    "-e",
    type=str,
    default="latin1",
    help="The encoding to use when saving the CSV file.",
)
@parser_options
@click.argument('input_path', nargs=-1, required=True)
def convert(
    input_path: List[str],
    *,
    output_path: str,
    drop_duplicates: bool = False,
    parser: str,
    separator: str = ",",
    encoding: str = "latin1",
    **kwargs
) -> None:
    """
    Convert images to CSV files.
    """

    for flag, is_true in kwargs.items():
        if available_parser_classes.get(flag) and is_true:
            parser = flag
            break

    if not parser:
        raise click.MissingParameter(
            "No parser engine provided. Either pass `--parser` and the parser name or "
            "one of the parser flags in the format `--<parser_name>`."
        )

    if not output_path:
        output_path = f"{parser}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    with warnings.catch_warnings(record=True) as warnings_list:
        warnings.simplefilter("always")
        parser_obj = available_parser_classes[parser](input_path)
        for warning in warnings_list:
            click.secho(warning.message, fg="yellow")

    click.secho(f"Found {len(parser_obj.images)} images to convert...")

    try:
        parser_obj.to_csv(
            output_path,
            drop_duplicates=drop_duplicates,
            separator=separator,
            encoding=encoding,
        )
    except EmptyResults as exc:
        click.secho(str(exc), fg="red")

    click.secho(f"Images parsed with success to file '{output_path}'.\n", fg="green")


if __name__ == "__main__":
    cli()

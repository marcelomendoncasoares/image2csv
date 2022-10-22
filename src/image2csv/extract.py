"""
Classes for extracting data from images.
"""

from concurrent.futures import ThreadPoolExecutor
from itertools import chain as flatten
from pathlib import Path
from typing import Iterable, List, Optional, Union, overload

from PIL import Image
from pytesseract import pytesseract


class OCRExtractor:
    """
    Class to extract text from an image using `pytesseract`.
    """

    def __init__(
        self,
        language: str = "por",
        page_segmentation_mode: int = 4,
        extra_tesseract_config: str = "",
        max_workers: Optional[int] = None,
    ) -> None:
        """
        For table formatted images, best results usually are achieved with value `4` or `6`
        for the parameter `page_segmentation_mode`. The options are:

            0  - Orientation and script detection (OSD) only.
            1  - Automatic page segmentation with OSD.
            2  - Automatic page segmentation, but no OSD, or OCR.
            3  - Fully automatic page segmentation, but no OSD. (Default)
            4  - Assume a single column of text of variable sizes.
            5  - Assume a single uniform block of vertically aligned text.
            6  - Assume a single uniform block of text.
            7  - Treat the image as a single text line.
            8  - Treat the image as a single word.
            9  - Treat the image as a single word in a circle.
            10 - Treat the image as a single character.
            11 - Sparse text. Find as much text as possible in no particular order.
            12 - Sparse text with OSD.
            13 - Raw line. Treat the image as a single text line, bypassing hacks that are Tesseract-specific.

        Extra options passed to `pytesseract` should not include `--psm`, as it is always
        specified before other arguments.

        Args:
            language: Language to be used for the OCR.
            page_segmentation_mode: Page segmentation mode to be used for the OCR.
            extra_tesseract_config: Extra options to be passed to the OCR.
            max_workers: Number of workers to be used for extracting text from images concurrently.
        """

        self.language = language
        self.page_segmentation_mode = page_segmentation_mode
        self.extra_tesseract_config = extra_tesseract_config
        self.max_workers = max_workers

    def extract_text_from_image(self, path: str) -> str:
        """
        Extract text from an image.

        Args:
            path: Path to the image file.

        Returns:
            The extracted text.
        """

        return pytesseract.image_to_string(
            Image.open(path),
            lang=self.language,
            config=f"--psm {self.page_segmentation_mode} {self.extra_tesseract_config}",
        )

    def extract_text_from_images(self, paths: Iterable[str]) -> List[str]:
        """
        Extract text from a list of images.

        Args:
            paths: Iterable of paths to the image files.

        Returns:
            The extracted text.
        """

        with ThreadPoolExecutor(self.max_workers) as executor:
            return list(executor.map(self.extract_text_from_image, paths))

    @overload
    def extract(self, path_or_paths: str) -> str:
        ...

    @overload
    def extract(self, path_or_paths: List[str]) -> List[str]:
        ...

    def extract(self, path_or_paths: Union[str, List[str]]) -> Union[str, List[str]]:
        """
        Extract text from images. If the path is a directory, all images in the
        directory will be extracted recursively. Supported extensions are `.jpg`,
        `.jpeg` or `.png`.

        Args:
            path_or_paths: Path or paths to the image file or folders with images.

        Returns:
            The extracted text, if path is a file, or list with extracted texts.
        """

        if isinstance(path_or_paths, list):
            return list(flatten(*[self.extract(path) for path in path_or_paths]))

        path_obj = Path(path_or_paths)

        if path_obj.is_file():
            return self.extract_text_from_image(path_or_paths)

        image_files = [path_obj.rglob(f"*.{ext}") for ext in ["jpg", "jpeg", "png"]]
        return self.extract_text_from_images(flatten(*image_files))

    @overload
    def __call__(self, path_or_paths: str) -> str:
        ...

    @overload
    def __call__(self, path_or_paths: List[str]) -> List[str]:
        ...

    def __call__(self, path_or_paths: Union[str, List[str]]) -> Union[str, List[str]]:
        """
        Shortcut for the `extract` method, which is the main API of the class.
        """
        return self.extract(path_or_paths)

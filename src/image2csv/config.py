"""
General configurations for the package.
"""

from subprocess import Popen, PIPE

from pytesseract import pytesseract


def find_tesseract_path() -> str:
    """
    Attempt to find the path to the tesseract executable.
    """

    possible_cmds = [
        r"tesseract",  # Command in PATH
        r"/usr/bin/tesseract",  # Linux
        r"/usr/local/bin/tesseract",  # macOS
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",  # Win64
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",  # Win32
    ]

    for possible_cmd in possible_cmds:
        try:
            if not Popen([possible_cmd, "-h"], stdout=PIPE).stderr:
                return possible_cmd
        except FileNotFoundError:
            pass

    raise EnvironmentError(
        "Could not determinate `tesseract` path automatically. Please add the "
        "`tesseract` executable to the PATH environment variable."
    )


def init_tesseract() -> None:
    """
    Initialize the tesseract executable.
    """
    pytesseract.tesseract_cmd = find_tesseract_path()

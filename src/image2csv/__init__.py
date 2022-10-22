"""
Image2CSV is a Python module for converting images to CSV files.

"""

from image2csv.config import init_tesseract

# Automatically initialize tesseract, as the package does not work without it. Any
# installation errors will prevent the package from being imported, but will also be
# quickly resolved by the user.
init_tesseract()

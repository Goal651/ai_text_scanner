import cv2
import pytesseract
from PIL import Image
import numpy as np

class OCRScanner:
    def __init__(self, tesseract_cmd=None):
        """
        Initialize the OCR scanner.
        :param tesseract_cmd: Optional path to tesseract executable if not in PATH.
        """
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def extract_text(self, image_source):
        """
        Extract text from an image source (path or numpy array).
        """
        image = self._preprocess_image(image_source)
        try:
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            return f"Error executing OCR: {e}"

    def extract_data(self, image_source):
        """
        Extract detailed data (boxes, confidences) from an image.
        Returns a dict containing 'text', 'left', 'top', 'width', 'height', 'conf'.
        """
        image = self._preprocess_image(image_source)
        try:
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            return data
        except Exception as e:
            print(f"Error executing OCR Data extraction: {e}")
            return None

    def _preprocess_image(self, image_source):
        """
        Convert to PIL Image if necessary.
        """
        if isinstance(image_source, str):
            return Image.open(image_source)
        elif isinstance(image_source, np.ndarray):
             # Convert OpenCV BGR to RGB
            image_rgb = cv2.cvtColor(image_source, cv2.COLOR_BGR2RGB)
            return Image.fromarray(image_rgb)
        else:
            return image_source

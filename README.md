# AI Text Scanner | No-ML Assignment

## Overview

This project is a GUI-based application for extracting text from images using Optical Character Recognition (OCR). It utilizes **PyQt5** for the interface, **OpenCV** for image handling and camera integration, and **Tesseract OCR** for text recognition.

The application allows users to load images from the filesystem or capture frames from a live camera feed. It features a Region of Interest (ROI) selection tool to perform OCR on specific parts of an image.

## Features

- **Image Loading**: Open common image formats (JPG, PNG, BMP) for analysis.
- **Live Camera Feed**: Integrate with the system webcam to capture and process live video frames.
- **ROI Selection**: Interactive "Region of Interest" tool to select specific areas of the image for text extraction.
- **OCR Integration**: Extracts text using Tesseract OCR and displays it in the side panel.
- **Visual Feedback**: Draws bounding boxes around detected text elements on the image associated with high confidence scores.

## Prerequisites

### System Dependencies

- **Tesseract OCR**: This application requires Tesseract to be installed on your system.
  - **Linux**: `sudo apt-get install tesseract-ocr`
  - **Windows**: Download the installer from the [UB Mannheim GitHub](https://github.com/UB-Mannheim/tesseract/wiki).
  - **macOS**: `brew install tesseract`

### Python Dependencies

Ensure you have Python 3.x installed. Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

*Key dependencies:*

- `PyQt5`
- `opencv-python`
- `pytesseract`
- `Pillow`
- `numpy`

## Usage

1. **Run the Application**:

   ```bash
   python main.py
   ```

2. **Load an Input**:
   - **File**: Click **Load Image** to select an image from your computer.
   - **Camera**: Click **Start Camera** to view the live feed. Click **Capture Processing Frame** (or Pause) to freeze the current frame for analysis.

3. **Select Region (Optional)**:
   - Check **ROI Select Mode**.
   - Click and drag on the image to draw a red dashed box around the text you want to scan.

4. **Extract Text**:
   - Click **RUN OCR**.
   - The extracted text will appear in the right-hand panel.
   - Detected text regions will be highlighted with green boxes on the image.

## Project Structure

- **`main.py`**: Entry point. Contains the `MainWindow` class and GUI logic (layout, event handling, camera control).
- **`scanner_core.py`**: Wrapper class `OCRScanner` for `pytesseract` interactions and image preprocessing.
- **`styles.qss`**: Stylesheet for customizing the look and feel of the Qt application.

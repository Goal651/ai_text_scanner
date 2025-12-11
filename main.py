import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QFileDialog, QGraphicsView,
    QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem, QMessageBox,
    QCheckBox, QSplitter
)
from PyQt5.QtGui import QPixmap, QImage, QPen, QColor, QBrush
from PyQt5.QtCore import Qt, QTimer, QRectF
from scanner_core import OCRScanner

class ResizableRectItem(QGraphicsRectItem):
    """
    A persistent rectangle for ROI selection.
    """
    def __init__(self, rect):
        super().__init__(rect)
        self.setPen(QPen(QColor("#f38ba8"), 2, Qt.DashLine)) # Red/Pink dashed line
        self.setBrush(QBrush(QColor(243, 139, 168, 50))) # Semi-transparent fill
        self.setFlags(QGraphicsRectItem.ItemIsMovable | QGraphicsRectItem.ItemIsSelectable | QGraphicsRectItem.ItemSendsGeometryChanges)

class ImageViewer(QGraphicsView):
    """
    Custom Graphics View for Image Display and ROI selection.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.pixmap_item = None
        self.roi_item = None
        self.drawing = False
        self.start_point = None
        self.setDragMode(QGraphicsView.RubberBandDrag) # Default mode

    def set_image(self, image_path=None, cv_image=None):
        self.scene.clear()
        self.roi_item = None
        
        if image_path:
            pixmap = QPixmap(image_path)
        elif cv_image is not None:
            # Convert CV2 image to QPixmap
            height, width, channel = cv_image.shape
            bytes_per_line = 3 * width
            q_img = QImage(cv_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
        else:
            return

        self.pixmap_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(self.pixmap_item)
        self.setSceneRect(QRectF(pixmap.rect()))
        
    def get_roi_rect(self):
        if self.roi_item:
            return self.roi_item.sceneBoundingRect()
        return None

    def enable_roi_mode(self, enabled):
        if enabled:
            self.setDragMode(QGraphicsView.NoDrag)
            self.setCursor(Qt.CrossCursor)
        else:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.setCursor(Qt.ArrowCursor)

    def mousePressEvent(self, event):
        if self.dragMode() == QGraphicsView.NoDrag and event.button() == Qt.LeftButton:
            self.drawing = True
            self.start_point = self.mapToScene(event.pos())
            if self.roi_item:
                self.scene.removeItem(self.roi_item)
            self.roi_item = ResizableRectItem(QRectF(self.start_point, self.start_point))
            self.scene.addItem(self.roi_item)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drawing and self.roi_item:
            end_point = self.mapToScene(event.pos())
            rect = QRectF(self.start_point, end_point).normalized()
            self.roi_item.setRect(rect)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.drawing:
            self.drawing = False
        else:
            super().mouseReleaseEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Text Scanner | No-ML Assignment")
        self.setGeometry(100, 100, 1200, 800)

        self.scanner = OCRScanner()
        self.current_image = None # Should be CV2 format (numpy array) if modified, or just path logic
        self.camera_active = False
        self.camera = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

        self.init_ui()
        self.load_styles()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # SPLITTER for resizeable layout
        splitter = QSplitter(Qt.Horizontal)

        # LEFT PANEL (Image / Camera)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        self.image_view = ImageViewer()
        left_layout.addWidget(self.image_view)

        # Control Bar for Left Panel
        controls_layout = QHBoxLayout()
        
        self.btn_load = QPushButton("Load Image")
        self.btn_load.clicked.connect(self.load_image)
        controls_layout.addWidget(self.btn_load)

        self.btn_camera = QPushButton("Start Camera")
        self.btn_camera.clicked.connect(self.toggle_camera)
        controls_layout.addWidget(self.btn_camera)
        
        self.chk_roi = QCheckBox("ROI Select Mode")
        self.chk_roi.toggled.connect(self.toggle_roi_mode)
        controls_layout.addWidget(self.chk_roi)

        left_layout.addLayout(controls_layout)

        # RIGHT PANEL (Results & Actions)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        self.lbl_title = QLabel("Extracted Text")
        self.lbl_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        right_layout.addWidget(self.lbl_title)

        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        self.text_output.setPlaceholderText("OCR results will appear here...")
        right_layout.addWidget(self.text_output)

        self.btn_ocr = QPushButton("RUN OCR")
        self.btn_ocr.setObjectName("actionButton") # For special styling
        self.btn_ocr.setMinimumHeight(50)
        self.btn_ocr.clicked.connect(self.run_ocr)
        right_layout.addWidget(self.btn_ocr)

        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 3) # Left side bigger
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter)

    def load_styles(self):
        try:
            with open("styles.qss", "r") as f:
                self.setStyleSheet(f.read())
        except:
            print("styles.qss not found, using default.")

    def load_image(self):
        if self.camera_active:
            self.toggle_camera() # Stop camera first

        path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if path:
            self.current_image = cv2.imread(path)
            # OpenCV reads in BGR, convert to RGB for Display
            img_rgb = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB)
            self.image_view.set_image(cv_image=img_rgb)

    def toggle_camera(self):
        if self.camera_active:
            self.timer.stop()
            if self.camera:
                self.camera.release()
            self.camera_active = False
            self.btn_camera.setText("Start Camera")
            self.btn_load.setEnabled(True)
        else:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                QMessageBox.critical(self, "Error", "Could not open camera!")
                return
            self.camera_active = True
            self.timer.start(30) # 30ms ~ 33fps
            self.btn_camera.setText("Capture Processing Frame")
            self.btn_load.setEnabled(False)

    def update_frame(self):
        ret, frame = self.camera.read()
        if ret:
            self.current_image = frame
            # Process for display
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # We don't want to clear the scene every frame if we want overlays to persist, 
            # but for live video we usually just update the pixmap.
            # Simplified approach: update entire view
            self.image_view.set_image(cv_image=frame_rgb)

    def toggle_roi_mode(self, active):
        self.image_view.enable_roi_mode(active)

    def run_ocr(self):
        if self.current_image is None:
            QMessageBox.warning(self, "No Image", "Please load an image or start camera first.")
            return

        # Check for ROI
        roi_rect = self.image_view.get_roi_rect()
        
        process_image = self.current_image.copy()
        
        # If ROI exists and has positive area
        if roi_rect and roi_rect.width() > 0 and roi_rect.height() > 0:
            # roi_rect coords are relative to the scene (image size)
            x, y, w, h = int(roi_rect.x()), int(roi_rect.y()), int(roi_rect.width()), int(roi_rect.height())
            
            # Clamp to image bounds
            h_img, w_img = process_image.shape[:2]
            x = max(0, x)
            y = max(0, y)
            w = min(w, w_img - x)
            h = min(h, h_img - y)
            
            process_image = process_image[y:y+h, x:x+w]

        # Display "Processing..."
        self.text_output.setPlainText("Processing...")
        QApplication.processEvents()

        # Run OCR
        # Note: In a real heavy app, use QThread. For this assignment, blocking is likely acceptable but minor lag.
        try:
            # Get verbose data for overlay
            # We perform OCR on the cutout (process_image)
            data = self.scanner.extract_data(process_image)
            text = self.scanner.extract_text(process_image)
            
            self.text_output.setPlainText(text)
            
            # Optional: Draw boxes on the processed image segment and show it?
            # Or draw boxes on the Main View?
            # Drawing on main view is cooler.
            
            # We need to map boxes back to original coordinates if ROI was used.
            offset_x = 0
            offset_y = 0
            if roi_rect:
                offset_x = int(roi_rect.x())
                offset_y = int(roi_rect.y())

            if data:
                n_boxes = len(data['text'])
                for i in range(n_boxes):
                    if int(data['conf'][i]) > 40: # Confidence threshold
                        (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
                        # Draw on the original scene
                        # Create a rect item
                        box_x, box_y = x + offset_x, y + offset_y
                        rect_item = QGraphicsRectItem(box_x, box_y, w, h)
                        rect_item.setPen(QPen(QColor("#a6e3a1"), 2)) # Green
                        self.image_view.scene.addItem(rect_item)

        except Exception as e:
            self.text_output.setPlainText(f"Error: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

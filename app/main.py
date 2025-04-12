import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QLabel, QFileDialog, QSpinBox, 
                            QProgressBar, QHBoxLayout, QLineEdit)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon
from fonteco.fonts import perforate_font

class FontProcessingThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, input_path, output_path, reduction_percentage):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.reduction_percentage = reduction_percentage

    def run(self):
        try:
            def update_progress(value):
                self.progress.emit(value)

            # Process the font
            perforate_font(
                input_font_path=self.input_path,
                output_font_path=self.output_path,
                reduction_percentage=self.reduction_percentage,
                draw_images=False,  # Don't save debug images
                debug=False,  # Don't print debug info
                progress_callback=update_progress
            )
            self.progress.emit(100)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fonteco")
        self.setMinimumSize(600, 300)  # Reduced minimum height
        
        # Set application icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                'misc', 'ecofont_logo.icns')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)  # Reduced spacing between elements
        layout.setContentsMargins(20, 20, 20, 20)  # Add some margins around the content
        
        # Add a label
        title_label = QLabel("FontEco: Making fonts eco-friendlier")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")  # Reduced margin
        layout.addWidget(title_label)
        
        # Input path selection
        input_layout = QHBoxLayout()
        self.input_path = QLineEdit()
        self.input_path.setPlaceholderText("Select input font file...")
        self.input_path.returnPressed.connect(self.start_conversion)
        input_layout.addWidget(self.input_path)
        
        input_button = QPushButton("Browse")
        input_button.clicked.connect(self.select_input_file)
        input_layout.addWidget(input_button)
        layout.addLayout(input_layout)
        
        # Output path selection
        output_layout = QHBoxLayout()
        self.output_path = QLineEdit()
        self.output_path.setPlaceholderText("Select output location...")
        self.output_path.returnPressed.connect(self.start_conversion)
        output_layout.addWidget(self.output_path)
        
        output_button = QPushButton("Browse")
        output_button.clicked.connect(self.select_output_file)
        output_layout.addWidget(output_button)
        layout.addLayout(output_layout)
        
        # Dithering options
        dither_layout = QHBoxLayout()
        dither_label = QLabel("Reduction Percentage:")
        self.reduction_spinbox = QSpinBox()
        self.reduction_spinbox.setRange(1, 100)
        self.reduction_spinbox.setValue(40)  # Default value from pipeline.py
        self.reduction_spinbox.setSuffix("%")
        # Install event filter for Enter key handling
        self.reduction_spinbox.installEventFilter(self)
        dither_layout.addWidget(dither_label)
        dither_layout.addWidget(self.reduction_spinbox)
        dither_layout.addStretch()
        layout.addLayout(dither_layout)
        
        # Progress bar and completion message
        self.progress_container = QWidget()
        progress_layout = QVBoxLayout(self.progress_container)
        progress_layout.setContentsMargins(0, 0, 0, 0)  # Remove extra margins
        progress_layout.setSpacing(5)  # Reduced spacing in progress container
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        self.completion_label = QLabel()
        self.completion_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.completion_label.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 16px;
                font-weight: bold;
                margin: 5px;  # Reduced margin
            }
        """)
        self.completion_label.setVisible(False)
        progress_layout.addWidget(self.completion_label)
        
        layout.addWidget(self.progress_container)
        
        # Convert button
        self.convert_button = QPushButton("Convert Font")
        self.convert_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.convert_button.clicked.connect(self.start_conversion)
        layout.addWidget(self.convert_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Add flexible space at the bottom
        layout.addStretch(1)  # Use stretch factor of 1
        
        self.processing_thread = None
        self.message_timer = QTimer()
        self.message_timer.timeout.connect(self.hide_completion_message)

    def select_input_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Font File",
            "",
            "Font Files (*.ttf *.otf);;All Files (*.*)"
        )
        if file_name:
            self.input_path.setText(file_name)

    def select_output_file(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save Font File",
            "",
            "Font Files (*.ttf);;All Files (*.*)"
        )
        if file_name:
            self.output_path.setText(file_name)

    def show_completion_message(self):
        self.progress_bar.setVisible(False)
        self.completion_label.setText("Font conversion completed successfully!")
        self.completion_label.setVisible(True)
        # Hide the message after 5 seconds
        self.message_timer.start(5000)

    def hide_completion_message(self):
        self.message_timer.stop()
        self.completion_label.setVisible(False)

    def start_conversion(self):
        if not self.input_path.text() or not self.output_path.text():
            return
        
        # Hide any existing completion message
        self.hide_completion_message()
        
        self.convert_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.processing_thread = FontProcessingThread(
            self.input_path.text(),
            self.output_path.text(),
            self.reduction_spinbox.value()
        )
        self.processing_thread.progress.connect(self.update_progress)
        self.processing_thread.finished.connect(self.conversion_finished)
        self.processing_thread.error.connect(self.handle_error)
        self.processing_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def conversion_finished(self):
        self.convert_button.setEnabled(True)
        self.show_completion_message()
        self.processing_thread = None

    def handle_error(self, error_message):
        self.convert_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.completion_label.setText(f"Error: {error_message}")
        self.completion_label.setStyleSheet("""
            QLabel {
                color: #f44336;
                font-size: 16px;
                font-weight: bold;
                margin: 10px;
            }
        """)
        self.completion_label.setVisible(True)
        self.message_timer.start(5000)  # Show error message for 5 seconds
        self.processing_thread = None

    def eventFilter(self, obj, event):
        if obj == self.reduction_spinbox and event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
                self.start_conversion()
                return True
        return super().eventFilter(obj, event)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 
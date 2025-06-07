import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QLabel, QFileDialog, QSpinBox, 
                            QProgressBar, QHBoxLayout, QLineEdit, QComboBox,
                            QGroupBox, QCheckBox, QTabWidget, QScrollArea)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon
from fonteco.fonts import perforate_font

class FontProcessingThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, input_path, output_path, options):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.options = options

    def run(self):
        try:
            def update_progress(value):
                self.progress.emit(value)

            # Process the font
            perforate_font(
                input_font_path=self.input_path,
                output_font_path=self.output_path,
                progress_callback=update_progress,
                **self.options
            )
            self.progress.emit(100)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fonteco")
        self.setMinimumSize(800, 600)  # Increased size for more options
        
        # Set application icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                'misc', 'ecofont_logo.icns')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Add a label
        title_label = QLabel("FontEco: Making fonts eco-friendlier")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # Create tab widget
        tab_widget = QTabWidget()
        main_tab = QWidget()
        advanced_tab = QWidget()
        tab_widget.addTab(main_tab, "Main")
        tab_widget.addTab(advanced_tab, "Advanced")
        layout.addWidget(tab_widget)
        
        # Main tab layout
        main_layout = QVBoxLayout(main_tab)
        
        # Input path selection
        input_layout = QHBoxLayout()
        self.input_path = QLineEdit()
        self.input_path.setPlaceholderText("Select input font file...")
        self.input_path.returnPressed.connect(self.start_conversion)
        input_layout.addWidget(self.input_path)
        
        input_button = QPushButton("Browse")
        input_button.clicked.connect(self.select_input_file)
        input_layout.addWidget(input_button)
        main_layout.addLayout(input_layout)
        
        # Output path selection
        output_layout = QHBoxLayout()
        self.output_path = QLineEdit()
        self.output_path.setPlaceholderText("Select output location...")
        self.output_path.returnPressed.connect(self.start_conversion)
        output_layout.addWidget(self.output_path)
        
        output_button = QPushButton("Browse")
        output_button.clicked.connect(self.select_output_file)
        output_layout.addWidget(output_button)
        main_layout.addLayout(output_layout)
        
        # Dithering mode selection
        dither_layout = QHBoxLayout()
        dither_label = QLabel("Dithering Mode:")
        self.dither_mode = QComboBox()
        self.dither_mode.addItems(["blue_noise", "shape", "line"])
        self.dither_mode.currentTextChanged.connect(self.update_dithering_options)
        dither_layout.addWidget(dither_label)
        dither_layout.addWidget(self.dither_mode)
        dither_layout.addStretch()
        main_layout.addLayout(dither_layout)
        
        # Rendering mode selection
        render_layout = QHBoxLayout()
        render_label = QLabel("Rendering Mode:")
        self.render_mode = QComboBox()
        self.render_mode.addItems(["original", "simplified", "optimized", "optimized_masked"])
        render_layout.addWidget(render_label)
        render_layout.addWidget(self.render_mode)
        render_layout.addStretch()
        main_layout.addLayout(render_layout)
        
        # Blue noise options
        self.blue_noise_group = QGroupBox("Blue Noise Options")
        blue_noise_layout = QVBoxLayout()
        
        reduction_layout = QHBoxLayout()
        reduction_label = QLabel("Reduction Percentage:")
        self.reduction_spinbox = QSpinBox()
        self.reduction_spinbox.setRange(1, 100)
        self.reduction_spinbox.setValue(40)
        self.reduction_spinbox.setSuffix("%")
        reduction_layout.addWidget(reduction_label)
        reduction_layout.addWidget(self.reduction_spinbox)
        reduction_layout.addStretch()
        blue_noise_layout.addLayout(reduction_layout)
        
        point_size_layout = QHBoxLayout()
        point_size_label = QLabel("Point Size:")
        self.point_size = QSpinBox()
        self.point_size.setRange(1, 10)
        self.point_size.setValue(1)
        point_size_layout.addWidget(point_size_label)
        point_size_layout.addWidget(self.point_size)
        point_size_layout.addStretch()
        blue_noise_layout.addLayout(point_size_layout)
        
        self.blue_noise_group.setLayout(blue_noise_layout)
        main_layout.addWidget(self.blue_noise_group)
        
        # Shape options
        self.shape_group = QGroupBox("Shape Options")
        shape_layout = QVBoxLayout()
        
        shape_type_layout = QHBoxLayout()
        shape_type_label = QLabel("Shape Type:")
        self.shape_type = QComboBox()
        self.shape_type.addItems(["circle", "rectangle"])
        shape_type_layout.addWidget(shape_type_label)
        shape_type_layout.addWidget(self.shape_type)
        shape_type_layout.addStretch()
        shape_layout.addLayout(shape_type_layout)
        
        shape_size_layout = QHBoxLayout()
        shape_size_label = QLabel("Shape Size:")
        self.shape_size = QComboBox()
        self.shape_size.addItems(["10", "random", "biggest"])
        shape_size_layout.addWidget(shape_size_label)
        shape_size_layout.addWidget(self.shape_size)
        shape_size_layout.addStretch()
        shape_layout.addLayout(shape_size_layout)
        
        margin_layout = QHBoxLayout()
        margin_label = QLabel("Margin:")
        self.margin = QSpinBox()
        self.margin.setRange(0, 50)
        self.margin.setValue(1)
        margin_layout.addWidget(margin_label)
        margin_layout.addWidget(self.margin)
        margin_layout.addStretch()
        shape_layout.addLayout(margin_layout)
        
        self.shape_group.setLayout(shape_layout)
        main_layout.addWidget(self.shape_group)
        
        # Line options
        self.line_group = QGroupBox("Line Options")
        line_layout = QVBoxLayout()
        
        line_type_layout = QHBoxLayout()
        line_type_label = QLabel("Line Type:")
        self.line_type = QComboBox()
        self.line_type.addItems(["parallel", "random"])
        line_type_layout.addWidget(line_type_label)
        line_type_layout.addWidget(self.line_type)
        line_type_layout.addStretch()
        line_layout.addLayout(line_type_layout)
        
        curve_type_layout = QHBoxLayout()
        curve_type_label = QLabel("Curve Type:")
        self.curve_type = QComboBox()
        self.curve_type.addItems(["straight", "curved"])
        curve_type_layout.addWidget(curve_type_label)
        curve_type_layout.addWidget(self.curve_type)
        curve_type_layout.addStretch()
        line_layout.addLayout(curve_type_layout)
        
        line_width_layout = QHBoxLayout()
        line_width_label = QLabel("Line Width:")
        self.line_width = QSpinBox()
        self.line_width.setRange(1, 10)
        self.line_width.setValue(1)
        line_width_layout.addWidget(line_width_label)
        line_width_layout.addWidget(self.line_width)
        line_width_layout.addStretch()
        line_layout.addLayout(line_width_layout)
        
        curve_layout = QHBoxLayout()
        curve_label = QLabel("Curve Amount:")
        self.curve = QSpinBox()
        self.curve.setRange(0, 100)
        self.curve.setValue(0)
        curve_layout.addWidget(curve_label)
        curve_layout.addWidget(self.curve)
        curve_layout.addStretch()
        line_layout.addLayout(curve_layout)
        
        num_lines_layout = QHBoxLayout()
        num_lines_label = QLabel("Number of Random Lines:")
        self.num_random_lines = QSpinBox()
        self.num_random_lines.setRange(1, 100)
        self.num_random_lines.setValue(10)
        num_lines_layout.addWidget(num_lines_label)
        num_lines_layout.addWidget(self.num_random_lines)
        num_lines_layout.addStretch()
        line_layout.addLayout(num_lines_layout)
        
        self.line_group.setLayout(line_layout)
        main_layout.addWidget(self.line_group)
        
        # Advanced tab layout
        advanced_layout = QVBoxLayout(advanced_tab)
        
        # Scale factor
        scale_layout = QHBoxLayout()
        scale_label = QLabel("Scale Factor:")
        self.scale_factor = QLineEdit()
        self.scale_factor.setText("AUTO")
        scale_layout.addWidget(scale_label)
        scale_layout.addWidget(self.scale_factor)
        scale_layout.addStretch()
        advanced_layout.addLayout(scale_layout)
        
        # Test mode
        test_layout = QHBoxLayout()
        self.test_mode = QCheckBox("Test Mode (Process only first 20 glyphs)")
        test_layout.addWidget(self.test_mode)
        test_layout.addStretch()
        advanced_layout.addLayout(test_layout)
        
        # Debug mode
        debug_layout = QHBoxLayout()
        self.debug_mode = QCheckBox("Debug Mode")
        debug_layout.addWidget(self.debug_mode)
        debug_layout.addStretch()
        advanced_layout.addLayout(debug_layout)
        
        # Debug directory
        debug_dir_layout = QHBoxLayout()
        debug_dir_label = QLabel("Debug Directory:")
        self.debug_dir = QLineEdit()
        self.debug_dir.setPlaceholderText("Select debug output directory...")
        debug_dir_layout.addWidget(debug_dir_label)
        debug_dir_layout.addWidget(self.debug_dir)
        
        debug_dir_button = QPushButton("Browse")
        debug_dir_button.clicked.connect(self.select_debug_dir)
        debug_dir_layout.addWidget(debug_dir_button)
        advanced_layout.addLayout(debug_dir_layout)
        
        # Number of levels
        levels_layout = QHBoxLayout()
        levels_label = QLabel("Number of Levels:")
        self.num_levels = QSpinBox()
        self.num_levels.setRange(2, 10)
        self.num_levels.setValue(2)
        levels_layout.addWidget(levels_label)
        levels_layout.addWidget(self.num_levels)
        levels_layout.addStretch()
        advanced_layout.addLayout(levels_layout)
        
        # Progress bar and completion message
        self.progress_container = QWidget()
        progress_layout = QVBoxLayout(self.progress_container)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(5)
        
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
                margin: 5px;
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
        
        # Initialize dithering options visibility
        self.update_dithering_options(self.dither_mode.currentText())
        
        self.processing_thread = None
        self.message_timer = QTimer()
        self.message_timer.timeout.connect(self.hide_completion_message)

    def update_dithering_options(self, mode):
        self.blue_noise_group.setVisible(mode == "blue_noise")
        self.shape_group.setVisible(mode == "shape")
        self.line_group.setVisible(mode == "line")

    def select_debug_dir(self):
        dir_name = QFileDialog.getExistingDirectory(
            self,
            "Select Debug Directory",
            ""
        )
        if dir_name:
            self.debug_dir.setText(dir_name)

    def get_options(self):
        options = {
            'dithering_mode': self.dither_mode.currentText(),
            'render_mode': self.render_mode.currentText(),
            'reduction_percentage': self.reduction_spinbox.value(),
            'point_size': self.point_size.value(),
            'shape_type': self.shape_type.currentText(),
            'shape_size': self.shape_size.currentText(),
            'margin': self.margin.value(),
            'line_type': self.line_type.currentText(),
            'curve_type': self.curve_type.currentText(),
            'line_width': self.line_width.value(),
            'curve': self.curve.value(),
            'num_random_lines': self.num_random_lines.value(),
            'scale_factor': self.scale_factor.text(),
            'test': self.test_mode.isChecked(),
            'debug': self.debug_mode.isChecked(),
            'debug_dir': self.debug_dir.text() if self.debug_dir.text() else None,
            'num_levels': self.num_levels.value(),
            'draw_images': False
        }
        return options

    def start_conversion(self):
        if not self.input_path.text() or not self.output_path.text():
            return
        
        self.hide_completion_message()
        self.convert_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.processing_thread = FontProcessingThread(
            self.input_path.text(),
            self.output_path.text(),
            self.get_options()
        )
        self.processing_thread.progress.connect(self.update_progress)
        self.processing_thread.finished.connect(self.conversion_finished)
        self.processing_thread.error.connect(self.handle_error)
        self.processing_thread.start()

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

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 
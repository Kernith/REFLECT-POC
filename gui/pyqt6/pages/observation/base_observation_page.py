import time, csv
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QFileDialog, QMessageBox, QTextEdit, 
                            QGroupBox, QGridLayout)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QIcon, QPixmap
from core.util_functions import resource_path, get_current_time
from backend.data.collectors.observation_collector import ObservationCollector
from backend.data.collectors.timer_service import TimerService
from backend.data.exporters.csv_exporter import CSVExporter
from gui.pyqt6.adapters.timer_adapter import PyQt6TimerAdapter

class BaseObservationPage(QWidget):
    def __init__(self, switch_page, app_state):
        super().__init__()
        self.switch_page = switch_page
        self.app_state = app_state
        
        # Initialize backend services
        self.timer_service = TimerService()
        self.csv_exporter = CSVExporter()
        
        # Button behavior configuration
        self.button_behavior = self.get_button_behavior()
        
        self.load_config()
        
        # Initialize observation collector with config
        self.observation_collector = ObservationCollector(self.config)
        
        # Initialize timer adapter
        self.timer_adapter = PyQt6TimerAdapter(self.timer_service, self.update_timer)
        
        self.create_ui()

    def get_button_behavior(self):
        """Override in subclasses to define button behavior"""
        raise NotImplementedError("Subclasses must define button behavior")

    def create_ui(self):
        """Create the user interface"""
        # Main layout with three sections
        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)
        
        # Left section - Student Actions
        left_section = self.create_student_actions_section()
        main_layout.addWidget(left_section)
        
        # Add stretch to push sections apart
        main_layout.addStretch(1)
        
        # Middle section - Student Engagement and Comments
        middle_section = self.create_middle_section()
        main_layout.addWidget(middle_section)
        
        # Add stretch to push sections apart
        main_layout.addStretch(1)
        
        # Right section - Instructor Actions
        right_section = self.create_instructor_actions_section()
        main_layout.addWidget(right_section)
        
        # Add timer and control buttons at the bottom
        control_layout = QVBoxLayout()
        control_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.timer_label = QLabel("Timer: 0:00")
        self.timer_label.setStyleSheet("font-size: 18px;")
        control_layout.addWidget(self.timer_label)
        
        button_row = QHBoxLayout()
        btn_start = QPushButton("Start Observation")
        btn_start.clicked.connect(self.start_observation)
        button_row.addWidget(btn_start)
        
        btn_stop = QPushButton("Stop && Save")
        btn_stop.clicked.connect(self.stop_observation)
        button_row.addWidget(btn_stop)
        
        btn_back = QPushButton("Back to Home")
        btn_back.clicked.connect(self.handle_back_to_home)
        button_row.addWidget(btn_back)
        
        control_layout.addLayout(button_row)
        
        # Combine main sections with controls
        final_layout = QVBoxLayout()
        final_layout.addLayout(main_layout)
        final_layout.addLayout(control_layout)
        
        self.setLayout(final_layout)

    def load_config(self):
        """Load button configuration from the global config"""
        try:
            self.config = self.app_state.get_current_config()
        except Exception as e:
            QMessageBox.critical(self, "Error", "Could not load configuration.")
            self.switch_page(0)
            self.config = {
                "student_actions": [],
                "instructor_actions": [],
                "engagement_images": [],
                "colors": {
                    "student": "#F46715",
                    "engagement": "#4169E1",
                    "instructor": "#0C8346",
                    "comments": "#808080",
                    "carmine": "#931621"
                }
            }

    def create_button_with_image(self, button_data, color, size=(100, 100), category=""):
        """Create button with configurable behavior"""
        btn = QPushButton()
        btn.setFixedSize(*size)
        btn.setToolTip(button_data.get("text", ""))
        
        # Configure button based on behavior type
        behavior = self.button_behavior
        btn.setCheckable(behavior.is_toggle)
        btn.setText(button_data["label"])
        
        # Apply styling based on behavior
        btn.setStyleSheet(behavior.get_style_sheet(color))
        
        # Connect appropriate event handler
        behavior.connect_button(btn, button_data, category, self)
        
        # Load image if present
        self._load_button_image(btn, button_data)
        
        return btn

    def _load_button_image(self, btn, button_data):
        """Common image loading logic"""
        image_path = button_data.get("image", "")
        if image_path:
            try:
                # Use resource_path to make the path PyInstaller-safe
                full_image_path = resource_path(image_path)
                pixmap = QPixmap(full_image_path)
                if not pixmap.isNull():
                    # Scale image to fit button (leave some space for text)
                    scaled_pixmap = pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    icon = QIcon(scaled_pixmap)
                    btn.setIcon(icon)
                    btn.setIconSize(scaled_pixmap.size())
            except Exception as e:
                print(f"Could not load image {full_image_path}: {e}")

    def create_student_actions_section(self):
        """Create the left section for student actions"""
        group = QGroupBox("Student Actions")
        group.setStyleSheet("QGroupBox { border: none; }")
        layout = QGridLayout()
        layout.setContentsMargins(10, 20, 10, 10)
        
        student_buttons = self.config.get("student_actions", [])
        student_color = self.config.get("colors", {}).get("student", "#FFA500")
        
        for i, button_data in enumerate(student_buttons):
            btn = self.create_button_with_image(button_data, student_color, category="Student")
            
            # Calculate row and column for 4-column grid
            row = i // 4
            col = i % 4
            layout.addWidget(btn, row, col)
        
        group.setLayout(layout)
        return group

    def create_middle_section(self):
        """Create the middle section with engagement and comments"""
        group = QGroupBox()
        group.setStyleSheet("QGroupBox { border: none; }")
        layout = QVBoxLayout()
        
        # Top subsection - Student Engagement
        engagement_group = QGroupBox("Student Engagement")
        engagement_group.setStyleSheet("QGroupBox { border: none; }")
        engagement_layout = QHBoxLayout()
        engagement_layout.setContentsMargins(10, 20, 10, 10)
        
        # Load engagement buttons from config
        engagement_buttons = self.config.get("engagement_images", [])
        engagement_color = self.config.get("colors", {}).get("engagement", "#4169E1")
        
        # Store engagement buttons for radio button functionality
        self.engagement_buttons = []
        
        for button_data in engagement_buttons:
            btn = QPushButton()
            btn.setFixedSize(80, 40)
            btn.setText(button_data["label"])
            btn.setToolTip(button_data["text"])
            btn.setCheckable(True)  # Make it a toggle button
            
            # Try to load engagement image
            image_path = button_data.get("image", "")
            if image_path:
                try:
                    # Use resource_path to make the path PyInstaller-safe
                    full_image_path = resource_path(image_path)
                    pixmap = QPixmap(full_image_path)
                    if not pixmap.isNull():
                        scaled_pixmap = pixmap.scaled(30, 30, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                        icon = QIcon(scaled_pixmap)
                        btn.setIcon(icon)
                        btn.setIconSize(scaled_pixmap.size())
                except Exception as e:
                    print(f"Could not load engagement image {full_image_path}: {e}")
            
            # Apply color to button background with toggle styling
            btn.setStyleSheet(f"""
                QPushButton {{ 
                    background-color: {engagement_color}; 
                    color: white; 
                    font-weight: bold; 
                    border: 2px solid {engagement_color};
                }}
                QPushButton:checked {{ 
                    background-color: #FFD700; 
                    color: black; 
                    border: 2px solid #FFD700;
                }}
            """)
            
            # Connect toggle functionality with radio button behavior
            btn.toggled.connect(lambda checked, label=button_data["label"], btn_ref=btn: 
                              self.toggle_engagement_button(label, checked, btn_ref))
            
            # Store button reference for radio button functionality
            self.engagement_buttons.append(btn)
            engagement_layout.addWidget(btn)
        
        engagement_group.setLayout(engagement_layout)
        layout.addWidget(engagement_group)
        
        # Bottom subsection - Comments
        comments_group = QGroupBox("Comments")
        comments_group.setStyleSheet("QGroupBox { border: none; }")
        comments_layout = QVBoxLayout()
        comments_layout.setContentsMargins(10, 20, 10, 10)
        
        self.comment_field = QTextEdit()
        self.comment_field.setPlaceholderText("Enter your observation comments here...")
        self.comment_field.setMaximumHeight(100)
        comments_layout.addWidget(self.comment_field)
        
        btn_save_comment = QPushButton("Save Comment")
        comments_color = self.config.get("colors", {}).get("comments", "#808080")
        # Apply color to save comment button
        btn_save_comment.setStyleSheet(f"QPushButton {{ background-color: {comments_color}; color: white; font-weight: bold; }}")
        btn_save_comment.clicked.connect(self.save_comment)
        comments_layout.addWidget(btn_save_comment)
        
        comments_group.setLayout(comments_layout)
        layout.addWidget(comments_group)
        
        group.setLayout(layout)
        return group

    def create_instructor_actions_section(self):
        """Create the right section for instructor actions"""
        group = QGroupBox("Instructor Actions")
        group.setStyleSheet("QGroupBox { border: none; }")
        layout = QGridLayout()
        layout.setContentsMargins(10, 20, 10, 10)  # Add margins to right section
        
        instructor_buttons = self.config.get("instructor_actions", [])
        instructor_color = self.config.get("colors", {}).get("instructor", "#32CD32")
        
        for i, button_data in enumerate(instructor_buttons):
            btn = self.create_button_with_image(button_data, instructor_color, category="Instructor")
            
            # Calculate row and column for 4-column grid
            row = i // 4
            col = i % 4
            layout.addWidget(btn, row, col)
        
        group.setLayout(layout)
        return group

    def toggle_engagement_button(self, label, checked, clicked_button):
        """Handle engagement button toggle with radio button behavior"""
        if not self.start_time:
            return
        
        if checked:
            # Uncheck all other engagement buttons
            for btn in self.engagement_buttons:
                if btn != clicked_button and btn.isChecked():
                    btn.setChecked(False)
            
            # Update button states
            self.button_states[f"Engagement_{label}"] = True
            print(f"Engagement selected: {label}")
        else:
            # If this button was unchecked, remove it from states
            key = f"Engagement_{label}"
            if key in self.button_states:
                del self.button_states[key]
            print(f"Engagement deselected: {label}")

    def save_comment(self):
        """Save the current comment and clear the field"""
        comment = self.comment_field.toPlainText().strip()
        if comment:
            self.record_response("Comment", comment)  # The value will be set automatically in record_response
            self.comment_field.clear()

    def start_observation(self):
        """Start the observation - override in subclasses for specific behavior"""
        self.observation_collector.start_observation()
        self.timer_adapter.start(100)

    def update_timer(self):
        if self.timer_service.is_running():
            self.timer_label.setText(f"Timer: {self.timer_service.format_time()}")

    def record_response(self, category, response, value=None):
        """Record a response with optional value - override in subclasses for specific behavior"""
        self.observation_collector.record_response(category, response, value)

    def stop_observation(self):
        """Stop observation and save data - override in subclasses for specific behavior"""
        self.timer_adapter.stop()
        
        # Get responses from collector
        responses = self.observation_collector.get_responses()
        if not responses:
            QMessageBox.information(self, "No data", "No observations recorded.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Save Observation Data", "", "CSV Files (*.csv)"
        )
        if path:
            # Create metadata for export
            current_config = self.app_state.get_current_config()
            start_time = self.observation_collector.start_time
            duration = self.observation_collector.get_elapsed_time()
            metadata = self.csv_exporter.create_metadata(current_config, start_time, duration)
            
            # Export using CSV exporter
            success = self.csv_exporter.export_observations(responses, path, metadata)
            if success:
                QMessageBox.information(self, "Saved", f"Observation data saved to:\n{path}")
            else:
                QMessageBox.critical(self, "Error", "Failed to save observation data")
        self.switch_page(0)

    def handle_back_to_home(self):
        """Handle back to home button - override in subclasses for specific behavior"""
        self.switch_page(0)

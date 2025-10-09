import time, csv, json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QFileDialog, QMessageBox, QTextEdit, 
                            QGroupBox, QGridLayout)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QIcon, QPixmap
from utils.paths import resource_path

class ObservationPage(QWidget):
    def __init__(self, switch_page):
        super().__init__()
        self.switch_page = switch_page
        self.start_time = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.responses = []
        
        # Load button configuration
        self.config = self.load_config()

        # Main layout with three sections
        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)  # Add spacing between sections (default is usually 0)
        
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
        
        self.timer_label = QLabel("Timer: 0.0 s")
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
        btn_back.clicked.connect(lambda: switch_page(0))
        button_row.addWidget(btn_back)
        
        control_layout.addLayout(button_row)
        
        # Combine main sections with controls
        final_layout = QVBoxLayout()
        final_layout.addLayout(main_layout)
        final_layout.addLayout(control_layout)
        
        self.setLayout(final_layout)

    def load_config(self):
        """Load button configuration from config.json"""
        try:
            config_path = resource_path("config.json")
            with open(config_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            QMessageBox.critical(self, "Error", "Could not load configuration.")
            self.switch_page(0)
            return {}

    def create_button_with_image(self, button_data, color, size=(100, 100)):
        """Create a button with image and text"""
        btn = QPushButton()
        btn.setFixedSize(*size)
        btn.setToolTip(button_data.get("text", ""))
        
        # Set button text
        btn.setText(button_data["label"])
        
        # Try to load and set image if path exists
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
        
        # Apply color to button background
        btn.setStyleSheet(f"QPushButton {{ background-color: {color}; color: white; font-weight: bold; }}")
        
        return btn

    def create_student_actions_section(self):
        """Create the left section for student actions"""
        group = QGroupBox("Student Actions")
        group.setStyleSheet("QGroupBox { border: none; }")
        layout = QGridLayout()
        layout.setContentsMargins(10, 20, 10, 10)
        
        student_buttons = self.config.get("student_actions", [])
        student_color = self.config.get("colors", {}).get("student", "#FFA500")
        
        for i, button_data in enumerate(student_buttons):
            btn = self.create_button_with_image(button_data, student_color)
            btn.clicked.connect(lambda _, label=button_data["label"]: 
                              self.record_response("Student", label))
            
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
        
        engagement_buttons = [
            ("Low", "Low engagement"),
            ("Medium", "Medium engagement"), 
            ("High", "High engagement")
        ]
        
        engagement_color = self.config.get("colors", {}).get("engagement", "#4169E1")
        engagement_images = self.config.get("engagement_images", {})
        
        for label, tooltip in engagement_buttons:
            btn = QPushButton()
            btn.setFixedSize(80, 40)
            btn.setText(label)
            btn.setToolTip(tooltip)
            
            # Try to load engagement image
            image_path = engagement_images.get(label, "")
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
            
            # Apply color to button background
            btn.setStyleSheet(f"QPushButton {{ background-color: {engagement_color}; color: white; font-weight: bold; }}")
            btn.clicked.connect(lambda _, label=label: 
                              self.record_response("Engagement", label))
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
            btn = self.create_button_with_image(button_data, instructor_color)
            btn.clicked.connect(lambda _, label=button_data["label"]: 
                              self.record_response("Instructor", label))
            
            # Calculate row and column for 4-column grid
            row = i // 4
            col = i % 4
            layout.addWidget(btn, row, col)
        
        group.setLayout(layout)
        return group

    def save_comment(self):
        """Save the current comment and clear the field"""
        comment = self.comment_field.toPlainText().strip()
        if comment:
            self.record_response("Comment", comment)
            self.comment_field.clear()

    def start_observation(self):
        self.start_time = time.time()
        self.responses = []
        self.timer.start(100)

    def update_timer(self):
        if self.start_time:
            elapsed = time.time() - self.start_time
            self.timer_label.setText(f"Timer: {elapsed:.1f} s")

    def record_response(self, category, response):
        if not self.start_time:
            return
        t = time.time() - self.start_time
        self.responses.append((t, category, response))
        print(f"Recorded {category}: {response} at {t:.1f}s")

    def stop_observation(self):
        self.timer.stop()
        if not self.responses:
            QMessageBox.information(self, "No data", "No observations recorded.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Save Observation Data", "", "CSV Files (*.csv)"
        )
        if path:
            with open(path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["time_s", "category", "response"])
                writer.writerows(self.responses)
            QMessageBox.information(self, "Saved", f"Observation data saved to:\n{path}")
        self.switch_page(0)
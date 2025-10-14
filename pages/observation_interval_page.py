import time, csv
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QFileDialog, QMessageBox, QTextEdit, 
                            QGroupBox, QGridLayout)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QIcon, QPixmap
from utils.paths import resource_path

class ObservationIntervalPage(QWidget):
    def __init__(self, switch_page, app_state):
        super().__init__()
        self.switch_page = switch_page
        self.app_state = app_state
        self.start_time = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.responses = []
        
        # Track button states for toggle functionality
        self.button_states = {}
        self.interval_timer = QTimer()
        self.interval_timer.timeout.connect(self.save_interval_data)
        
        # Load button configuration
        self.load_config()
        self.create_ui()

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
            # Get timer interval from config
            self.timer_interval = self.config.get("timer_interval", 120) * 1000  # Convert to milliseconds
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
            self.timer_interval = 120000  # Default 2 minutes

    def create_button_with_image(self, button_data, color, size=(100, 100), category="", is_toggle=True):
        """Create a button with image and text"""
        btn = QPushButton()
        btn.setFixedSize(*size)
        btn.setToolTip(button_data.get("text", ""))
        btn.setCheckable(is_toggle)  # Make it a toggle button
        
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
        if is_toggle:
            btn.setStyleSheet(f"""
                QPushButton {{ 
                    background-color: {color}; 
                    color: white; 
                    font-weight: bold; 
                    border: 2px solid {color};
                }}
                QPushButton:checked {{ 
                    background-color: #FFD700; 
                    color: black; 
                    border: 2px solid #FFD700;
                }}
            """)
        else:
            btn.setStyleSheet(f"QPushButton {{ background-color: {color}; color: white; font-weight: bold; overflow-wrap: break-word; width: 15ch;}}")
        
        # Connect toggle functionality
        if is_toggle:
            btn.toggled.connect(lambda checked, label=button_data["label"], cat=category: 
                              self.toggle_button(cat, label, checked))
        
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

    def toggle_button(self, category, label, checked):
        """Handle button toggle state"""
        if not self.start_time:
            return
        
        key = f"{category}_{label}"
        if checked:
            self.button_states[key] = True
            print(f"Toggled ON: {category} - {label}")
        else:
            self.button_states[key] = False
            print(f"Toggled OFF: {category} - {label}")

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
            self.record_response("Comment", comment)
            self.comment_field.clear()

    def start_observation(self):
        self.start_time = time.time()
        self.responses = []
        self.button_states = {}
        self.timer.start(100)
        self.interval_timer.start(self.timer_interval)  # Start interval timer

    def update_timer(self):
        if self.start_time:
            elapsed = time.time() - self.start_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            self.timer_label.setText(f"Timer: {minutes}:{seconds:02d}")

    def save_interval_data(self):
        """Save data for all toggled buttons and reset them"""
        if not self.start_time:
            return
        
        current_time = time.time() - self.start_time
        
        # Save data for all toggled buttons
        for key, is_toggled in self.button_states.items():
            if is_toggled:
                category, label = key.split("_", 1)
                self.responses.append((current_time, category, label))
                print(f"Interval save: {category} - {label} at {current_time:.1f}s")
        
        # Reset all buttons
        self.reset_all_buttons()
        
        # Clear button states
        self.button_states = {}

    def reset_all_buttons(self):
        """Reset all toggle buttons to unchecked state"""
        # Find all toggle buttons and uncheck them
        for widget in self.findChildren(QPushButton):
            if widget.isCheckable():
                widget.setChecked(False)

    def record_response(self, category, response):
        if not self.start_time:
            return
        t = time.time() - self.start_time
        self.responses.append((t, category, response))
        print(f"Recorded {category}: {response} at {t:.1f}s")

    def stop_observation(self):
        self.timer.stop()
        self.interval_timer.stop()
        
        # Save any remaining toggled buttons before stopping
        if self.start_time:
            current_time = time.time() - self.start_time
            for key, is_toggled in self.button_states.items():
                if is_toggled:
                    category, label = key.split("_", 1)
                    self.responses.append((current_time, category, label))
        
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

    def handle_back_to_home(self):
        """Handle back to home button with confirmation if timer is running"""
        if self.start_time:
            # Timer is running, show confirmation dialog
            reply = QMessageBox.question(
                self, 
                "Confirm Navigation", 
                "An observation is currently running. Are you sure you want to go back to home? This will stop the current observation.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                # Stop the observation and go back
                self.timer.stop()
                self.interval_timer.stop()
                self.start_time = None
                self.switch_page(0)
        else:
            # Timer is not running, go back directly
            self.switch_page(0)
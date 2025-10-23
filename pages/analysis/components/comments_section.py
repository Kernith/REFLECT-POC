import pandas as pd
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QTextEdit
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


class CommentsSection:
    """Component for creating comments section"""
    
    def create_section(self, df: pd.DataFrame) -> QFrame:
        """Create comments section with timestamps"""
        comments_frame = QFrame()
        comments_layout = QVBoxLayout()
        
        title = QLabel("Comments Timeline")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        comments_layout.addWidget(title)
        
        # Filter for comments/notes data
        comments_data = df[df['category'].str.contains('Comment|Note|comment|note', case=False, na=False)]
        
        if comments_data.empty:
            no_comments_label = QLabel("No comments found in the data")
            no_comments_label.setStyleSheet("color: gray; font-style: italic; padding: 20px;")
            no_comments_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            comments_layout.addWidget(no_comments_label)
        else:
            # Sort by timestamp
            comments_sorted = comments_data.sort_values('time_s')
            
            # Create scrollable text area for comments
            comments_text = QTextEdit()
            comments_text.setReadOnly(True)
            comments_text.setMaximumHeight(200)  # Limit height to keep it manageable
            comments_text.setStyleSheet("border: none; background: transparent;")
            
            # Format comments with timestamps
            comments_content = ""
            for _, row in comments_sorted.iterrows():
                timestamp = row['time_s']
                minutes = int(timestamp // 60)
                seconds = int(timestamp % 60)
                time_str = f"{minutes:02d}:{seconds:02d}"
                
                comment_text = row.get('response', 'No comment text')
                value = row.get('value', '')
                
                # Format the comment entry
                comments_content += f"<b>[{time_str}]</b> {comment_text}"
                if value and str(value).strip():
                    comments_content += f" <i>({value})</i>"
                comments_content += "<br><br>"
            
            comments_text.setHtml(comments_content)
            comments_layout.addWidget(comments_text)
            
            # Add summary info
            total_comments = len(comments_sorted)
            time_span = comments_sorted['time_s'].max() - comments_sorted['time_s'].min()
            summary_text = f"<b>Summary:</b> {total_comments} comments over {time_span:.1f} seconds"
            summary_label = QLabel(summary_text)
            summary_label.setStyleSheet("color: #666; font-size: 12px; padding: 5px;")
            comments_layout.addWidget(summary_label)
        
        comments_frame.setLayout(comments_layout)
        return comments_frame

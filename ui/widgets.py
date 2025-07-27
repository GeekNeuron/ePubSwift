# ui/widgets.py
from PySide6.QtWidgets import QProgressBar, QWidget, QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFrame
from PySide6.QtGui import QPainter, QPen, QColor
from PySide6.QtCore import Qt, Signal, QRect, QTimer

class ClickableProgressBar(QProgressBar):
    """A custom progress bar that is clickable and has reactive text color."""
    jump_requested = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setTextVisible(False) # We draw the text manually for reactive color

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        
        progress_ratio = self.value() / self.maximum() if self.maximum() != 0 else 0
        chunk_width = int(self.width() * progress_ratio)
        
        text = f"{self.value()}%"
        font = self.font()
        font.setPointSize(9)
        font.setBold(True)
        painter.setFont(font)
        
        # 1. Draw the white text part (clipped to the blue chunk)
        pen_white = QPen(QColor("white"))
        painter.setPen(pen_white)
        clip_white = QRect(0, 0, chunk_width, self.height())
        painter.save()
        painter.setClipRect(clip_white)
        painter.drawText(self.rect(), Qt.AlignCenter, text)
        painter.restore()
        
        # 2. Draw the dark blue text part (clipped to the gray background)
        pen_blue = QPen(QColor("#345B9A"))
        painter.setPen(pen_blue)
        clip_blue = QRect(chunk_width, 0, self.width() - chunk_width, self.height())
        painter.save()
        painter.setClipRect(clip_blue)
        painter.drawText(self.rect(), Qt.AlignCenter, text)
        painter.restore()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.process_jump(event.pos())

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton: self.process_jump(event.pos())
            
    def process_jump(self, pos):
        percentage = (pos.x() / self.width()) * 100
        self.setValue(int(percentage))
        self.jump_requested.emit(percentage)


class LoadingSpinner(QWidget):
    """A modal loading spinner animation."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setWindowModality(Qt.ApplicationModal)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_angle)
        self.timer.setInterval(20) # Controls animation speed

    def update_angle(self):
        self.angle = (self.angle + 10) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw a semi-transparent background overlay
        painter.fillRect(self.rect(), QColor(240, 240, 240, 150))
        
        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(self.angle)
        
        pen = QPen(QColor("#345B9A"), 8)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        
        # Draw a smaller arc for a more subtle animation
        painter.drawArc(QRect(-20, -20, 40, 40), 0, 270 * 16)

    def start_animation(self):
        if self.parent():
            self.setGeometry(self.parent().rect())
        self.timer.start()
        self.show()

    def stop_animation(self):
        self.timer.stop()
        self.hide()


class AboutDialog(QDialog):
    """A dialog to show application information, styled to match the main UI."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About ePub Swift")
        self.setFixedSize(380, 200)
        self.setWindowModality(Qt.ApplicationModal)

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setContentsMargins(20, 15, 20, 15)

        # --- Top Section ---
        title_font = self.font()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label = QLabel("ePub Swift v1.0")
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        dev_label = QLabel("Developed by GeekNeuron")
        dev_label.setAlignment(Qt.AlignCenter)
        
        main_layout.addWidget(title_label)
        main_layout.addWidget(dev_label)
        
        # --- Separator Line ---
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.HLine)
        separator1.setObjectName("Separator")
        main_layout.addWidget(separator1)

        # --- Middle Section ---
        support_label = QLabel("For support, contributions, and contact:")
        support_label.setAlignment(Qt.AlignCenter)
        
        links_widget = QWidget()
        links_layout = QHBoxLayout(links_widget)
        links_layout.setAlignment(Qt.AlignCenter)
        links_layout.setSpacing(20)

        # Using rich text (HTML) in labels to create clickable links
        github_link = "<a href='https://github.com/GeekNeuron' style='text-decoration:none; color:#345B9A;'>GitHub</a>"
        telegram_link = "<a href='https://t.me/GeekNeuron' style='text-decoration:none; color:#345B9A;'>Telegram</a>"
        twitter_link = "<a href='https://twitter.com/GeekNeuron' style='text-decoration:none; color:#345B9A;'>Twitter</a>"
        
        github_label = QLabel(github_link)
        github_label.setOpenExternalLinks(True)
        telegram_label = QLabel(telegram_link)
        telegram_label.setOpenExternalLinks(True)
        twitter_label = QLabel(twitter_link)
        twitter_label.setOpenExternalLinks(True)

        links_layout.addWidget(github_label)
        links_layout.addWidget(telegram_label)
        links_layout.addWidget(twitter_label)
        
        main_layout.addWidget(support_label)
        main_layout.addWidget(links_widget)
        main_layout.addStretch()

        # Apply stylesheet for a clean look
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QFrame#Separator {
                border: none;
                border-top: 1px dashed #cccccc;
                margin-top: 10px;
                margin-bottom: 10px;
            }
            QLabel {
                color: #2c3e50;
            }
        """)

# ui/widgets.py
from PySide6.QtWidgets import QProgressBar, QWidget
from PySide6.QtGui import QPainter, QPen, QColor
from PySide6.QtCore import Qt, Signal, QRect, QTimer

# ClickableProgressBar remains mostly the same
class ClickableProgressBar(QProgressBar):
    jump_requested = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setTextVisible(False)

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
        
        pen_white = QPen(QColor("white"))
        painter.setPen(pen_white)
        clip_white = QRect(0, 0, chunk_width, self.height())
        painter.save()
        painter.setClipRect(clip_white)
        painter.drawText(self.rect(), Qt.AlignCenter, text)
        painter.restore()
        
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


# New Loading Spinner Widget
class LoadingSpinner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setWindowModality(Qt.ApplicationModal)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_angle)
        self.timer.setInterval(20) # 50 FPS

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
        
        # Draw an arc
        painter.drawArc(QRect(-20, -20, 40, 40), 0, 270 * 16)

    def start_animation(self):
        if self.parent():
            self.setGeometry(self.parent().rect())
        self.timer.start()
        self.show()

    def stop_animation(self):
        self.timer.stop()
        self.hide()

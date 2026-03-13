import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtCore import QTimer, QDateTime, Qt
from PyQt5.QtGui import QFont, QFontDatabase


THEMES = [
    {
        "name": "ICE BLUE",
        "bg": "#000d1a",
        "primary": "#00cfff",
        "dim": "#005566",
        "btn_bg": "#001a2a",
    },
    {
        "name": "AMBER GOLD",
        "bg": "#0d0800",
        "primary": "#ffaa00",
        "dim": "#664400",
        "btn_bg": "#1a1000",
    },
    {
        "name": "PURPLE NEON",
        "bg": "#0a0010",
        "primary": "#cc44ff",
        "dim": "#551166",
        "btn_bg": "#120020",
    },
    {
        "name": "CYBER RED",
        "bg": "#0d0000",
        "primary": "#ff2244",
        "dim": "#661122",
        "btn_bg": "#1a0008",
    },
]


class CountdownClock(QWidget):
    def __init__(self):
        super().__init__()
        self.flash_timer = QTimer(self)
        self.flash_state = False
        self._drag_pos = None
        self.theme_index = 0
        self.theme_timer = QTimer(self)

        tomorrow = QDateTime.currentDateTime().addDays(1)
        self.exam_time = QDateTime.fromString("17-03-2026 12:00:00", "dd-MM-yyyy hh:mm:ss")
        
        self.initUI()

    def initUI(self):
        self.setWindowTitle("GET209 Exam Countdown")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setGeometry(400, 300, 600, 380)

        font_path = os.path.join(os.path.dirname(__file__), "DS-DIGIT.TTF")
        font_id = QFontDatabase.addApplicationFont(font_path)
        self.font_family = None
        if font_id != -1:
            self.font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(30, 16, 30, 20)

        # ── Custom title bar ──────────────────────────────────────────
        title_bar = QHBoxLayout()

        self.title_label = QLabel("GET207 EXAM")
        self.title_label.setStyleSheet(
            "font-size: 20px; letter-spacing: 8px; background: transparent;"
        )

        self.minimize_btn = QPushButton("−")
        self.minimize_btn.setFixedSize(32, 32)
        self.minimize_btn.clicked.connect(self.showMinimized)

        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(32, 32)
        self.close_btn.clicked.connect(self.close)

        title_bar.addWidget(self.title_label)
        title_bar.addStretch()
        title_bar.addWidget(self.minimize_btn)
        title_bar.addWidget(self.close_btn)
        main_layout.addLayout(title_bar)

        # ── Status label ──────────────────────────────────────────────
        self.status_label = QLabel("COUNTDOWN TO EXAM")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(
            "font-size: 13px; letter-spacing: 4px; background: transparent;"
        )
        main_layout.addWidget(self.status_label)

        # ── Time display boxes ────────────────────────────────────────
        hbox = QHBoxLayout()
        hbox.setSpacing(14)

        self.units = {}
        for unit in ["DAYS", "HOURS", "MINS", "SECS"]:
            box = QWidget()
            box_layout = QVBoxLayout()
            box_layout.setSpacing(2)

            val_label = QLabel("00")
            val_label.setAlignment(Qt.AlignCenter)
            val_label.setStyleSheet("font-size: 64px; border: none;")
            if self.font_family:
                val_label.setFont(QFont(self.font_family, 64))

            unit_label = QLabel(unit)
            unit_label.setAlignment(Qt.AlignCenter)
            unit_label.setStyleSheet("font-size: 13px; letter-spacing: 4px; border: none;")

            box_layout.addWidget(val_label)
            box_layout.addWidget(unit_label)
            box.setLayout(box_layout)
            hbox.addWidget(box)
            self.units[unit] = (box, val_label, unit_label)

        main_layout.addLayout(hbox)
        self.setLayout(main_layout)

        # ── Timers ────────────────────────────────────────────────────
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(1000)

        self.flash_timer.timeout.connect(self.flash_display)

        # Cycle theme every 10 seconds
        self.theme_timer.timeout.connect(self.next_theme)
        self.theme_timer.start(10000)

        self.apply_theme(THEMES[self.theme_index])
        self.update_countdown()

    # ── Drag to move ──────────────────────────────────────────────────
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos:
            self.move(event.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    # ── Theme cycling ─────────────────────────────────────────────────
    def next_theme(self):
        self.theme_index = (self.theme_index + 1) % len(THEMES)
        self.apply_theme(THEMES[self.theme_index])

    def apply_theme(self, theme):
        self.current_theme = theme
        p = theme["primary"]
        d = theme["dim"]
        bg = theme["bg"]
        btn_bg = theme["btn_bg"]

        self.setStyleSheet(f"background-color: {bg}; border-radius: 12px;")

        self.title_label.setStyleSheet(
            f"font-size: 20px; color: {p}; letter-spacing: 8px; background: transparent;"
        )
        self.status_label.setStyleSheet(
            f"font-size: 13px; color: {p}; letter-spacing: 4px; background: transparent;"
        )

        for btn in [self.minimize_btn, self.close_btn]:
            btn.setStyleSheet(
                f"QPushButton {{ background: {btn_bg}; color: {p}; border: 1px solid {p};"
                f"border-radius: 16px; font-size: 14px; }}"
                f"QPushButton:hover {{ background: #ff4444; color: white; border-color: #ff4444; }}"
            )

        for unit, (box, val_label, unit_label) in self.units.items():
            box.setStyleSheet(
                f"border: 2px solid {p}; border-radius: 10px; padding: 6px;"
            )
            val_label.setStyleSheet(f"font-size: 64px; color: {p}; border: none;")
            unit_label.setStyleSheet(
                f"font-size: 13px; color: {d}; letter-spacing: 4px; border: none;"
            )

    def set_color(self, color, dim=None):
        for unit, (box, val_label, unit_label) in self.units.items():
            box.setStyleSheet(
                f"border: 2px solid {color}; border-radius: 10px; padding: 6px;"
            )
            val_label.setStyleSheet(f"font-size: 64px; color: {color}; border: none;")
            if dim:
                unit_label.setStyleSheet(
                    f"font-size: 13px; color: {dim}; letter-spacing: 4px; border: none;"
                )

    # ── Countdown logic ───────────────────────────────────────────────
    def update_countdown(self):
        now = QDateTime.currentDateTime()
        secs_remaining = now.secsTo(self.exam_time)

        if secs_remaining <= 0:
            self.timer.stop()
            self.theme_timer.stop()
            if not self.flash_timer.isActive():
                self.flash_timer.start(500)
            for _, val_label, _ in self.units.values():
                val_label.setText("00")
            self.status_label.setText("⚠  EXAM TIME!  ⚠")
            self.status_label.setStyleSheet(
                "font-size: 13px; color: #ff0000; letter-spacing: 4px; background: transparent;"
            )
            return

        days    = secs_remaining // 86400
        hours   = (secs_remaining % 86400) // 3600
        minutes = (secs_remaining % 3600) // 60
        seconds = secs_remaining % 60

        self.units["DAYS"][1].setText(f"{days:02d}")
        self.units["HOURS"][1].setText(f"{hours:02d}")
        self.units["MINS"][1].setText(f"{minutes:02d}")
        self.units["SECS"][1].setText(f"{seconds:02d}")

        # Under 1 hour — override to red warning regardless of theme
        if secs_remaining <= 3600:
            self.theme_timer.stop()
            self.set_color("#ff4444", "#661111")
            self.status_label.setText("⚠  GET209 EXAM — UNDER 1 HOUR!  ⚠")
            self.status_label.setStyleSheet(
                "font-size: 13px; color: #ff4444; letter-spacing: 4px; background: transparent;"
            )

    def flash_display(self):
        self.flash_state = not self.flash_state
        color = "#ff4444" if self.flash_state else "#ff0000"
        self.set_color(color)


if __name__ == "__main__":
    # Start on Ice Blue (index 0)
    app = QApplication(sys.argv)
    clock = CountdownClock()
    clock.show()
    sys.exit(app.exec_())
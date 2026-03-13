import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout,
                              QHBoxLayout, QPushButton, QSpinBox)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QFontDatabase


class Stopwatch(QWidget):
    def __init__(self):
        super().__init__()
        self.timer = QTimer(self)
        self.elapsed_ms = 0
        self.running = False
        self.countdown_mode = False
        self.target_ms = 0
        self.flash_timer = QTimer(self)
        self.flash_state = False
        self.font_family = None
        self._drag_pos = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Stopwatch")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setGeometry(400, 250, 400, 380)
        self.setStyleSheet("background-color: #0a0a1a; border-radius: 12px;")

        # Load DS-DIGIT font
        font_path = os.path.join(os.path.dirname(__file__), "DS-DIGIT.TTF")
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            self.font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

        main_layout = QVBoxLayout()
        main_layout.setSpacing(14)
        main_layout.setContentsMargins(30, 16, 30, 20)

        # ── Custom title bar ──────────────────────────────────────────
        title_bar = QHBoxLayout()

        title = QLabel("STOPWATCH")
        title.setStyleSheet("font-size: 20px; color: #4488ff; letter-spacing: 8px; background: transparent;")

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(32, 32)
        close_btn.setStyleSheet(
            "QPushButton { background: #1a1a3a; color: #4488ff; border: 1px solid #4488ff;"
            "border-radius: 16px; font-size: 14px; }"
            "QPushButton:hover { background: #ff4444; color: white; border-color: #ff4444; }"
        )
        close_btn.clicked.connect(self.close)

        minimize_btn = QPushButton("−")
        minimize_btn.setFixedSize(32, 32)
        minimize_btn.setStyleSheet(
            "QPushButton { background: #1a1a3a; color: #4488ff; border: 1px solid #4488ff;"
            "border-radius: 16px; font-size: 18px; }"
            "QPushButton:hover { background: #223366; }"
        )
        minimize_btn.clicked.connect(self.showMinimized)

        title_bar.addWidget(title)
        title_bar.addStretch()
        title_bar.addWidget(minimize_btn)
        title_bar.addWidget(close_btn)
        main_layout.addLayout(title_bar)

        # ── Duration picker ───────────────────────────────────────────
        picker_widget = QWidget()
        picker_widget.setStyleSheet(
            "border: 1px solid #4488ff; border-radius: 8px; padding: 6px;"
        )
        picker_layout = QHBoxLayout()
        picker_layout.setSpacing(10)

        picker_title = QLabel("Set Duration:")
        picker_title.setStyleSheet("font-size: 14px; color: #aaaacc; border: none;")
        picker_layout.addWidget(picker_title)

        self.hr_spin = QSpinBox()
        self.hr_spin.setRange(0, 23)
        self.hr_spin.setSuffix(" hr")
        self._style_spinbox(self.hr_spin)

        self.min_spin = QSpinBox()
        self.min_spin.setRange(0, 59)
        self.min_spin.setSuffix(" min")
        self._style_spinbox(self.min_spin)

        self.sec_spin = QSpinBox()
        self.sec_spin.setRange(0, 59)
        self.sec_spin.setSuffix(" sec")
        self._style_spinbox(self.sec_spin)

        set_btn = QPushButton("SET")
        set_btn.setFixedWidth(70)
        set_btn.setStyleSheet(
            "QPushButton { background-color: #4488ff; color: white; border-radius: 6px;"
            "font-size: 13px; padding: 6px; border: none; }"
            "QPushButton:hover { background-color: #66aaff; }"
            "QPushButton:pressed { background-color: #2266dd; }"
        )
        set_btn.clicked.connect(self.set_duration)

        clear_btn = QPushButton("CLEAR")
        clear_btn.setFixedWidth(70)
        clear_btn.setStyleSheet(
            "QPushButton { background-color: #223366; color: #aaaacc; border-radius: 6px;"
            "font-size: 13px; padding: 6px; border: 1px solid #4488ff; }"
            "QPushButton:hover { background-color: #334477; }"
        )
        clear_btn.clicked.connect(self.clear_duration)

        picker_layout.addWidget(self.hr_spin)
        picker_layout.addWidget(self.min_spin)
        picker_layout.addWidget(self.sec_spin)
        picker_layout.addWidget(set_btn)
        picker_layout.addWidget(clear_btn)
        picker_layout.addStretch()
        picker_widget.setLayout(picker_layout)
        main_layout.addWidget(picker_widget)

        # ── Mode label ────────────────────────────────────────────────
        self.mode_label = QLabel("STOPWATCH MODE")
        self.mode_label.setAlignment(Qt.AlignCenter)
        self.mode_label.setStyleSheet(
            "font-size: 13px; color: #4488ff; letter-spacing: 4px; background: transparent;"
        )
        main_layout.addWidget(self.mode_label)

        # ── Time display boxes ────────────────────────────────────────
        hbox = QHBoxLayout()
        hbox.setSpacing(14)

        self.unit_widgets = {}
        for unit in ["HH", "MM", "SS", "MS"]:
            box = QWidget()
            box.setStyleSheet(
                "border: 2px solid #4488ff; border-radius: 10px; padding: 6px;"
            )
            box_layout = QVBoxLayout()
            box_layout.setSpacing(2)

            val_label = QLabel("00")
            val_label.setAlignment(Qt.AlignCenter)
            val_label.setStyleSheet("font-size: 88px; color: #4488ff; border: none;")
            if self.font_family:
                val_label.setFont(QFont(self.font_family, 88))

            unit_label = QLabel(unit)
            unit_label.setAlignment(Qt.AlignCenter)
            unit_label.setStyleSheet(
                "font-size: 14px; color: #556688; letter-spacing: 4px; border: none;"
            )

            box_layout.addWidget(val_label)
            box_layout.addWidget(unit_label)
            box.setLayout(box_layout)
            hbox.addWidget(box)
            self.unit_widgets[unit] = (box, val_label)

        main_layout.addLayout(hbox)

        # ── Control buttons ───────────────────────────────────────────
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(16)

        self.start_btn = QPushButton("▶  START")
        self.reset_btn = QPushButton("↺  RESET")

        for btn in [self.start_btn, self.reset_btn]:
            btn.setFixedHeight(48)
            btn.setStyleSheet(
                "QPushButton { background-color: #112244; color: #4488ff;"
                "border: 2px solid #4488ff; border-radius: 10px;"
                "font-size: 16px; letter-spacing: 2px; }"
                "QPushButton:hover { background-color: #223366; }"
                "QPushButton:pressed { background-color: #4488ff; color: white; }"
            )

        self.start_btn.clicked.connect(self.toggle_start)
        self.reset_btn.clicked.connect(self.reset)

        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.reset_btn)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

        # ── Timers ────────────────────────────────────────────────────
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.update_display)
        self.flash_timer.timeout.connect(self.flash_display)

    # ── Drag to move (frameless window) ──────────────────────────────
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos:
            self.move(event.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    # ── Helpers ───────────────────────────────────────────────────────
    def _style_spinbox(self, spinbox):
        spinbox.setFixedWidth(95)
        spinbox.setStyleSheet(
            "QSpinBox { background-color: #112244; color: #4488ff;"
            "border: 1px solid #4488ff; border-radius: 6px; font-size: 14px; padding: 4px; }"
            "QSpinBox::up-button, QSpinBox::down-button { background-color: #223366; border: none; }"
        )

    def set_color(self, color):
        for unit, (box, val_label) in self.unit_widgets.items():
            box.setStyleSheet(
                f"border: 2px solid {color}; border-radius: 10px; padding: 6px;"
            )
            val_label.setStyleSheet(f"font-size: 88px; color: {color}; border: none;")

    # ── Duration controls ─────────────────────────────────────────────
    def set_duration(self):
        h = self.hr_spin.value()
        m = self.min_spin.value()
        s = self.sec_spin.value()
        total = (h * 3600 + m * 60 + s) * 1000
        if total > 0:
            self.target_ms = total
            self.elapsed_ms = 0
            self.countdown_mode = True
            self.running = False
            self.timer.stop()
            self.flash_timer.stop()
            self.start_btn.setText("▶  START")
            self.mode_label.setText("COUNTDOWN MODE")
            self.mode_label.setStyleSheet(
                "font-size: 13px; color: #ff9900; letter-spacing: 4px; background: transparent;"
            )
            self.set_color("#ff9900")
            self.update_display()

    def clear_duration(self):
        self.hr_spin.setValue(0)
        self.min_spin.setValue(0)
        self.sec_spin.setValue(0)
        self.countdown_mode = False
        self.target_ms = 0
        self.elapsed_ms = 0
        self.running = False
        self.timer.stop()
        self.flash_timer.stop()
        self.start_btn.setText("▶  START")
        self.mode_label.setText("STOPWATCH MODE")
        self.mode_label.setStyleSheet(
            "font-size: 13px; color: #4488ff; letter-spacing: 4px; background: transparent;"
        )
        self.set_color("#4488ff")
        self.update_display()

    # ── Stopwatch controls ────────────────────────────────────────────
    def toggle_start(self):
        if self.running:
            self.timer.stop()
            self.running = False
            self.start_btn.setText("▶  START")
        else:
            self.timer.start()
            self.running = True
            self.start_btn.setText("⏸  PAUSE")

    def reset(self):
        self.timer.stop()
        self.flash_timer.stop()
        self.running = False
        self.elapsed_ms = 0
        self.start_btn.setText("▶  START")
        color = "#ff9900" if self.countdown_mode else "#4488ff"
        self.set_color(color)
        self.update_display()

    # ── Display update ────────────────────────────────────────────────
    def update_display(self):
        if self.running:
            self.elapsed_ms += 10

        if self.countdown_mode and self.target_ms > 0:
            remaining = max(0, self.target_ms - self.elapsed_ms)
            self._render_time(remaining)
            if remaining == 0 and self.running:
                self.timer.stop()
                self.running = False
                self.start_btn.setText("▶  START")
                if not self.flash_timer.isActive():
                    self.flash_timer.start(400)
        else:
            self._render_time(self.elapsed_ms)

    def _render_time(self, ms):
        hours   = ms // 3600000
        minutes = (ms % 3600000) // 60000
        seconds = (ms % 60000) // 1000
        millis  = (ms % 1000) // 10
        self.unit_widgets["HH"][1].setText(f"{hours:02d}")
        self.unit_widgets["MM"][1].setText(f"{minutes:02d}")
        self.unit_widgets["SS"][1].setText(f"{seconds:02d}")
        self.unit_widgets["MS"][1].setText(f"{millis:02d}")

    def flash_display(self):
        self.flash_state = not self.flash_state
        color = "#ff4444" if self.flash_state else "#ff9900"
        self.set_color(color)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    sw = Stopwatch()
    sw.show()
    sys.exit(app.exec_())
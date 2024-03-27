#!/usr/bin/env python
#
# SPDX-FileCopyrightText: 2024 Sascha Brawer <sascha@brawer.ch>
# SPDX-License-Identifier: MIT

import os
import sys

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QKeyEvent, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import QFileDialog

from .vision import find_symbols

from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)


app = None


class ClassifyDialog(QDialog):
    def __init__(self, parent):
        super(ClassifyDialog, self).__init__(parent)
        self.candidate = None
        self.candidates = []
        self.candidate_ids = {}  # id -> index in self.candidates

        vbox = QVBoxLayout()
        self.image = image = QLabel()
        self.symbol_buttons = {}
        self.symbol_classes = {}
        class_box = QWidget()
        clay = QVBoxLayout()
        class_box.setLayout(clay)
        for key, folder, label in [
            ("X", "other", "Other"),
            ("A", "white_circle", "White Circle \u25CB"),
            ("B", "white_circle_double", "Double White Circle \u29BE"),
            ("P", "black_dot", "Black Dot ·"),
            ("Q", "black_circle", "Black Circle \u29BF"),
            ("T", "cross_small", "Small Cross ×"),
            ("U", "cross_large", "Big Cross ✛"),
        ]:
            button = QRadioButton(f"{key} {label}")
            button.folder = os.path.join("corpus", folder)
            os.makedirs(button.folder, exist_ok=True)
            clay.addWidget(button)
            button.toggled.connect(self._on_radio_toggle)
            self.symbol_buttons[key] = button

        content_box = QWidget()
        content_layout = QHBoxLayout()
        content_box.setLayout(content_layout)
        content_layout.addWidget(image)
        content_layout.addWidget(class_box, alignment=Qt.AlignmentFlag.AlignTop)

        navrow = QWidget()
        self.prev_button = prev = QPushButton("Previous", parent=navrow)
        self.prev_button.setEnabled(False)
        self.next_button = next = QPushButton("Next", parent=navrow)
        self.next_button.setEnabled(False)
        self.next_button.clicked.connect(self._on_next)
        self.prev_button.clicked.connect(self._on_prev)

        lay = QHBoxLayout()
        lay.addWidget(prev)
        lay.addWidget(next)
        navrow.setLayout(lay)

        vbox.addWidget(content_box)
        vbox.addWidget(navrow, alignment=Qt.AlignmentFlag.AlignRight)
        self.setLayout(vbox)

    def _on_next(self):
        self.save_to_corpus()
        id = self.candidate_ids[self.candidate]
        if id + 1 < len(self.candidates):
            self.set_candidate(self.candidates[id + 1][0])

    def _on_prev(self):
        self.save_to_corpus()
        idx = self._candidate_index()
        if idx - 1 >= 0:
            self.set_candidate(self.candidates[idx - 1][0])

    def _candidate_index(self):
        return self.candidate_ids[self.candidate]

    def _on_radio_toggle(self):
        any_checked = any(b.isChecked() for b in self.symbol_buttons.values())
        if any_checked:
            self.save_to_corpus()

    def save_to_corpus(self):
        if self.candidate is None:
            return
        candidate_index = self.candidate_ids[self.candidate]
        _, png = self.candidates[candidate_index]
        for key, button in self.symbol_buttons.items():
            filepath = os.path.join(button.folder, self.candidate + ".png")
            if button.isChecked():
                with open(filepath, "wb") as png_file:
                    png_file.write(png)
            else:
                try:
                    os.remove(filepath)
                except FileNotFoundError:
                    pass

    def keyPressEvent(self, event):
        if type(event) != QKeyEvent:
            return super().keyPressEvent(event)
        key = event.text().upper()
        if key not in self.symbol_buttons:
            return super().keyPressEvent(event)
        for bkey, b in self.symbol_buttons.items():
            b.setChecked(key == bkey)

    def add_candidate(self, id, image):
        self.candidate_ids[id] = len(self.candidates)
        self.candidates.append((id, image))

    def set_candidate(self, id):
        assert type(id) == str, id
        if self.candidate == id:
            return
        self.candidate = id
        pixmap = QPixmap(256, 256)
        if id is not None:
            _, png = self.candidates[self.candidate_ids[id]]
            pixmap.loadFromData(png, format="png")
        else:
            pixmap.fill(QColor(255, 255, 255))
        p = QPainter(pixmap)
        p.setPen(QPen(QColor(0x44, 0x44, 0xFF, 0xCC), 3))
        w = 32
        width, height = pixmap.width(), pixmap.height()
        cx, cy = int(width / 2), int(height / 2)
        p.drawLine(cx, cy - w, cx, cy + w)
        p.drawLine(cx - w, cy, cx + w, cy)
        p.end()
        pixmap.setDevicePixelRatio(2.0)
        self.image.setPixmap(pixmap)
        for button in self.symbol_buttons.values():
            button.setChecked(False)
        idx = self._candidate_index()
        self.next_button.setEnabled(idx + 1 < len(self.candidates))
        self.next_button.setDefault(idx + 1 < len(self.candidates))
        self.prev_button.setEnabled(idx > 0)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    dialog = QFileDialog()
    dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
    dialog.setNameFilter("PDFs (*.pdf)")
    if not dialog.exec():
        sys.exit(0)

    classify_dialog = ClassifyDialog(parent=None)
    for f in dialog.selectedFiles():
        for id, img in find_symbols(f):
            classify_dialog.add_candidate(id, img)
    classify_dialog.set_candidate(classify_dialog.candidates[0][0])
    classify_dialog.show()

    sys.exit(app.exec())

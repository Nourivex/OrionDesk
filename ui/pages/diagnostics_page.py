from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QStyle, QTextBrowser, QVBoxLayout, QWidget

from ui.theme_tokens import ThemeTokens


class DiagnosticsPage(QWidget):
    generateReportRequested = Signal()
    performanceBaselineRequested = Signal()
    saveSnapshotRequested = Signal()

    def __init__(self, theme: ThemeTokens, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            theme.spacing_md,
            theme.spacing_md,
            theme.spacing_md,
            theme.spacing_md,
        )
        title = QLabel("Diagnostics", self)
        title.setObjectName("placeholderTitle")

        button_row = QHBoxLayout()
        self.generate_button = QPushButton("Generate Report", self)
        self.generate_button.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView)
        )
        self.generate_button.clicked.connect(self.generateReportRequested.emit)

        self.baseline_button = QPushButton("Run Performance Baseline", self)
        self.baseline_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        self.baseline_button.clicked.connect(self.performanceBaselineRequested.emit)

        self.snapshot_button = QPushButton("Save Recovery Snapshot", self)
        self.snapshot_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
        self.snapshot_button.clicked.connect(self.saveSnapshotRequested.emit)

        button_row.addWidget(self.generate_button)
        button_row.addWidget(self.baseline_button)
        button_row.addWidget(self.snapshot_button)
        button_row.addStretch()

        self.diagnostics_info = QTextBrowser(self)
        self.diagnostics_info.setObjectName("diagnosticsInfo")
        layout.addWidget(title)
        layout.addLayout(button_row)
        layout.addWidget(self.diagnostics_info)

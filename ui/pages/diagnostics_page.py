from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QStyle, QTextBrowser, QVBoxLayout, QWidget

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

        summary_card = QFrame(self)
        summary_card.setObjectName("topCard")
        summary_layout = QGridLayout(summary_card)
        summary_layout.setContentsMargins(theme.spacing_md, theme.spacing_md, theme.spacing_md, theme.spacing_md)
        summary_layout.setHorizontalSpacing(theme.spacing_md)
        summary_layout.setVerticalSpacing(theme.spacing_sm)

        health_title = QLabel("Runtime Health", summary_card)
        health_title.setObjectName("sectionHint")
        self.health_state_label = QLabel("Online", summary_card)
        self.health_state_label.setObjectName("sectionTitle")

        release_title = QLabel("Release Checklist", summary_card)
        release_title.setObjectName("sectionHint")
        self.release_checklist_label = QLabel("-", summary_card)
        self.release_checklist_label.setObjectName("sectionTitle")

        profile_title = QLabel("Execution Profile", summary_card)
        profile_title.setObjectName("sectionHint")
        self.profile_state_label = QLabel("-", summary_card)
        self.profile_state_label.setObjectName("sectionTitle")

        summary_layout.addWidget(health_title, 0, 0)
        summary_layout.addWidget(release_title, 0, 1)
        summary_layout.addWidget(profile_title, 0, 2)
        summary_layout.addWidget(self.health_state_label, 1, 0)
        summary_layout.addWidget(self.release_checklist_label, 1, 1)
        summary_layout.addWidget(self.profile_state_label, 1, 2)

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
        layout.addWidget(summary_card)
        layout.addLayout(button_row)
        layout.addWidget(self.diagnostics_info)

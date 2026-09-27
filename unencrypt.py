from __future__ import annotations

import sys
from pathlib import Path
from typing import List

from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt
from pypdf import PdfReader, PdfWriter


def decrypt_pdf_file(input_pdf_path: str, password: str, output_dir: str | None = None) -> str:
    input_path = Path(input_pdf_path)
    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_pdf_path}")

    reader = PdfReader(str(input_path))
    if not reader.is_encrypted:
        raise ValueError(f"{input_path.name} is not encrypted and does not need decryption.")

    decrypted = reader.decrypt(password)
    if decrypted == 0:
        raise ValueError(f"Incorrect password for: {input_path.name}")

    target_dir = Path(output_dir) if output_dir else input_path.parent
    target_dir.mkdir(parents=True, exist_ok=True)

    output_path = target_dir / f"{input_path.stem}_unencrypted.pdf"
    if output_path.exists():
        count = 1
        while True:
            candidate = target_dir / f"{input_path.stem}_unencrypted_{count}.pdf"
            if not candidate.exists():
                output_path = candidate
                break
            count += 1

    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    with open(output_path, "wb") as file:
        writer.write(file)

    return str(output_path)


class BatchDecryptWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Batch PDF Unencrypt")
        self.resize(720, 500)

        self.selected_files: List[str] = []

        main_layout = QVBoxLayout(self)

        file_group = QGroupBox("1. Select PDF files")
        file_layout = QVBoxLayout(file_group)

        row = QHBoxLayout()
        self.select_button = QPushButton("Select PDFs")
        self.select_button.clicked.connect(self.select_files)
        self.remove_button = QPushButton("Remove selected")
        self.remove_button.clicked.connect(self.remove_selected_files)
        row.addWidget(self.select_button)
        row.addWidget(self.remove_button)
        file_layout.addLayout(row)

        self.file_list = QListWidget()
        self.file_list.setSelectionMode(self.file_list.SelectionMode.MultiSelection)
        file_layout.addWidget(self.file_list)

        settings_group = QGroupBox("2. Password and output")
        settings_layout = QFormLayout(settings_group)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Known PDF password")
        self.password_input.setEchoMode(QLineEdit.Password)
        settings_layout.addRow("Password:", self.password_input)

        output_row = QHBoxLayout()
        self.output_dir_input = QLineEdit()
        self.output_dir_input.setPlaceholderText("Output folder (optional)")
        self.output_dir_input.setReadOnly(True)
        self.output_dir_button = QPushButton("Choose folder")
        self.output_dir_button.clicked.connect(self.choose_output_dir)
        output_row.addWidget(self.output_dir_input)
        output_row.addWidget(self.output_dir_button)
        settings_layout.addRow("Output folder:", output_row)

        main_layout.addWidget(file_group)
        main_layout.addWidget(settings_group)

        self.process_button = QPushButton("Unencrypt selected PDFs")
        self.process_button.clicked.connect(self.process_files)
        main_layout.addWidget(self.process_button)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("Processing log will appear here...")
        main_layout.addWidget(self.log_output)

    def select_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select PDF files",
            "",
            "PDF Files (*.pdf)",
        )
        if not paths:
            return

        for path in paths:
            if path not in self.selected_files:
                self.selected_files.append(path)
                self.file_list.addItem(QListWidgetItem(path))

        if self.selected_files and not self.output_dir_input.text().strip():
            self.output_dir_input.setText(str(Path(self.selected_files[0]).parent))

    def choose_output_dir(self):
        folder = QFileDialog.getExistingDirectory(self, "Choose output folder")
        if folder:
            self.output_dir_input.setText(folder)

    def remove_selected_files(self):
        selected_rows = self.file_list.selectedItems()
        if not selected_rows:
            QMessageBox.information(self, "No files selected", "Select one or more uploaded PDFs to remove.")
            return

        for item in selected_rows:
            path = item.text()
            if path in self.selected_files:
                self.selected_files.remove(path)
            row = self.file_list.row(item)
            self.file_list.takeItem(row)

        if not self.selected_files:
            self.output_dir_input.clear()

    def process_files(self):
        password = self.password_input.text().strip()
        if not password:
            QMessageBox.warning(self, "Missing password", "Please enter the known PDF password.")
            return

        if not self.selected_files:
            QMessageBox.warning(self, "No PDF selected", "Please choose at least one PDF file first.")
            return

        output_dir = self.output_dir_input.text().strip() or str(Path(self.selected_files[0]).parent)
        self.log_output.clear()
        self.log_output.append("Starting batch unencryption...\n")

        success_count = 0
        failed_count = 0

        for pdf_path in list(self.selected_files):
            try:
                output_path = decrypt_pdf_file(pdf_path, password, output_dir)
                self.log_output.append(f"OK: {pdf_path} -> {output_path}")
                success_count += 1
            except Exception as exc:
                self.log_output.append(f"FAILED: {pdf_path} -> {exc}")
                failed_count += 1

        self.log_output.append(f"\nCompleted: {success_count} success, {failed_count} failed.")
        QMessageBox.information(
            self,
            "Batch unencryption complete",
            f"Successfully unencrypted {success_count} file(s).\nFailed: {failed_count}.",
        )


def main():
    app = QApplication(sys.argv)
    window = BatchDecryptWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
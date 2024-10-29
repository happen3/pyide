import os
import re
import sys
import traceback
from tkinter import messagebox, filedialog

from PyQt5 import QtCore
from PyQt5.QtCore import QFileSelector
from PyQt5.QtGui import QTextCharFormat, QSyntaxHighlighter, QColor
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QTextEdit, QMainWindow, QAction, QFileDialog, \
    QErrorMessage, QMessageBox


# Create a custom QWidget class
def load_stylesheet(filename):
    with open(filename, 'r') as f:
        return f.read()

class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)

        # Define the format for different types of syntax
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor("orange"))

        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("gray"))

        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("red"))

        self.function_form = QTextCharFormat()
        self.function_form.setForeground(QColor("green"))

        self.obj_name = QTextCharFormat()
        self.obj_name.setForeground(QColor(115, 117, 255))

        self.sp = QTextCharFormat()
        self.sp.setForeground(QColor("purple"))

        self.num = QTextCharFormat()
        self.num.setForeground(QColor("cyan"))

        self.highlighting_rules = [
            (r'\b(?:def|pass|class|if|else|elif|for|del|while|return|import|from|as|with|try|except|finally|raise|in|is|lambda)\b', self.keyword_format),
            (r'#.*', self.comment_format),
            (r'\b(?:print|type|isinstance|set)\b', self.function_form),
            (r'\b\d+(\.\d+)?\b', self.num),
            (r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)', self.obj_name),
            (r'class\s+([^\s(]+)', self.obj_name),
            (r'\b(?:self|__init__|super|__get__|__set__|__getattr__|__setattr__|__call__|__dict__|__str__|__repr__|__name__)\b', self.sp),
            (r"(?<!\\)'(?:[^\n']|\\')*(?<!\\)'|(?<!\\)\"(?:[^\n\"]|\\\")*(?<!\\)\"", self.string_format),
        ]
    def highlightBlock(self, text):
        for pattern, fmt in self.highlighting_rules:
            for match in re.finditer(pattern, text):
                if pattern == r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)' or pattern == r'class\s+([^\s(]+)':
                    start, end = match.span(1)
                else:
                    start, end = match.span()
                self.setFormat(start, end - start, fmt)

class CodeBox(QTextEdit):
    def keyPressEvent(self, event):
        """Override keyPressEvent to replace tab with spaces."""
        if event.key() == QtCore.Qt.Key_Tab:
            # Insert four spaces instead of a tab character
            self.insertPlainText('    ')  # Insert four spaces
            return  # Prevent the default tab action
        elif event.key() == QtCore.Qt.Key_Return:
            if self.toPlainText().strip().endswith(':'):
                self.insertPlainText('\n    ')
            else:
                super().keyPressEvent(event)
        else:
            # Call the base class implementation for other key events
            super().keyPressEvent(event)

class MyMainWindow(QMainWindow):
    def saveas(self):
        # Open the save file dialog
        file_path, _ = QFileDialog.getSaveFileName(None, "Save File", "", "Python files (*.py *pyw *.pyi);;All files (*)")
        if file_path:  # Check if a file path was selected
            try:
                # Open the selected file and write the content of the QTextEdit
                with open(file_path, 'w') as f:
                    f.write(self.code_box.toPlainText())  # Save the text from the QTextEdit
            except Exception as e:
                QMessageBox.critical(None, "Error", "Could not save the file.")
    def save(self):
        # Open the save file dialog
        file_path = self.full_path if self.full_path else True
        if file_path: return self.saveas()
        if file_path:  # Check if a file path was selected
            try:
                # Open the selected file and write the content of the QTextEdit
                with open(file_path, 'w') as f:
                    f.write(self.code_box.toPlainText())  # Save the text from the QTextEdit
            except Exception as e:
                QMessageBox.critical(None, "Error", "Could not save the file.")
    def open(self):
        # Open the save file dialog
        file_path, _ = QFileDialog.getOpenFileName(None, "Open File", "", "Python files (*.py *pyw *.pyi);;All files (*)")
        if file_path:  # Check if a file path was selected
            try:
                # Open the selected file and write the content of the QTextEdit
                with open(file_path, 'r') as f:
                    self.code_box.setPlainText(f.read())  # Save the text from the QTextEdit
                    self.file_set(os.path.split(file_path)[-1])
            except Exception as e:
                QMessageBox.critical(None, "Error", "Could not open the file.")
    def file_set(self, file_name, full_path=None):
        self.current_file = file_name
        self.full_path = full_path
        self.setWindowTitle(f"Pyide - {file_name}")
    def new(self):
        self.code_box.clear()
        self.file_set("Untitled")
    def __init__(self):
        super().__init__()

        # Set up the main window
        self.full_path = None
        self.setWindowTitle("Pyide")
        self.setGeometry(100, 100, 600, 400)
        self.current_file = "Untitled"
        self.file_set(self.current_file)

        # Create a central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Create a vertical layout
        layout = QVBoxLayout()

        # Create a multi-line text box (QTextEdit)
        self.code_box = CodeBox(self)
        self.highlighter = PythonHighlighter(self.code_box.document())
        self.code_box.setPlaceholderText("Enter your text here...")
        self.code_box.setStyleSheet(load_stylesheet("res/CodeBox_Theme.css"))

        # Add the text box to the layout
        layout.addWidget(self.code_box)

        # Set the layout for the central widget
        self.central_widget.setLayout(layout)

        # Create a menu bar
        self.create_menu_bar()

    def create_menu_bar(self):
        # Create the menu bar
        menu_bar = self.menuBar()

        # Create a File menu
        file_menu = menu_bar.addMenu("File")

        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new)
        file_menu.addAction(new_action)

        # Create an action for opening a file
        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open)
        file_menu.addAction(open_action)

        # Create an action for saving a file
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save)
        file_menu.addAction(save_action)

        # Create an action for saving a file as
        saveas_action = QAction("Save As", self)
        saveas_action.setShortcut("Shift+Ctrl+S")
        saveas_action.triggered.connect(self.saveas)
        file_menu.addAction(saveas_action)

        # Create an action for exiting the application
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)


def handle_exception(exc_type, exc_value, exc_traceback):
    """Handle unhandled exceptions globally."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.exit(0)
    if exc_traceback is not None:
        print("Unhandled exception:", file=sys.stderr)
        traceback.print_exception(exc_type, exc_value, exc_traceback)

        # Optionally show the error in a message box
        message = f"{exc_value}"
        print(message, file=sys.stderr)

# Main execution
def create():
    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec_())

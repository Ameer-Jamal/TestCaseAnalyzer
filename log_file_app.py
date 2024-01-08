import sys

from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QVBoxLayout, QWidget, QListWidget, QFileDialog, \
    QMessageBox, QDialog, QDialogButtonBox, QLineEdit, QCheckBox, QLabel, QGridLayout
from PyQt5.Qsci import QsciScintilla, QsciLexerPython
import os
import mmap
import tempfile
import utilities as utils
import ruamel.yaml
from log_analysis import LogAnalysis


class LogFileApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Log File Analyzer")
        self.setGeometry(300, 300, 1000, 800)

        # Main layout
        layout = QVBoxLayout()

        # Directory selection button
        self.select_dir_button = QPushButton("Select Log Directory")
        self.select_dir_button.clicked.connect(self.select_directory)
        layout.addWidget(self.select_dir_button)

        # Listbox for displaying log files
        self.log_files_listbox = QListWidget()
        layout.addWidget(self.log_files_listbox)

        # Process button
        self.process_button = QPushButton("Process Selected File")
        self.process_button.clicked.connect(self.process_file)
        layout.addWidget(self.process_button)

        # Open in VS Code button
        self.open_vscode_button = QPushButton("Open in VS Code")
        self.open_vscode_button.clicked.connect(self.open_in_vscode)
        layout.addWidget(self.open_vscode_button)

        # Edit Configurations button
        self.edit_configs_button = QPushButton("Edit Configurations")
        self.edit_configs_button.clicked.connect(self.edit_yaml_configs)
        layout.addWidget(self.edit_configs_button)

        # QScintilla editor for output
        self.output_text = QsciScintilla()
        self.lexer = QsciLexerPython()  # Set lexer for Python syntax, change as needed
        self.output_text.setLexer(self.lexer)
        layout.addWidget(self.output_text)

        # Set the layout to the central widget
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.config = None
        self.log_directory = None
        self.use_temp_file = None
        self.report_directory = None
        self.temp_file_path = None
        self.files = []

    def select_directory(self):
        self.log_directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if self.log_directory:
            self.populate_files_listbox()

    def process_file(self):
        selected_item = self.log_files_listbox.currentItem()
        if not selected_item:
            QMessageBox.information(self, "Information", "Please select a file.")
            return

        choice = self.log_files_listbox.row(selected_item)
        mm = self.read_latest_log_from_directory(choice)
        if mm:
            if self.use_temp_file:
                # Create a temporary file
                with tempfile.NamedTemporaryFile(mode='w+', suffix=".txt", delete=False) as temp_file:
                    self.temp_file_path = temp_file.name
            else:
                # Create a unique file in the specified temp_directory
                if not os.path.exists(self.report_directory):
                    os.makedirs(self.report_directory)
                self.temp_file_path = utils.create_unique_filename(self.report_directory)

            # Extract failed test cases and write them to the file
            LogAnalysis.extract_failed_test_cases(mm, self.temp_file_path)
            mm.close()
            self.display_file_content(self.temp_file_path)

    def populate_files_listbox(self):
        self.log_files_listbox.clear()
        self.files = LogAnalysis.get_files_from_dir(self.log_directory)
        for filename in self.files:
            self.log_files_listbox.addItem(filename)

    def display_file_content(self, file_path):
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            self.output_text.setText(content)  # Set the content in QsciScintilla widget
        except Exception as e:
            self.show_alert(f"Error reading file: {e}")

    def open_in_vscode(self):
        if hasattr(self, 'temp_file_path') and self.temp_file_path:
            os.system(f"code \"{self.temp_file_path}\"")
        else:
            self.show_alert("No file to open in VS Code.")

    def read_latest_log_from_directory(self, choice):
        try:
            filename = os.path.join(self.log_directory, self.files[choice])
            with open(filename, 'r') as f:
                mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            return mm
        except Exception as e:
            self.show_alert(f"An error occurred: {e}")
            return None

    def populate_files_listbox(self):
        self.log_files_listbox.clear()
        self.files = LogAnalysis.get_files_from_dir(self.log_directory, True)
        for filename in self.files:
            self.log_files_listbox.addItem(filename)

    @staticmethod
    def show_alert(message):
        """Show an alert message box."""
        QMessageBox.information(None, "Alert", message)

    def set_configuration(self, config):
        self.config = config
        self.log_directory = self.config.get('log_location', {}).get('where_are_your_logs_located', '')
        self.use_temp_file = self.config.get('file_handling', {}).get('use_temp_file', True)
        self.report_directory = self.config.get('file_handling', {}).get('report_directory', '')

        # Check if a log directory is specified and populate the listbox
        if self.log_directory:
            self.populate_files_listbox()


    def edit_yaml_configs(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Configurations")
        dialog.resize(400, 200)  # Adjust the size of the dialog

        layout = QVBoxLayout(dialog)
        grid_layout = QGridLayout()

        # Create widgets for editing configuration
        self.log_location_edit = QLineEdit()
        self.log_location_edit.setFixedWidth(300)  # Adjust the width
        self.use_temp_file_checkbox = QCheckBox()
        self.report_directory_edit = QLineEdit()
        self.report_directory_edit.setFixedWidth(300)  # Adjust the width

        # Load current configuration into the widgets
        self.load_yaml_config_to_widgets()

        # Add widgets to grid layout
        grid_layout.addWidget(QLabel("Log Location:"), 0, 0)
        grid_layout.addWidget(self.log_location_edit, 0, 1)
        grid_layout.addWidget(QLabel("Use Temporary Files?:"), 1, 0)
        grid_layout.addWidget(self.use_temp_file_checkbox, 1, 1)
        grid_layout.addWidget(QLabel("Report Directory:"), 2, 0)
        grid_layout.addWidget(self.report_directory_edit, 2, 1)

        # Add grid layout to main layout
        layout.addLayout(grid_layout)

        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save_yaml_config_from_widgets)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)
        dialog.exec_()
    def get_config_path(self):
        # Construct the full path to the config.yaml file
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.yaml')


    def load_yaml_config_to_widgets(self):
        config_path = self.get_config_path()
        if os.path.exists(config_path):
            with open(config_path, 'r') as file:
                yaml = ruamel.yaml.YAML()
                config = yaml.load(file)
            self.log_location_edit.setText(config.get('log_location', {}).get('where_are_your_logs_located', ''))
            self.use_temp_file_checkbox.setChecked(config.get('file_handling', {}).get('use_temp_file', False))
            self.report_directory_edit.setText(config.get('file_handling', {}).get('report_directory', ''))

    def save_yaml_config_from_widgets(self):
        config_path = self.get_config_path()
        with open(config_path, 'r') as file:
            yaml = ruamel.yaml.YAML()
            config = yaml.load(file)

        # Update only the specific keys
        config['log_location']['where_are_your_logs_located'] = self.log_location_edit.text()
        config['file_handling']['use_temp_file'] = self.use_temp_file_checkbox.isChecked()
        config['file_handling']['report_directory'] = self.report_directory_edit.text()

        # Write back the entire configuration
        with open(config_path, 'w') as file:
            yaml.dump(config, file)

        QMessageBox.information(self, "Success", "Configuration saved successfully.")


def main():
    app = QApplication(sys.argv)
    main_window = LogFileApp()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

import sys

from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QListWidget, \
    QFileDialog, \
    QMessageBox, QDialog, QDialogButtonBox, QLineEdit, QCheckBox, QLabel, QGridLayout, QSplitter
from PyQt5.Qsci import QsciScintilla
import os
import consts
import mmap
import tempfile
import utilities as utils
import ruamel.yaml
from log_analysis import LogAnalysis
from custom_log_lexer import CustomLogLexer


class LogFileApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(consts.WINDOW_TITLE)
        self.setGeometry(300, 300, 1000, 800)
        self.default_font_size = 14  # Default value if not set in config

        # Load stylesheet
        stylesheet = self.load_stylesheet("styles.css")

        # Main layout
        main_layout = QVBoxLayout()

        # Create horizontal layout for log files list and output editor
        splitter = QSplitter()

        # Listbox for displaying log files
        self.log_files_listbox = QListWidget()
        self.log_files_listbox.itemDoubleClicked.connect(self.process_file)  # Add double-click event
        splitter.addWidget(self.log_files_listbox)

        # QScintilla editor for output
        self.output_text = QsciScintilla()
        self.lexer = CustomLogLexer(self.output_text)  # Use custom lexer for log text
        self.output_text.setLexer(self.lexer)
        self.output_text.setWrapMode(QsciScintilla.SC_WRAP_WORD)  # Enable text wrapping
        splitter.addWidget(self.output_text)

        # Add the splitter to the main layout
        main_layout.addWidget(splitter)

        # Create a horizontal layout for buttons
        button_layout = QHBoxLayout()

        # Increase Font Size button
        self.increase_font_button = QPushButton(consts.INCREASE_FONT_SIZE)
        self.increase_font_button.clicked.connect(self.increase_font_size)
        self.increase_font_button.setStyleSheet(stylesheet)
        button_layout.addWidget(self.increase_font_button)

        # Decrease Font Size button
        self.decrease_font_button = QPushButton(consts.DECREASE_FONT_SIZE)
        self.decrease_font_button.clicked.connect(self.decrease_font_size)
        self.decrease_font_button.setStyleSheet(stylesheet)
        button_layout.addWidget(self.decrease_font_button)

        # Reload Files button
        self.reload_button = QPushButton(consts.RELOAD_FILES_MESSAGE)
        self.reload_button.clicked.connect(self.reload_files)
        self.reload_button.setStyleSheet(stylesheet)
        button_layout.addWidget(self.reload_button)

        # Process button
        self.process_button = QPushButton(consts.PROCESS_SELECTED_FILE_MESSAGE)
        self.process_button.clicked.connect(self.process_file)
        self.process_button.setStyleSheet(stylesheet)
        button_layout.addWidget(self.process_button)

        # Open in VS Code button
        self.open_vscode_button = QPushButton(consts.OPEN_IN_VS_CODE_MESSAGE)
        self.open_vscode_button.clicked.connect(self.open_in_vscode)
        self.open_vscode_button.setStyleSheet(stylesheet)
        button_layout.addWidget(self.open_vscode_button)

        # Edit Configurations button
        self.edit_configs_button = QPushButton(consts.EDIT_CONFIGURATIONS_MESSAGE)
        self.edit_configs_button.clicked.connect(self.edit_yaml_configs)
        self.edit_configs_button.setStyleSheet(stylesheet)
        button_layout.addWidget(self.edit_configs_button)

        # Add the button layout to the main layout
        main_layout.addLayout(button_layout)

        # Set the layout to the central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.config = None
        self.log_directory = None
        self.use_temp_file = None
        self.report_directory = None
        self.temp_file_path = None
        self.default_font_size = None
        self.files = []

    @staticmethod
    def load_stylesheet(filename):
        with open(filename, "r") as file:
            return file.read()

    def increase_font_size(self):
        self.default_font_size += 1
        self.update_font_size_in_styles(self.default_font_size, self.output_text.font().family())

    def decrease_font_size(self):
        if self.default_font_size > 1:  # Prevent font size from being too small
            self.default_font_size -= 1
            self.update_font_size_in_styles(self.default_font_size, self.output_text.font().family())

    def update_font_size_in_styles(self, size, font_family):
        for style in range(128):  # Scintilla supports up to 128 styles
            self.output_text.SendScintilla(self.output_text.SCI_STYLESETSIZE, style, size)
            self.output_text.SendScintilla(self.output_text.SCI_STYLESETFONT, style, font_family.encode('utf-8'))

    def select_directory(self):
        self.log_directory = QFileDialog.getExistingDirectory(self, consts.SELECT_LOG_DIRECTORY)
        if self.log_directory:
            self.populate_files_listbox()

    def reload_files(self):
        if self.log_directory:
            self.populate_files_listbox()

    def process_file(self):
        selected_item = self.log_files_listbox.currentItem()
        if not selected_item:
            QMessageBox.information(self, consts.INFORMATION_MESSAGE, consts.PLEASE_SELECT_A_FILE_MESSAGE)
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

    def display_file_content(self, file_path):
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            self.output_text.setText(content)  # Set the content in QsciScintilla widget
        except Exception as e:
            self.show_alert(consts.ERROR_READING_FILE_MESSAGE.format(e))

    def open_in_vscode(self):
        if hasattr(self, 'temp_file_path') and self.temp_file_path:
            os.system(f"code \"{self.temp_file_path}\"")
        else:
            self.show_alert(consts.NO_FILE_TO_OPEN_MESSAGE)

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
        self.log_files_listbox.clear()  # Clear the listbox
        if self.log_directory:
            self.files = LogAnalysis.get_files_from_dir(self.log_directory, True)
            for filename in self.files:
                if filename not in consts.MACOS_SYSTEM_FILES:  # Skip macOS system files
                    self.log_files_listbox.addItem(filename)

    @staticmethod
    def show_alert(message):
        """Show an alert message box."""
        QMessageBox.information(None, consts.ALERT_MESSAGE, message)

    def set_initial_font_size(self):
        font = self.output_text.font()
        font.setPointSize(self.default_font_size)
        self.output_text.setFont(font)
        self.update_font_size_in_styles(self.default_font_size, font.family())

    def set_configuration(self, config):
        self.config = config
        self.log_directory = self.config.get('log_location', {}).get('where_are_your_logs_located', '')
        self.use_temp_file = self.config.get('file_handling', {}).get('use_temp_file', True)
        self.report_directory = self.config.get('file_handling', {}).get('report_directory', '')
        self.default_font_size = self.config.get('ui_settings', {}).get('default_font_size', 16)

        # Check if a log directory is specified and populate the listbox
        if self.log_directory:
            self.populate_files_listbox()

        # Set the initial font size
        self.set_initial_font_size()

    def edit_yaml_configs(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(consts.EDIT_CONFIGURATIONS_DIALOG_TITLE)
        dialog.resize(400, 200)  # Adjust the size of the dialog

        layout = QVBoxLayout(dialog)
        grid_layout = QGridLayout()

        # Create widgets for editing configuration
        self.log_location_edit = QLineEdit()
        self.log_location_edit.setFixedWidth(300)  # Adjust the width
        self.use_temp_file_checkbox = QCheckBox()
        self.report_directory_edit = QLineEdit()
        self.report_directory_edit.setFixedWidth(300)  # Adjust the width
        self.default_font_size_edit = QLineEdit()
        self.default_font_size_edit.setFixedWidth(100)  # Adjust the width

        # Directory selection button
        self.select_dir_button = QPushButton(consts.SELECT_LOG_DIRECTORY)
        self.select_dir_button.clicked.connect(self.select_directory)
        stylesheet = self.load_stylesheet("styles.css")
        self.select_dir_button.setStyleSheet(stylesheet)
        layout.addWidget(self.select_dir_button)

        # Load current configuration into the widgets
        self.load_yaml_config_to_widgets()

        # Add widgets to grid layout
        grid_layout.addWidget(QLabel(consts.LOG_LOCATION_LABEL), 0, 0)
        grid_layout.addWidget(self.log_location_edit, 0, 1)
        grid_layout.addWidget(QLabel(consts.USE_TEMPORARY_FILES_LABEL), 1, 0)
        grid_layout.addWidget(self.use_temp_file_checkbox, 1, 1)
        grid_layout.addWidget(QLabel(consts.REPORT_DIRECTORY_LABEL), 2, 0)
        grid_layout.addWidget(self.report_directory_edit, 2, 1)
        grid_layout.addWidget(QLabel("Default Font Size:"), 3, 0)
        grid_layout.addWidget(self.default_font_size_edit, 3, 1)

        # Add grid layout to main layout
        layout.addLayout(grid_layout)

        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save_yaml_config_from_widgets)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)
        dialog.exec_()

    @staticmethod
    def get_config_path():
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
            self.default_font_size_edit.setText(str(config.get('ui_settings', {}).get('default_font_size', 14)))

    def save_yaml_config_from_widgets(self):
        config_path = self.get_config_path()
        with open(config_path, 'r') as file:
            yaml = ruamel.yaml.YAML()
            config = yaml.load(file)

        # Update only the specific keys
        config['log_location']['where_are_your_logs_located'] = self.log_location_edit.text()
        config['file_handling']['use_temp_file'] = self.use_temp_file_checkbox.isChecked()
        config['file_handling']['report_directory'] = self.report_directory_edit.text()
        config['ui_settings']['default_font_size'] = int(self.default_font_size_edit.text())

        # Write back the entire configuration
        with open(config_path, 'w') as file:
            yaml.dump(config, file)

        # Update the current font size
        self.default_font_size = int(self.default_font_size_edit.text())
        self.set_initial_font_size()

        QMessageBox.information(self, consts.SUCCESS_MESSAGE, consts.CONFIGURATION_SAVED_MESSAGE)


def main():
    app = QApplication(sys.argv)
    main_window = LogFileApp()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

# consts.py

# Regular expressions used in the log analysis
FAILED_PATTERN = rb'\((\d+) FAILED\)'
REASON_PATTERN = rb'(.*?FAILED)'
END_OF_REASON_PATTERN = rb'HeadlessChrome \d+\.\d+\.\d'

# Messages and strings
FAILED_MESSAGE = " FAILED:"
TAB_INDENT = "\t"
NO_ERRORS_MESSAGE = "No errors found."

# List of known macOS system files to skip
MACOS_SYSTEM_FILES = [
    '.DS_Store',
    '._.DS_Store',
    '.localized',
    '.Spotlight-V100',
    '.Trashes',
    'Icon\r'
]

# Strings used in the LogFileApp class
WINDOW_TITLE = "Log File Analyzer"
SELECT_LOG_DIRECTORY = "Select Log Directory"
RELOAD_FILES_MESSAGE = "Reload Files ↻"
PROCESS_SELECTED_FILE_MESSAGE = "Process Selected File"
OPEN_IN_VS_CODE_MESSAGE = "Open in VS Code"
EDIT_CONFIGURATIONS_MESSAGE = "Edit Configurations ⚙️"
ERROR_READING_FILE_MESSAGE = "Error reading file: {}"
NO_FILE_TO_OPEN_MESSAGE = "No file to open in VS Code."
INFORMATION_MESSAGE = "Information"
PLEASE_SELECT_A_FILE_MESSAGE = "Please select a file."
ALERT_MESSAGE = "Alert"
SUCCESS_MESSAGE = "Success"
CONFIGURATION_SAVED_MESSAGE = "Configuration saved successfully. ✅"
EDIT_CONFIGURATIONS_DIALOG_TITLE = "Edit Configurations"
LOG_LOCATION_LABEL = "Log Location:"
USE_TEMPORARY_FILES_LABEL = "Use Temporary Files?:"
REPORT_DIRECTORY_LABEL = "Report Directory:"
INCREASE_FONT_SIZE = "Font Size +"
DECREASE_FONT_SIZE = "DECREASE Size -"

# Strings used in the read_latest_log_from_directory function
AN_ERROR_OCCURRED_MESSAGE = "An error occurred: {}"
LATEST_LOG_FILE_PROMPT = "Select Directory"
CHOOSE_FILE_NUMBER_PROMPT = "Please choose a file by number"
REFRESH_OPTION = "r"

# Lexer
# Styles used in the CustomLogLexer
STYLES = {
    "default": 0,
    "error": 1,
    "trace": 2,
    "cyan": 3,
    "orange": 4,
    "green": 5
}

# Colors used in the CustomLogLexer
COLORS = {
    "default": (255, 255, 255),  # White
    "error": (255, 100, 100),  # Light Red
    "trace": (169, 169, 169),  # Light Gray
    "cyan": (0, 255, 255),  # Cyan
    "orange": (255, 165, 0),  # Orange
    "green": (0, 255, 0)  # Green
}

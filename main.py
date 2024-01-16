# This program extracts failed test cases from log files and writes them to a temporary file
###########################################

import os  # For file and directory operations
import mmap  # For memory-mapped file objects
import tempfile  # For creating temporary files
import utilities as utils  # For utils
import yaml  # For reading config file
import sys
from PyQt5.QtWidgets import QApplication
from log_analysis import LogAnalysis  # Log analysis tools
from log_file_app import LogFileApp


def read_latest_log_from_directory(directory: str):
    """Reads the latest log file from a directory and returns its memory-mapped object."""
    try:
        files = LogAnalysis.get_files_from_dir(directory, False)

        print_files_in_console(files)

        # Ask the user to choose a file by number
        choice = utils.input_file_to_select()
        # If the input is empty, default to the latest log file
        if choice.lower() == 'r':
            utils.insert_console_separator()
            utils.print_refresh_message_in_console()
            utils.insert_console_separator()
            return
        else:
            choice = len(files) if choice == "" else int(choice)

        return return_file_chosen_as_memory_mapped_obj(choice, directory, files)

    except Exception as e:
        # Print the error message and return an empty string
        print(f"An error occurred: {e}")
        return ""


def return_file_chosen_as_memory_mapped_obj(choice, directory, files):
    # Open the chosen file in read mode
    with open(os.path.join(directory, files[choice - 1]), 'r') as f:
        # Create a memory-mapped object from the file
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        # Return the memory-mapped object
        return mm


def print_files_in_console(files):
    """Print the files with their numbers in console"""
    utils.print_files_header_in_console()
    for idx, filename in enumerate(files, 1):
        utils.print_file_name(filename, idx)
        utils.print_white_seperator_in_console()


def main_run_gui_version(gui_config):
    app = QApplication(sys.argv)  # Create a new QApplication instance
    main_window = LogFileApp()    # Instantiate your LogFileApp

    if gui_config:
        main_window.set_configuration(gui_config)
    else:
        main_window.show_alert("Config.yaml not found or values are missing. Please fill in the values in the application.")

    main_window.show()  # Show the main window
    sys.exit(app.exec_())  # Execute the application's main loop


def main_run_cli_version(cli_config):
    # Check for missing configuration values
    log_directory = cli_config.get('log_location', {}).get('where_are_your_logs_located')
    use_temp_file = cli_config.get('file_handling', {}).get('use_temp_file')
    report_directory = cli_config.get('file_handling', {}).get('report_directory')

    if not log_directory or use_temp_file is None or not report_directory:
        print("Config.yaml values are missing. Please fill in the values and try again.")
        exit()

    while True:
        mm = read_latest_log_from_directory(log_directory)
        if mm:
            if use_temp_file:
                # Create a temporary file
                with tempfile.NamedTemporaryFile(mode='w+', suffix=".txt", delete=False) as temp_file:
                    temp_file_path = temp_file.name
            else:
                # Create a unique file in the specified temp_directory
                if not os.path.exists(report_directory):
                    os.makedirs(report_directory)
                temp_file_path = utils.create_unique_filename(report_directory)

            # Extract failed test cases and write them to the file
            LogAnalysis.extract_failed_test_cases(mm, temp_file_path)
            mm.close()

            # Open the file with Visual Studio Code
            os.system(f"code \"{temp_file_path}\"")
            utils.insert_console_separator()


if __name__ == "__main__":
    try:
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        config = None

    # Check for the use_gui_mode setting
    use_gui_mode = config.get('gui_mode', {}).get('use_gui_mode', False)

    if use_gui_mode is None:
        print("Config.yaml use_gui_mode value is missing. Fill in true or false for gui or command line program "
              "interactions.")
        exit()
    elif use_gui_mode:
        main_run_gui_version(config)
    else:
        main_run_cli_version(config)

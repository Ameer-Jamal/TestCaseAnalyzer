# This program extracts failed test cases from log files and writes them to a temporary file
###########################################

# Import the modules needed for the program
import re  # For regular expressions
import os  # For file and directory operations
import mmap  # For memory-mapped file objects
import tempfile  # For creating temporary files
from typing import Dict, List, Set  # For type annotations
import utilities as utils


def read_latest_log_from_directory(directory: str):
    """Reads the latest log file from a directory and returns its memory-mapped object."""
    try:
        files = get_files_from_dir(directory)

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


def get_files_from_dir(directory):
    """Get a list of files in the directory oldest first"""
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    # Sort the files by modification time in ascending order (oldest first)
    files.sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)))
    return files


def extract_failed_test_cases(mm: mmap.mmap, temp_file_path: str):
    """
    Extracts failed test cases from the logs and writes them to a temporary file.
    The keys are the fail counts and the values are lists of reasons.
    """
    # Compile regular expressions for matching failed test cases and reasons
    failed_pattern = get_failed_pattern()
    reason_pattern = get_reason_pattern()
    end_reason_pattern = get_end_of_reason_pattern()

    # Create a set to store the seen fail counts
    seen_fail_counts: Set[int] = set()

    # Open the temporary file in write mode
    with open(temp_file_path, 'w') as temp:
        # Seek to the beginning of the memory-mapped object
        mm.seek(0)
        # Iterate over each line in the memory-mapped object
        for line in iter(mm.readline, b""):
            # Search for a match with the failed pattern
            failed_match = failed_pattern.search(line)
            if failed_match:
                # Get the fail count as an integer
                fail_count = int(failed_match.group(1))

                # If the fail count is not seen before
                if fail_count not in seen_fail_counts:
                    write_failure_found_in_file(temp, mm, fail_count, reason_pattern, end_reason_pattern, )
                    seen_fail_counts.add(fail_count)
        if not seen_fail_counts:
            utils.write_no_errors_message_to_file(temp)

        # Close the memory-mapped object
        mm.close()


def get_end_of_reason_pattern():
    return re.compile(rb'HeadlessChrome \d+\.\d+\.\d')


def get_reason_pattern():
    return re.compile(rb'(.*?FAILED)')


def get_failed_pattern():
    return re.compile(rb'\((\d+) FAILED\)')


def write_failure_found_in_file(file, mm, fail_count, reason_pattern, end_reason_pattern):
    """ Extract the reason lines from the memory-mapped object using a generator expression"""
    reason_lines = extract_reasons(iter(mm.readline, b""), reason_pattern, end_reason_pattern)
    utils.insert_line_separator_in_file(file, True, 2)
    # Write the fail count to the temporary file
    file.write(f"{fail_count} FAILED:\n")
    # Write each reason line to the temporary file with a tab indentation
    for reason in reason_lines:
        file.write(f"\t{reason}\n")
    # Add the fail count to the seen set


def extract_reasons(lines: iter, start_pattern: re.Pattern, end_pattern: re.Pattern) -> List[str]:
    """Extracts reason lines from an iterator of lines using start and end patterns."""
    # Create an empty list to store the reason lines
    reason_lines = []
    # Initialize a flag to indicate whether the start pattern is found or not
    found_start = False

    # Iterate over each line in the iterator
    for line in lines:
        # Decode bytes to string
        line_str = line.decode('utf-8')
        if not found_start:
            # Search for a match with the start pattern at the beginning of the line
            start_match = start_pattern.match(line)
            if start_match:
                # Append the matched group to the reason lines list after decoding bytes to string
                reason_lines.append(start_match.group(1).decode('utf-8'))
                # Set the flag to True
                found_start = True
            continue

        # Search for a match with the end pattern at the beginning of the line
        if end_pattern.match(line):
            break

        # Append the line to the reason lines list
        reason_lines.append(line_str)

        # If the reason lines list has 20 elements, break the loop
        # Remove this if you don't want a limit.
        if len(reason_lines) == 20:
            break

    # Return the reason lines list
    return reason_lines


def write_to_temp_file(results: Dict[int, List[str]]) -> str:
    """Writes the results to a temporary file and returns the file path."""
    # Create a named temporary file in write mode with a .txt suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode='w') as temp:
        # Iterate over the results dictionary items
        for count, reasons in results.items():
            # Write a separator line to the temporary file
            utils.insert_line_separator_in_file(temp, False, 1)
            # Write the fail count to the temporary file
            temp.write(f"{count} FAILED:\n")
            # Write each reason to the temporary file with a tab indentation
            for reason in reasons:
                temp.write(f"\t{reason}\n")
        # Return the temporary file path
        return temp.name


if __name__ == "__main__":
    # Define the directory where the log files are located
    directory = "/Users/ajamal/Documents/Logs/TESTCI_Runs"

    while True:  # Keep running the program

        # Read the latest log file from the directory and get its memory-mapped object
        mm = read_latest_log_from_directory(directory)
        if mm:
            # Create a secure temporary file
            with tempfile.NamedTemporaryFile(mode='w+', suffix=".txt", delete=False) as temp_file:
                temp_file_path = temp_file.name
                # Extract failed test cases from the memory-mapped object and write them to the temporary file
                extract_failed_test_cases(mm, temp_file_path)
                # Close the memory-mapped object
                mm.close()

            # Open the temporary file with Visual Studio Code
            os.system(f"code {temp_file_path}")
            utils.insert_console_separator()

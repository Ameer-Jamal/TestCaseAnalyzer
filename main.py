# This program extracts failed test cases from log files and writes them to a temporary file
###########################################

# Import the modules needed for the program
import re  # For regular expressions
import os  # For file and directory operations
import mmap  # For memory-mapped file objects
import tempfile  # For creating temporary files
from typing import Dict, List, Set  # For type annotations


def read_latest_log_from_directory(directory: str):
    """Reads the latest log file from a directory and returns its memory-mapped object."""
    try:
        # Get a list of files in the directory
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        # Sort the files by modification time in descending order
        files.sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True)

        # Print the files with their numbers
        print("\n \033[42m \033[31m" + "\t" * 6 + "FILES:" + "\t" * 6 + "\033[0m\n")
        for idx, filename in enumerate(files, 1):
            print(f"\033[95m{idx}\033[0m. \033[93m{filename}\033[0m\n")
            print("\033[47m\t" * 13 + "\033[0m\n")

        # Ask the user to choose a file by number
        choice = input("\033[32m Choose a log file by number\n - Enter to Select Latest \n - \'r\' to refresh:  \033[0m")
        # If the input is empty, default to the first log file
        if choice == 'r' or choice == 'R':
            print("\n \033[92m===REFRESHING====\033[0m\n")
            return
        else:
            choice = 1 if choice == "" else int(choice)

        # Open the chosen file in read mode
        with open(os.path.join(directory, files[choice - 1]), 'r') as f:
            # Create a memory-mapped object from the file
            mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            # Return the memory-mapped object
            return mm
    except Exception as e:
        # Print the error message and return an empty string
        print(f"An error occurred: {e}")
        return ""


def extract_failed_test_cases(mm: mmap.mmap, temp_file_path: str):
    """
    Extracts failed test cases from the logs and writes them to a temporary file.
    The keys are the fail counts and the values are lists of reasons.
    """
    # Compile regular expressions for matching failed test cases and reasons
    failed_pattern = re.compile(rb'\((\d+) FAILED\)')
    reason_pattern = re.compile(rb'(.*?FAILED)')
    end_reason_pattern = re.compile(rb'HeadlessChrome \d+\.\d+\.\d')

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
                    # Extract the reason lines from the memory-mapped object using a generator expression
                    reason_lines = extract_reasons(iter(mm.readline, b""), reason_pattern, end_reason_pattern)
                    temp.write("====================================================================================\n")
                    # Write the fail count to the temporary file
                    temp.write(f"{fail_count} FAILED:\n")
                    # Write each reason line to the temporary file with a tab indentation
                    for reason in reason_lines:
                        temp.write(f"\t{reason}\n")
                    # Add the fail count to the seen set
                    seen_fail_counts.add(fail_count)
        if not seen_fail_counts:
            temp.write("\n")
            temp.write("  _   _          _____                           _____                       _ \n")
            temp.write(" | \\ | | ___   | ____|_ __ _ __ ___  _ __ ___   |  ___|__  _   _ _ __    __|  |\n")
            temp.write(" |  \\| |/ _ \\  |  _| | '__| '__/ _  \| '__/ __| | |_ / _  \| | | | '_ \ /     |\n")
            temp.write(" | |\\  | (_) | | |___| |  | | | (_) | |   \__ \ |  _| (_) | |_| | | | | (_|   |\n")
            temp.write(" |_| \\_|\\___/  |_____|_|  |_|  \___/|_|  |___/ |_|  \___/ \ __,_|_| |_|\__,__ |\n")
            temp.write("\n")

        # Close the memory-mapped object
        mm.close()


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
            temp.write("============================================================================")
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
            # Create a temporary file path with a .txt suffix
            temp_file_path = tempfile.mktemp(suffix=".txt")
            # Extract failed test cases from the memory-mapped object and write them to the temporary file
            extract_failed_test_cases(mm, temp_file_path)
            # Close the memory-mapped object
            mm.close()
            # Open the temporary file with Visual Studio Code
            os.system(f"code {temp_file_path}")

        print("\033[94m                                                                                 ")
        print("              ,d88b.                    ,d88b.                    ,d88b.         ")
        print(" ,d88b.    ,'    \`Y88P'   ,d88b.    , '    \`Y88P'   ,d88b.    ,'     \`Y88P'   ")
        print("'    \`Y88P'   ,d88b.    , '    \`Y88P'   ,d88b.    , '    \`Y88P'  ,d88b.     ,  ")
        print("             '   \`Y88P'               '    \`Y88P'               '     \`Y88P'  ")
        print("                                                                                 ")
        print("                                                                                 \033[0m")

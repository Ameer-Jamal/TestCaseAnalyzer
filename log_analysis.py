import os
import re
import tempfile
import utilities as utils
import mmap  # For memory-mapped file objects
from typing import Dict, List, Set  # For type annotations


def _write_to_temp_file(results: Dict[int, List[str]]) -> str:
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


def _get_failed_pattern():
    return re.compile(rb'\((\d+) FAILED\)')


def _get_reason_pattern():
    return re.compile(rb'(.*?FAILED)')


def _get_end_of_reason_pattern():
    return re.compile(rb'HeadlessChrome \d+\.\d+\.\d')


def _extract_reasons(lines: iter, start_pattern: re.Pattern, end_pattern: re.Pattern):
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


def _write_failure_found_in_file(file, mm, fail_count, reason_pattern, end_reason_pattern):
    """ Extract the reason lines from the memory-mapped object using a generator expression"""
    reason_lines = _extract_reasons(iter(mm.readline, b""), reason_pattern, end_reason_pattern)
    utils.insert_line_separator_in_file(file, True, 2)
    # Write the fail count to the temporary file
    file.write(f"{fail_count} FAILED:\n")
    # Write each reason line to the temporary file with a tab indentation
    for reason in reason_lines:
        file.write(f"\t{reason}\n")
    # Add the fail count to the seen set


#####################################################################################################################

class LogAnalysis:

    @staticmethod
    def get_files_from_dir(directory, is_reversed):
        """Get a list of files in the directory."""
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        files.sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=is_reversed)
        return files

    @staticmethod
    def extract_failed_test_cases(mm: mmap.mmap, temp_file_path: str):
        """
        Extracts failed test cases from the logs and writes them to a temporary file.
        The keys are the fail counts and the values are lists of reasons.
        """
        # Compile regular expressions for matching failed test cases and reasons
        failed_pattern = _get_failed_pattern()
        reason_pattern = _get_reason_pattern()
        end_reason_pattern = _get_end_of_reason_pattern()

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
                        _write_failure_found_in_file(temp, mm, fail_count, reason_pattern,
                                                                 end_reason_pattern, )
                        seen_fail_counts.add(fail_count)
            if not seen_fail_counts:
                utils.write_no_errors_message_to_file(temp)

            # Close the memory-mapped object
            mm.close()

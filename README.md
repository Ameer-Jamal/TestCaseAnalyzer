# TestCaseAnalyzer

## Overview

`TestCaseAnalyzer` is a Python application designed to parse and analyze test case logs. It extracts failed test cases along with the reasons for their failure and writes the results to a temporary file. This is especially useful for large log files where manual inspection becomes tedious.

## Features

- Efficiently handles large log files (up to 10MB or more)
- Uses memory-mapped files for optimized performance
- Extracts failed test cases and reasons for failure
- Writes the results to a temporary file for easy inspection

## Prerequisites

- Python 3.x
- `re` for regular expressions
- `os` for file and directory operations
- `mmap` for memory-mapped file support
- `tempfile` for creating temporary files

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/TestCaseAnalyzer.git
    ```

2. Navigate to the project directory:

    ```bash
    cd TestCaseAnalyzer
    ```

## Usage

1. Run the script:

    ```bash
    python main.py
    ```

2. Follow the on-screen prompts to select a log file.

3. The script will process the log file and write the results to a temporary file.

4. The temporary file will be opened in your default text editor for inspection.

## Limitations

- The script is optimized for log files generated in a specific format. Customization may be needed for other formats.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.


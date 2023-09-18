# TestCaseAnalyzer

## Overview
`TestCaseAnalyzer` is a Python application specifically tailored for Angular applications using Jasmine and Karma for testing. It parses and analyzes test case logs to extract failed test cases along with the reasons for their failure. The results are then written to a temporary file for easy inspection. This tool is especially optimized for large log files and is invaluable for projects where manual log inspection becomes cumbersome.
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
    git clone https://github.com/Ameer-Jamal/TestCaseAnalyzer.git
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
- This program is tested for angular applications with this package.json:
- "codelyzer": "^4.1.0",
- "jasmine-core": "2.6.2",
- "jasmine-spec-reporter": "4.1.0",
- "karma": "1.7.0",
- "karma-chrome-launcher": "2.1.1",
- "karma-cli": "1.0.1",
- "karma-coverage-istanbul-reporter": "2.1.1",
- "karma-jasmine": "1.1.0",
- "karma-jasmine-html-reporter": "0.2.2",
- "karma-junit-reporter": "1.2.0",
- "ng-mocks": "7.7.0",
-  "protractor": "5.1.2",
- "puppeteer": "1.12.2",

Tested on:
- "@angular/core": "6.0.7",
---
## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.


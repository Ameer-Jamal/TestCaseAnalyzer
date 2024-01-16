import tkinter as tk
import os
from tkinter import filedialog, messagebox, Listbox, Scrollbar, VERTICAL
import mmap
import tempfile
import utilities as utils
from log_analysis import LogAnalysis


class LogFileApp:
    def __init__(self, master):
        self.master = master

        master.title("Log File Analyzer")

        # Directory selection button
        self.select_dir_button = tk.Button(master, text="Select Log Directory", command=self.select_directory)
        self.select_dir_button.pack()

        # Listbox with scrollbar for displaying log files
        self.scrollbar = Scrollbar(master, orient=VERTICAL)
        self.log_files_listbox = Listbox(master, yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.log_files_listbox.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.log_files_listbox.pack(fill="both", expand=True)

        # Process button
        self.process_button = tk.Button(master, text="Process Selected File", command=self.process_file)
        self.process_button.pack()

        # Open in VS Code button
        self.open_vscode_button = tk.Button(master, text="Open in VS Code", command=self.open_in_vscode)
        self.open_vscode_button.pack()

        # Text area for output
        self.output_text = tk.Text(master, height=15, width=50)
        self.output_text.pack()

        self.log_directory = None
        self.files = []

    def select_directory(self):
        self.log_directory = filedialog.askdirectory()
        if self.log_directory:
            self.populate_files_listbox()

    def process_file(self):
        selected_index = self.log_files_listbox.curselection()
        if not selected_index:
            messagebox.showinfo("Information", "Please select a file.")
            return

        choice = selected_index[0]
        mm = self.read_latest_log_from_directory(choice)
        if mm:
            if self.use_temp_file:
                # Create a temporary file
                with tempfile.NamedTemporaryFile(mode='w+', suffix=".txt", delete=False) as temp_file:
                    temp_file_path = temp_file.name
            else:
                # Create a unique file in the specified temp_directory
                if not os.path.exists(self.report_directory):
                    os.makedirs(self.report_directory)
                temp_file_path = utils.create_unique_filename(self.report_directory)

            # Extract failed test cases and write them to the file
            LogAnalysis.extract_failed_test_cases(mm, temp_file_path)
            mm.close()
            self.display_file_content(temp_file_path)

    def display_file_content(self, file_path):
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            self.output_text.delete('1.0', tk.END)  # Clear existing content
            self.output_text.insert(tk.END, content)  # Insert new content
        except Exception as e:
            self.show_alert(f"Error reading file: {e}")

    def open_in_vscode(self):
        # Assuming temp_file_path is stored as an instance variable
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
        """Populate the listbox with file names from the log directory."""
        self.log_files_listbox.delete(0, tk.END)  # Clear existing entries
        self.files = LogAnalysis.get_files_from_dir(self.log_directory, True)
        for idx, filename in enumerate(self.files, 1):
            self.log_files_listbox.insert(tk.END, f"{idx}. {filename}")

    @staticmethod
    def show_alert(message):
        """Show an alert message box."""
        tk.messagebox.showinfo("Alert", message)

    def set_configuration(self, config):
        self.config = config
        self.log_directory = self.config.get('log_location', {}).get('where_are_your_logs_located', '')
        self.use_temp_file = self.config.get('file_handling', {}).get('use_temp_file', True)
        self.report_directory = self.config.get('file_handling', {}).get('report_directory', '')

        # Check if a log directory is specified and populate the listbox
        if self.log_directory:
            self.populate_files_listbox()


def main():
    root = tk.Tk()
    root.mainloop()


if __name__ == "__main__":
    main()

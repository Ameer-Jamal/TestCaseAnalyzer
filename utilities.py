def insert_line_separator_in_file(temp_file, with_new_line, number_of_lines):
    """Writes in file seperator with amount and new line depending on params"""
    separator = "===============================================================================\n" if with_new_line \
        else "==============================================================================="
    for _ in range(number_of_lines):
        temp_file.write(separator)


def write_no_errors_message_to_file(temp_file):
    """Writes in file ascii art NO ERRORS FOUND in file"""

    temp_file.write("\n")
    temp_file.write("  _   _          _____                           _____                       _ \n")
    temp_file.write(" | \\ | | ___   | ____|_ __ _ __ ___  _ __ ___   |  ___|__  _   _ _ __    __|  |\n")
    temp_file.write(" |  \\| |/ _ \\  |  _| | '__| '__/ _  \| '__/ __| | |_ / _  \| | | | '_ \ /     |\n")
    temp_file.write(" | |\\  | (_) | | |___| |  | | | (_) | |   \__ \ |  _| (_) | |_| | | | | (_|   |\n")
    temp_file.write(" |_| \\_|\\___/  |_____|_|  |_|  \___/|_|  |___/ |_|  \___/ \ __,_|_| |_|\__,__ |\n")
    temp_file.write("\n")


def insert_console_separator():
    """Prints ascii art Wave in blue in console"""
    print("\033[94m                                                                                 ")
    print("              ,d88b.                    ,d88b.                    ,d88b.         ")
    print(" ,d88b.    ,'    \`Y88P'   ,d88b.    , '    \`Y88P'   ,d88b.    ,'     \`Y88P'   ")
    print("'    \`Y88P'   ,d88b.    , '    \`Y88P'   ,d88b.    , '    \`Y88P'  ,d88b.     ,  ")
    print("             '   \`Y88P'               '    \`Y88P'               '     \`Y88P'  ")
    print("                                                                                 ")
    print("                                                                                 \033[0m")


def print_refresh_message_in_console():
    """Prints refreshing with separation in console"""
    print("\n \033[92m==================================REFRESHING==================================\033[0m\n")


def print_white_seperator_in_console():
    print("\033[47m\t" * 13 + "\033[0m\n")


def print_file_name(filename, idx):
    """print file ID in purple and file name in yellow"""
    print(f"\033[95m{idx}\033[0m. \033[93m{filename}\033[0m\n")


def print_files_header_in_console():
    """print the word FILES with green highlight"""
    print("\n \033[42m \033[31m" + "\t" * 6 + "FILES:" + "\t" * 6 + "\033[0m\n")

def input_file_to_select():
    """input with input message in green"""
    return input(
        "\033[32m Choose a log file by number\n - Enter to Select Latest \n - \'r\' to refresh:  \033[0m")


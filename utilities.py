def insert_line_separator_in_file(temp_file, with_new_line, number_of_lines):
    separator = "===============================================================================\n" if with_new_line \
        else "==============================================================================="
    for _ in range(number_of_lines):
        temp_file.write(separator)


def write_no_errors_message_to_file(temp_file):
    temp_file.write("\n")
    temp_file.write("  _   _          _____                           _____                       _ \n")
    temp_file.write(" | \\ | | ___   | ____|_ __ _ __ ___  _ __ ___   |  ___|__  _   _ _ __    __|  |\n")
    temp_file.write(" |  \\| |/ _ \\  |  _| | '__| '__/ _  \| '__/ __| | |_ / _  \| | | | '_ \ /     |\n")
    temp_file.write(" | |\\  | (_) | | |___| |  | | | (_) | |   \__ \ |  _| (_) | |_| | | | | (_|   |\n")
    temp_file.write(" |_| \\_|\\___/  |_____|_|  |_|  \___/|_|  |___/ |_|  \___/ \ __,_|_| |_|\__,__ |\n")
    temp_file.write("\n")


def insert_console_separator():
    print("\033[94m                                                                                 ")
    print("              ,d88b.                    ,d88b.                    ,d88b.         ")
    print(" ,d88b.    ,'    \`Y88P'   ,d88b.    , '    \`Y88P'   ,d88b.    ,'     \`Y88P'   ")
    print("'    \`Y88P'   ,d88b.    , '    \`Y88P'   ,d88b.    , '    \`Y88P'  ,d88b.     ,  ")
    print("             '   \`Y88P'               '    \`Y88P'               '     \`Y88P'  ")
    print("                                                                                 ")
    print("                                                                                 \033[0m")


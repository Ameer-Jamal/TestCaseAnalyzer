from PyQt5.Qsci import QsciLexerCustom
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
import re
import consts


class CustomLogLexer(QsciLexerCustom):
    def __init__(self, parent=None):
        super(CustomLogLexer, self).__init__(parent)
        self._styles = consts.STYLES

        # Set colors suitable for dark background
        self.setDefaultColor(QColor(*consts.COLORS["default"]))  # Light color for default text
        self.setColor(QColor(*consts.COLORS["error"]), self._styles["error"])  # Lighter red for errors
        self.setColor(QColor(*consts.COLORS["trace"]), self._styles["trace"])  # Light gray for traces
        self.setColor(QColor(*consts.COLORS["cyan"]), self._styles["cyan"])  # Cyan for specific lines
        self.setColor(QColor(*consts.COLORS["orange"]), self._styles["orange"])  # Orange for specific lines
        self.setColor(QColor(*consts.COLORS["green"]), self._styles["green"])  # Green for specific lines

    def language(self):
        return "Log"

    def description(self, style):
        for desc, sty in self._styles.items():
            if style == sty:
                return desc.capitalize()
        return ""

    import re

    def styleText(self, start, end):
        editor = self.editor()
        if editor is None:
            return

        source = self.getSourceText(editor, start, end)
        self.startStyling(start)
        text = source.decode('utf-8')
        lines = text.split('\n')

        position = start
        for line in lines:
            length = len(line)
            if position + length <= end:
                self.applyStyling(line, length, position, end)
                position += length
                if position < end:
                    self.setStyling(1, self._styles["default"])  # for newline character
                    position += 1

    def getSourceText(self, editor, start, end):
        source = bytearray(end - start)
        editor.SendScintilla(editor.SCI_GETTEXTRANGE, start, end, source)
        return source

    def applyStyling(self, line, length, position, end):
        if "FAILED" in line:
            self.setStyling(length, self._styles["error"])
        elif re.search(r'\bat\b', line):
            self.setStyling(length, self._styles["orange"])
        elif "Expected" in line or "TypeError" in line:
            self.setStyling(length, self._styles["green"])
        elif line.strip() == "=" * 79:
            self.setStyling(length, self._styles["cyan"])
        elif any(keyword in line for keyword in ["at ", "Error: ", "Usage: "]):
            self.setStyling(length, self._styles["trace"])
        else:
            self.setStyling(length, self._styles["default"])

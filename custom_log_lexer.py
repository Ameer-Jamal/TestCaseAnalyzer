from PyQt5.Qsci import QsciLexerCustom
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt


class CustomLogLexer(QsciLexerCustom):
    def __init__(self, parent=None):
        super(CustomLogLexer, self).__init__(parent)
        self._styles = {
            "default": 0,
            "error": 1,
            "trace": 2
        }
        self.setDefaultColor(QColor(Qt.black))
        self.setColor(QColor(Qt.red), self._styles["error"])
        self.setColor(QColor(Qt.darkGray), self._styles["trace"])

    def language(self):
        return "Log"

    def description(self, style):
        if style == self._styles["default"]:
            return "Default"
        elif style == self._styles["error"]:
            return "Error"
        elif style == self._styles["trace"]:
            return "Trace"
        return ""

    def styleText(self, start, end):
        editor = self.editor()
        if editor is None:
            return

        source = bytearray(end - start)
        editor.SendScintilla(editor.SCI_GETTEXTRANGE, start, end, source)

        self.startStyling(start)

        text = source.decode('utf-8')
        lines = text.split('\n')
        position = start

        for line in lines:
            length = len(line)
            if length > 0:
                if "FAILED" in line:
                    self.setStyling(length, self._styles["error"])
                elif any(keyword in line for keyword in ["at ", "Error: ", "Usage: "]):
                    self.setStyling(length, self._styles["trace"])
                else:
                    self.setStyling(length, self._styles["default"])
            self.setStyling(1, self._styles["default"])  # for newline character
            position += length + 1

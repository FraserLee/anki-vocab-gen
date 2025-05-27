from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QLineEdit, QSizePolicy
)
from PyQt5.QtCore import Qt, QEvent
import sys


class CardEditor(QWidget):
    def __init__(self):
        super().__init__()

        self.term_label = QLabel("Current Term:")
        self.term_title = QLabel("(none)")
        self.term_title.setStyleSheet("font-weight: bold; font-size: 18px")

        self.definition_input = QLineEdit()
        self.definition_input.setPlaceholderText("Enter definition here")

        layout = QVBoxLayout()
        layout.addWidget(self.term_label)
        layout.addWidget(self.term_title)
        layout.addWidget(QLabel("Definition:"))
        layout.addWidget(self.definition_input)

        self.setLayout(layout)

    def set_term(self, text):
        self.term_title.setText(text)
        self.definition_input.clear()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Card Editor")

        # Left: multi-line text input
        self.text_input = QTextEdit()
        self.text_input.setPlainText("foo\nbar\nbaz")

        # Right: card display
        self.card_editor = CardEditor()

        # Next button
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.show_next_card)

        # Trigger "Next" on Enter when focused on definition input
        self.card_editor.definition_input.returnPressed.connect(self.show_next_card)

        # Layout
        main_layout = QHBoxLayout()

        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Input Terms:"))
        left_layout.addWidget(self.text_input)
        left_layout.addStretch()

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.card_editor)
        right_layout.addStretch()
        right_layout.addWidget(self.next_button, alignment=Qt.AlignRight)

        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        QApplication.instance().installEventFilter(self)

    def show_next_card(self):
        text = self.text_input.toPlainText().strip()
        lines = text.splitlines()

        if not lines:
            self.card_editor.set_term("(no more terms)")
            return

        next_term = lines.pop(0)
        self.card_editor.set_term(next_term)
        self.text_input.setPlainText("\n".join(lines))


    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            widget = QApplication.widgetAt(event.globalPos())
            is_text = False
            w = widget
            while w:
                if isinstance(w, (QLineEdit, QTextEdit)):
                    is_text = True
                    break
                w = w.parent()
            if not is_text:
                focused = QApplication.focusWidget()
                if isinstance(focused, (QLineEdit, QTextEdit)):
                    focused.clearFocus()
        if event.type() == QEvent.KeyPress and event.key() in (Qt.Key_Return, Qt.Key_Enter):
            fw = QApplication.focusWidget()
            if not isinstance(fw, (QLineEdit, QTextEdit, QPushButton)):
                self.show_next_card()
                return True
        return super().eventFilter(obj, event)

app = QApplication(sys.argv)
window = MainWindow()
window.resize(600, 300)
window.show()
app.exec()

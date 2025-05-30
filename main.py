from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QLineEdit, QSizePolicy
)
from PyQt5.QtCore import Qt, QEvent
import sys
import os

# Editable multi-line text: Enter finishes edit, Shift+Enter newline, blur also finishes
class EditableTextEdit(QTextEdit):
    def __init__(self, finish_callback=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.finish_callback = finish_callback
    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        if self.finish_callback:
            self.finish_callback()
    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter) and event.modifiers() == Qt.NoModifier:
            if self.finish_callback:
                self.finish_callback()
        else:
            super().keyPressEvent(event)


class CardEditor(QWidget):
    def __init__(self):
        super().__init__()

        self.term_label = QLabel("Current Term:")
        self.term_title = QLabel("(none)")
        self.term_title.setStyleSheet("font-weight: bold; font-size: 18px")

        # Definition field (display and editor)
        self.definition_display = QLabel("")
        self.definition_input = QLineEdit()
        self.definition_input.setPlaceholderText("Enter definition here")
        self.definition_input.hide()
        self.definition_input.editingFinished.connect(self._on_definition_finished)
        # Example sentence field
        self.example_display = QLabel("")
        self.example_input = QLineEdit()
        self.example_input.setPlaceholderText("Enter example sentence here")
        self.example_input.hide()
        self.example_input.editingFinished.connect(self._on_example_finished)
        # Pinyin field
        self.pinyin_display = QLabel("")
        self.pinyin_input = QLineEdit()
        self.pinyin_input.setPlaceholderText("Enter pinyin here")
        self.pinyin_input.hide()
        self.pinyin_input.editingFinished.connect(self._on_pinyin_finished)
        # Notes field
        self.notes_display = QLabel("")
        self.notes_display.setWordWrap(True)
        self.notes_input = EditableTextEdit(finish_callback=self._on_notes_finished)
        self.notes_input.setPlaceholderText("Enter notes here")
        self.notes_input.hide()

        layout = QVBoxLayout()
        layout.addWidget(self.term_label)
        layout.addWidget(self.term_title)
        # Definition row
        def_row = QHBoxLayout()
        def_row.addWidget(QLabel("Definition:"))
        def_row.addWidget(self.definition_display, 1)
        def_row.addWidget(self.definition_input, 1)
        layout.addLayout(def_row)
        # Example sentence row
        ex_row = QHBoxLayout()
        ex_row.addWidget(QLabel("Example sentence:"))
        ex_row.addWidget(self.example_display, 1)
        ex_row.addWidget(self.example_input, 1)
        layout.addLayout(ex_row)
        # Pinyin row
        pin_row = QHBoxLayout()
        pin_row.addWidget(QLabel("Pinyin:"))
        pin_row.addWidget(self.pinyin_display, 1)
        pin_row.addWidget(self.pinyin_input, 1)
        layout.addLayout(pin_row)
        # Notes row
        note_row = QVBoxLayout()
        sub_row = QHBoxLayout()
        sub_row.addWidget(QLabel("Notes:"), alignment=Qt.AlignTop)
        sub_row.addWidget(self.notes_display, 1, Qt.AlignTop)
        note_row.addLayout(sub_row)
        note_row.addWidget(self.notes_input)
        layout.addLayout(note_row)

        self.setLayout(layout)

    def set_term(self, text):
        self.term_title.setText(text)
        # clear all fields and reset to display mode
        self.definition_input.clear(); self.definition_display.setText("")
        self.example_input.clear(); self.example_display.setText("")
        self.pinyin_input.clear(); self.pinyin_display.setText("")
        self.notes_input.clear(); self.notes_display.setText("")
        self.definition_input.hide(); self.definition_display.show()
        self.example_input.hide(); self.example_display.show()
        self.pinyin_input.hide(); self.pinyin_display.show()
        self.notes_input.hide(); self.notes_display.show()
    def start_edit(self, field):
        if field == 'definition':
            self.definition_input.setText(self.definition_display.text())
            self.definition_display.hide(); self.definition_input.show();
            self.definition_input.setFocus(); self.definition_input.selectAll()
        elif field == 'example':
            self.example_input.setText(self.example_display.text())
            self.example_display.hide(); self.example_input.show();
            self.example_input.setFocus(); self.example_input.selectAll()
        elif field == 'pinyin':
            self.pinyin_input.setText(self.pinyin_display.text())
            self.pinyin_display.hide(); self.pinyin_input.show();
            self.pinyin_input.setFocus(); self.pinyin_input.selectAll()
        elif field == 'notes':
            self.notes_input.setPlainText(self.notes_display.text())
            self.notes_display.hide(); self.notes_input.show();
            self.notes_input.setFocus()
    def finish_edit(self, field):
        if field == 'definition':
            txt = self.definition_input.text(); self.definition_display.setText(txt)
            self.definition_input.hide(); self.definition_display.show()
        elif field == 'example':
            txt = self.example_input.text(); self.example_display.setText(txt)
            self.example_input.hide(); self.example_display.show()
        elif field == 'pinyin':
            txt = self.pinyin_input.text(); self.pinyin_display.setText(txt)
            self.pinyin_input.hide(); self.pinyin_display.show()
        elif field == 'notes':
            txt = self.notes_input.toPlainText(); self.notes_display.setText(txt)
            self.notes_input.hide(); self.notes_display.show()
    def _on_definition_finished(self):
        self.finish_edit('definition')
        self.definition_input.clearFocus()
        mw = self.window()
        if hasattr(mw, 'next_button'):
            mw.next_button.setFocus()

    def _on_example_finished(self):
        self.finish_edit('example')
        self.example_input.clearFocus()
        mw = self.window()
        if hasattr(mw, 'next_button'):
            mw.next_button.setFocus()

    def _on_pinyin_finished(self):
        self.finish_edit('pinyin')
        self.pinyin_input.clearFocus()
        mw = self.window()
        if hasattr(mw, 'next_button'):
            mw.next_button.setFocus()

    def _on_notes_finished(self):
        self.finish_edit('notes')
        self.notes_input.clearFocus()
        mw = self.window()
        if hasattr(mw, 'next_button'):
            mw.next_button.setFocus()


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
        # Clear focus on click outside text inputs
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
        # Shortcut keys to edit fields: d=Definition, e=Example, p=Pinyin, n=Notes
        if event.type() == QEvent.KeyPress and event.modifiers() == Qt.NoModifier:
            # when typing inside any text input, do not trigger shortcuts
            focused = QApplication.focusWidget()
            if isinstance(focused, (QLineEdit, QTextEdit)):
                return super().eventFilter(obj, event)
            k = event.key()
            if k == Qt.Key_D:
                self.card_editor.start_edit('definition')
                return True
            if k == Qt.Key_E:
                self.card_editor.start_edit('example')
                return True
            if k == Qt.Key_P:
                self.card_editor.start_edit('pinyin')
                return True
            if k == Qt.Key_N:
                self.card_editor.start_edit('notes')
                return True
        # Enter outside inputs still triggers Next
        if event.type() == QEvent.KeyPress and event.key() in (Qt.Key_Return, Qt.Key_Enter):
            fw = QApplication.focusWidget()
            if not isinstance(fw, (QLineEdit, QTextEdit, QPushButton)):
                self.show_next_card(); return True
        return super().eventFilter(obj, event)

data_dir = os.path.expanduser('~/.anki_card_gen')
os.makedirs(data_dir, exist_ok=True)

app = QApplication(sys.argv)
window = MainWindow()
window.resize(600, 300)
window.show()
app.exec()

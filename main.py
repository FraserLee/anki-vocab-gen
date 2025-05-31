from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QBoxLayout, QLayout,
    QPushButton, QTextEdit, QLabel, QLineEdit, QSizePolicy, QComboBox
)
from PyQt5.QtCore import Qt, QEvent, QObject
from PyQt5.QtGui import QKeyEvent, QFocusEvent, QMouseEvent
from typing import Any, Callable, Optional, cast, Dict, Union
from dataclasses import dataclass
import sys
import os

# Editable multi-line text: Enter finishes edit, Shift+Enter newline, blur also finishes
class EditableTextEdit(QTextEdit):
    def __init__(self, finish_callback: Optional[Callable[[], None]] = None, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.finish_callback = finish_callback

    def focusOutEvent(self, event: QFocusEvent) -> None:
        super().focusOutEvent(event)
        if self.finish_callback:
            self.finish_callback()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.Key_Return, Qt.Key_Enter) and int(event.modifiers()) == Qt.NoModifier:
            if self.finish_callback:
                self.finish_callback()
        else:
            super().keyPressEvent(event)


@dataclass
class CardField:
    key: str
    label: str
    input_widget_cls: type
    placeholder: str
    shortcut: Optional[int] = None

LANGUAGE_FIELDS = {
    "Chinese": [
        CardField("definition", "Definition:", QLineEdit, "Enter definition here", Qt.Key_D),
        CardField("example", "Example sentence:", QLineEdit, "Enter example sentence here", Qt.Key_E),
        CardField("pinyin", "Pinyin:", QLineEdit, "Enter pinyin here", Qt.Key_P),
        CardField("notes", "Notes:", EditableTextEdit, "Enter notes here", Qt.Key_N),
    ],
    "English": [
        CardField("definition", "Definition:", QLineEdit, "Enter definition here", Qt.Key_D),
        CardField("example", "Example sentence:", QLineEdit, "Enter example sentence here", Qt.Key_E),
        CardField("ipa", "IPA:", QLineEdit, "Enter IPA here", Qt.Key_I),
        CardField("notes", "Notes:", EditableTextEdit, "Enter notes here", Qt.Key_N),
    ],
}


class CardEditor(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.fields = LANGUAGE_FIELDS["Chinese"]
        self.widgets: Dict[str, tuple[QLabel, Union[QLineEdit, EditableTextEdit]]] = {}
        self.term_title = QLabel("(none)")
        self.term_title.setStyleSheet("font-weight: bold; font-size: 18px")
        self._layout = QVBoxLayout()
        self._layout.addWidget(self.term_title)
        self._fields_start_index = self._layout.count()
        self._build_fields()
        self.setLayout(self._layout)

    def _build_fields(self) -> None:
        for field in self.fields:

            display = QLabel("")

            if field.input_widget_cls == EditableTextEdit:
                display.setWordWrap(True)
                input_widget = field.input_widget_cls(
                    finish_callback=lambda k=field.key: self._on_field_finished(k)
                )
            elif field.input_widget_cls == QLineEdit:
                input_widget = field.input_widget_cls()
                input_widget.editingFinished.connect(
                    lambda k=field.key: self._on_field_finished(k)
                )
            else:
                raise ValueError(f"Unsupported input widget class: {field.input_widget_cls}")

            input_widget.setPlaceholderText(field.placeholder)
            input_widget.hide()

            if field.input_widget_cls == EditableTextEdit:
                row: QBoxLayout = QVBoxLayout()
                sub_row = QHBoxLayout()
                sub_row.addWidget(QLabel(field.label), alignment=Qt.AlignTop)
                sub_row.addWidget(display, 1, Qt.AlignTop)
                row.addLayout(sub_row)
                row.addWidget(input_widget)
                self._layout.addLayout(row)
            elif field.input_widget_cls == QLineEdit:
                row = QHBoxLayout()
                row.addWidget(QLabel(field.label))
                row.addWidget(display, 1)
                row.addWidget(input_widget, 1)
                self._layout.addLayout(row)
            else:
                raise ValueError(f"Unsupported input widget class: {field.input_widget_cls}")

            self.widgets[field.key] = (display, input_widget)

    def set_fields(self, lang: str) -> None:
        self.fields = LANGUAGE_FIELDS.get(lang, [])
        while self._layout.count() > self._fields_start_index:
            item = self._layout.takeAt(self._layout.count() - 1)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                layout = item.layout()
                if layout:
                    self._clear_layout(layout)
        self.widgets.clear()
        self._build_fields()

    def _clear_layout(self, layout: QLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                sub_layout = item.layout()
                if sub_layout:
                    self._clear_layout(sub_layout)

    def set_term(self, text: str) -> None:
        self.term_title.setText(text)
        for display, input_widget in self.widgets.values():
            input_widget.clear()
            display.setText("")
            input_widget.hide()
            display.show()

    def start_edit(self, field_key: str) -> None:
        if self.term_title.text() in ("(none)", "(no more terms)"):
            return
        if field_key not in self.widgets:
            return
        display, input_widget = self.widgets[field_key]
        text = display.text()
        if isinstance(input_widget, QLineEdit):
            input_widget.setText(text)
            input_widget.selectAll()
        else:
            input_widget.setPlainText(text)
        display.hide()
        input_widget.show()
        input_widget.setFocus()

    def finish_edit(self, field_key: str) -> None:
        if field_key not in self.widgets:
            return
        display, input_widget = self.widgets[field_key]
        if isinstance(input_widget, QLineEdit):
            txt = input_widget.text()
        else:
            txt = input_widget.toPlainText()
        display.setText(txt)
        input_widget.hide()
        display.show()

    def _on_field_finished(self, field_key: str) -> None:
        self.finish_edit(field_key)
        display, input_widget = self.widgets[field_key]
        input_widget.clearFocus()
        mw = self.window()
        if hasattr(mw, "next_button"):
            mw.next_button.setFocus()


class MainWindow(QMainWindow):
    def __init__(self) -> None:
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
        lang_row = QHBoxLayout()
        lang_row.addWidget(QLabel("Target Language:"))
        self.target_lang_combo = QComboBox()
        self.target_lang_combo.addItems(["Chinese", "English"])
        self.target_lang_combo.currentTextChanged.connect(self.card_editor.set_fields)
        lang_row.addWidget(self.target_lang_combo)
        # initialize fields based on selected language
        self.card_editor.set_fields(self.target_lang_combo.currentText())
        left_layout.addLayout(lang_row)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.card_editor)
        right_layout.addStretch()
        right_layout.addWidget(self.next_button, alignment=Qt.AlignRight)

        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        inst: Optional[QObject] = QApplication.instance()
        assert inst is not None
        inst.installEventFilter(self)

    def show_next_card(self) -> None:
        text = self.text_input.toPlainText().strip()
        lines = text.splitlines()

        if not lines:
            self.card_editor.set_term("(no more terms)")
            return

        next_term = lines.pop(0)
        self.card_editor.set_term(next_term)
        self.text_input.setPlainText("\n".join(lines))


    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        # Clear focus on click outside text inputs
        if event.type() == QEvent.MouseButtonPress:
            me = cast(QMouseEvent, event)
            widget: Optional[QObject] = QApplication.widgetAt(me.globalPos())
            is_text = False
            w: Optional[QObject] = widget
            while w is not None:
                if isinstance(w, (QLineEdit, QTextEdit)):
                    is_text = True
                    break
                w = w.parent()
            if not is_text:
                focused = QApplication.focusWidget()
                if isinstance(focused, (QLineEdit, QTextEdit)):
                    focused.clearFocus()
        if event.type() == QEvent.KeyPress:
            ke = cast(QKeyEvent, event)
            if int(ke.modifiers()) == Qt.NoModifier:
                focused = QApplication.focusWidget()
                if isinstance(focused, (QLineEdit, QTextEdit)):
                    return super().eventFilter(obj, event)
                k = ke.key()
                for field in self.card_editor.fields:
                    if field.shortcut is not None and k == field.shortcut and field.key in self.card_editor.widgets:
                        self.card_editor.start_edit(field.key)
                        return True
            if ke.key() in (Qt.Key_Return, Qt.Key_Enter):
                fw = QApplication.focusWidget()
                if not isinstance(fw, (QLineEdit, QTextEdit, QPushButton)):
                    self.show_next_card()
                    return True
        return super().eventFilter(obj, event)

data_dir = os.path.expanduser('~/.anki_card_gen')
os.makedirs(data_dir, exist_ok=True)

app = QApplication(sys.argv)
window = MainWindow()
window.resize(600, 300)
window.show()
app.exec()

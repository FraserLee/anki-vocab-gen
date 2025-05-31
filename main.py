from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QBoxLayout, QLayout,
    QPushButton, QTextEdit, QLabel, QLineEdit, QComboBox, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt, QEvent, QObject
from PyQt5.QtGui import QKeyEvent, QFocusEvent, QMouseEvent
from dataclasses import dataclass
from defaults import LANGUAGE_DEFAULTS
from typing import Any, Callable, Dict, List, Optional, Union, cast
import sys
import unicodedata
import data

# Editable multi-line text: Enter finishes edit, Shift+Enter newline, blur also finishes
class QTextAreaEdit(QTextEdit):
    def __init__(self, finish_callback: Optional[Callable[[], None]] = None, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.finish_callback = finish_callback

    def focusOutEvent(self, event: QFocusEvent) -> None:
        super().focusOutEvent(event)
        if self.finish_callback:
            self.finish_callback()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Escape) and int(event.modifiers()) == Qt.NoModifier:
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
        CardField("definition",  "[d]efinition:",        QLineEdit,      "Enter definition here",        Qt.Key_D),
        CardField("pinyin",      "[p]inyin:",            QLineEdit,      "Enter pinyin here",            Qt.Key_P),
        CardField("function",    "[f]unction:",          QLineEdit,      "Enter function here",          Qt.Key_F),
        CardField("example",     "[e]xample sentence:",  QLineEdit,      "Enter example sentence here",  Qt.Key_E),
        CardField("notes",       "[n]otes:",             QTextAreaEdit,  "Enter notes here",             Qt.Key_N),
    ],
    "English": [
        CardField("definition",  "[d]efinition:",        QLineEdit,      "Enter definition here",        Qt.Key_D),
        CardField("function",    "[f]unction:",          QLineEdit,      "Enter function here",          Qt.Key_F),
        CardField("ipa",         "[i]pa:",               QLineEdit,      "Enter IPA here",               Qt.Key_I),
        CardField("example",     "[e]xample sentence:",  QLineEdit,      "Enter example sentence here",  Qt.Key_E),
        CardField("notes",       "[n]otes:",             QTextAreaEdit,  "Enter notes here",             Qt.Key_N),
    ],
}



class CardEditor(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.fields = LANGUAGE_FIELDS["Chinese"]
        self.defaults_provider: Callable[[str], Any] = lambda _: {}
        self.widgets: Dict[str, tuple[QLabel, QLabel, Union[QLineEdit, QTextAreaEdit]]] = {}
        self.term_title = QLabel("(none)")
        self.term_title.setStyleSheet("font-weight: bold; font-size: 18px")
        self.term_title.setWordWrap(True)
        self.term_title.setTextFormat(Qt.RichText)
        self._layout = QVBoxLayout()
        self._layout.addWidget(self.term_title, alignment=Qt.AlignTop)
        self._fields_start_index = self._layout.count()
        self._build_fields()
        self.setLayout(self._layout)
        self.synset_options: list[Dict[str, str]] = []
        self.current_syn_index: int = 0
        self.selecting_synset: bool = False
        self.example_options: list[str] = []
        self.current_example_index: int = 0
        self.example_index_selected: Optional[int] = None
        self.selecting_example: bool = False

    def _build_fields(self) -> None:
        for field in self.fields:

            label_widget = QLabel(field.label)
            display = QLabel("")
            display.setWordWrap(True)
            display.setTextFormat(Qt.RichText)

            if field.input_widget_cls == QTextAreaEdit:
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

            if field.input_widget_cls == QTextAreaEdit:
                row: QBoxLayout = QVBoxLayout()
                sub_row = QHBoxLayout()
                sub_row.addWidget(label_widget, alignment=Qt.AlignTop)
                sub_row.addWidget(display, 1, Qt.AlignTop)
                row.addLayout(sub_row)
                row.addWidget(input_widget)
                self._layout.addLayout(row)
            elif field.input_widget_cls == QLineEdit:
                row = QHBoxLayout()
                row.addWidget(label_widget, alignment=Qt.AlignTop)
                row.addWidget(display, 1, Qt.AlignTop)
                row.addWidget(input_widget, 1, Qt.AlignTop)
                self._layout.addLayout(row)
            else:
                raise ValueError(f"Unsupported input widget class: {field.input_widget_cls}")

            self.widgets[field.key] = (label_widget, display, input_widget)

        self._layout.addStretch(1)

    def _strip_brackets(self, label: str) -> str:
        if len(label) >= 3 and label[0] == '[' and label[2] == ']':
            return label[1] + label[3:]
        return label

    def set_fields(self, lang: str) -> None:

        self.fields = LANGUAGE_FIELDS.get(lang, [])
        self.defaults_provider = LANGUAGE_DEFAULTS.get(lang, lambda _: {})

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
        options = self.defaults_provider(text)
        if isinstance(options, list):
            self.synset_options = options
        else:
            self.synset_options = [options]
        self.current_syn_index = 0
        self.selecting_synset = len(self.synset_options) > 1
        mw = self.window()
        if hasattr(mw, "setWindowTitle"):
            if self.selecting_synset:
                mw.setWindowTitle("Press Up/Down to browse defaults, Space to select")
            else:
                mw.setWindowTitle("Card Editor")

        count = len(self.synset_options)
        index = 1
        title = text
        if self.selecting_synset:
            curr = self.synset_options[0]
            info_parts = [f"{index}/{count}"]
            pos = curr.get("pos", "")
            if pos:
                info_parts.append(pos)
            syns = curr.get("synonyms", "")
            if syns:
                info_parts.append(syns)
            title = f"{text} ({' - '.join(info_parts)})"
        self.term_title.setText(title)

        self.current_example_index = 0
        self.example_index_selected = None
        self.selecting_example = False
        self._apply_current_defaults()

    def start_edit(self, field_key: str) -> None:
        if self.term_title.text() in ("(none)", "(no more terms)") or self.selecting_synset:
            return
        if field_key not in self.widgets:
            return
        if field_key == "example" and self.example_options and self.example_index_selected is None:
            if len(self.example_options) == 1:
                self.confirm_example_option_selection(0)
                return
            self.selecting_example = True
            mw = self.window()
            if hasattr(mw, "setWindowTitle"):
                mw.setWindowTitle(f"Press 1-{len(self.example_options)} to select example")
            _, display, _ = self.widgets.get("example", (None, None, None))
            if display is not None:
                preview = "\n".join(
                    f"({i+1}) {ex}" for i, ex in enumerate(self.example_options)
                )
                display.setText(preview)
            return
        _, display, input_widget = self.widgets[field_key]
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
        label_widget, display, input_widget = self.widgets[field_key]
        if isinstance(input_widget, QLineEdit):
            txt = input_widget.text()
        else:
            txt = input_widget.toPlainText()
        display.setText(txt)
        input_widget.hide()
        display.show()
        field = next(f for f in self.fields if f.key == field_key)
        if self.selecting_synset:
            label_widget.setText(self._strip_brackets(field.label))
        else:
            label_widget.setText(field.label)

    def _on_field_finished(self, field_key: str) -> None:
        self.finish_edit(field_key)
        _, _, input_widget = self.widgets[field_key]
        input_widget.clearFocus()
        mw = self.window()
        if hasattr(mw, "next_button"):
            mw.next_button.setFocus()

    def next_syn_option(self) -> None:
        """Preview next synset option."""
        if not self.selecting_synset:
            return
        self.current_syn_index = (self.current_syn_index + 1) % len(self.synset_options)
        self._apply_current_defaults()

    def prev_syn_option(self) -> None:
        """Preview previous synset option."""
        if not self.selecting_synset:
            return
        self.current_syn_index = (self.current_syn_index - 1) % len(self.synset_options)
        self._apply_current_defaults()

    def confirm_syn_option_selection(self) -> None:
        """Confirm current synset option and disable selection mode."""
        if not self.selecting_synset:
            return
        self.selecting_synset = False
        self._apply_current_defaults()
        text = self.term_title.text().split(" ", 1)[0]
        self.term_title.setText(text)
        mw = self.window()
        if hasattr(mw, "setWindowTitle"):
            mw.setWindowTitle("Card Editor")

    def confirm_example_option_selection(self, index: int) -> None:
        """Confirm selected example option and populate the example field."""
        if not self.selecting_example:
            return
        if index < 0 or index >= len(self.example_options):
            return
        self.selecting_example = False
        self.example_index_selected = index
        mw = self.window()
        if hasattr(mw, "setWindowTitle"):
            mw.setWindowTitle("Card Editor")
        _, display, _ = self.widgets.get("example", (None, None, None))
        if display is not None:
            display.setText(self.example_options[index])

    def _apply_current_defaults(self) -> None:
        """Apply synset defaults and update title with index."""
        count = len(self.synset_options)
        index = self.current_syn_index + 1
        term = self.term_title.text().split(" ", 1)[0]
        if self.selecting_synset:
            curr = self.synset_options[self.current_syn_index]
            info_parts = [f"{index}/{count}"]
            pos = curr.get("pos", "")
            if pos:
                info_parts.append(pos)
            syns = curr.get("synonyms", "")
            if syns:
                info_parts.append(syns)
            term = f"{term} ({' - '.join(info_parts)})"
        self.term_title.setText(term)
        defaults = self.synset_options[self.current_syn_index]
        self.example_options = cast(List[str], defaults.get("example", []))
        # update display-only fields and unbracket labels
        field_map = {f.key: f for f in self.fields}
        for key, (label_widget, display, _) in self.widgets.items():
            value = defaults.get(key, "")
            if isinstance(value, list):
                value = "\n<hr> ".join(value)
            display.setText(value)
            if self.selecting_synset:
                label_widget.setText(self._strip_brackets(field_map[key].label))
            else:
                label_widget.setText(field_map[key].label)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Card Editor")

        # Left: multi-line text input
        self.text_input = QTextEdit()
        self.text_input.setPlainText("研究员\n深度\n能力\n与\n积累\n高等教育\nrun\njailhouse\nrock")

        # Right: card display
        self.card_editor = CardEditor()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.card_editor)
        scroll.setFrameShape(QFrame.NoFrame)

        # Next button
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.show_next_card)
        self.next_button.setToolTip("Press Space or Enter to advance to the next card")


        # Layout
        main_layout = QHBoxLayout()

        left_layout = QVBoxLayout()
        lang_row = QHBoxLayout()
        lang_row.addWidget(QLabel("Target Language:"))
        self.target_lang_combo = QComboBox()
        self.target_lang_combo.addItems(["Chinese", "English"])
        self.target_lang_combo.currentTextChanged.connect(self.card_editor.set_fields)
        lang_row.addWidget(self.target_lang_combo)
        lang_row.addStretch()
        self.card_editor.set_fields(self.target_lang_combo.currentText())
        left_layout.addLayout(lang_row)
        left_layout.addWidget(QLabel("Queue:"))
        left_layout.addWidget(self.text_input)

        right_layout = QVBoxLayout()
        right_layout.addWidget(scroll)
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
        text = self.text_input.toPlainText().strip().lower()
        text = unicodedata.normalize("NFKC", text) # replace U+2F00 with U+4E00, etc.
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
            if self.card_editor.selecting_synset:
                if ke.key() in (Qt.Key_Up, Qt.Key_K):
                    self.card_editor.prev_syn_option()
                    return True
                if ke.key() in (Qt.Key_Down, Qt.Key_J, Qt.Key_Tab):
                    self.card_editor.next_syn_option()
                    return True
                if ke.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
                    self.card_editor.confirm_syn_option_selection()
                    return True
            if self.card_editor.selecting_example:
                if Qt.Key_1 <= ke.key() <= Qt.Key_9:
                    idx = ke.key() - Qt.Key_1
                    self.card_editor.confirm_example_option_selection(idx)
                    return True
                return True
            if int(ke.modifiers()) == Qt.NoModifier:
                focused = QApplication.focusWidget()
                if isinstance(focused, (QLineEdit, QTextEdit)):
                    return super().eventFilter(obj, event)
                # While choosing between synsets, block editing shortcuts
                if self.card_editor.selecting_synset:
                    return True
                k = ke.key()
                for field in self.card_editor.fields:
                    if field.shortcut is not None and k == field.shortcut and field.key in self.card_editor.widgets:
                        self.card_editor.start_edit(field.key)
                        return True
            if ke.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
                fw = QApplication.focusWidget()
                if not isinstance(fw, (QLineEdit, QTextEdit, QPushButton)):
                    self.show_next_card()
                    return True
        return super().eventFilter(obj, event)

data.init()
app = QApplication(sys.argv)
window = MainWindow()
window.resize(600, 300)
window.show()
app.exec()

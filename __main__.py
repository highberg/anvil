import ctypes
import locale
import os
import sys
from algorithms.anvil import Anvil
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QProgressBar,
    QMessageBox,
    QFileDialog,
    QLabel,
    QDialog,
    QScrollArea,
)
from PyQt6.QtCore import QThread, pyqtSignal

translations = {
    "en": {
        "window_title": "Anvil Lossless Compression",
        "help_menu": "Help",
        "about_menu": "About",
        "user_guide_menu": "User Guide",
        "encode_tab": "Encode",
        "decode_tab": "Decode",
        "select_file_button": "SELECT FILE PATH",
        "select_save_button": "SELECT SAVE PATH",
        "start_encoding_button": "START ENCODING",
        "start_decoding_button": "START DECODING",
        "success_message_title": "Success",
        "success_message_body": "Your operation has been completed successfully!",
        "error_message_title": "Error",
        "error_message_body": "An error occurred:\n",
        "about_file_not_found_error": '"help/about.txt" not found.\nPlease provide the file and try again.',
        "user_guide_file_not_found_error": '"help/user_guide.txt" not found.\nPlease provide the file and try again.',
        "file_select_title": "Select File",
        "save_file_title": "Save File",
        "about_title": "About",
        "user_guide_title": "User Guide",
        "text_files": "Text Files",
        "document_files": "Document Files",
        "anvil_files": "Anvil Files",
    },
    "tr": {
        "window_title": "Anvil Kayıpsız Sıkıştırma",
        "help_menu": "Yardım",
        "about_menu": "Hakkında",
        "user_guide_menu": "Kullanım Kılavuzu",
        "encode_tab": "Encode",
        "decode_tab": "Decode",
        "select_file_button": "DOSYA YOLU SEÇ",
        "select_save_button": "KAYIT YOLU SEÇ",
        "start_encoding_button": "ENCODING'E BAŞLA",
        "start_decoding_button": "DECODING'E BAŞLA",
        "success_message_title": "Başarılı",
        "success_message_body": "İşleminiz başarıyla gerçekleştirildi!",
        "error_message_title": "Hata",
        "error_message_body": "Bir hata ile karşılaşıldı:\n",
        "about_file_not_found_error": '"help/about.txt" yolunda "Hakkında" dosyası bulunamadı.\nLütfen dosyayı sağlayıp tekrar deneyiniz.',
        "user_guide_file_not_found_error": '"help/user_guide.txt" yolunda "Kullanıcı Kılavuzu" dosyası bulunamadı.\nLütfen dosyayı sağlayıp tekrar deneyiniz.',
        "file_select_title": "Dosya Seç",
        "save_file_title": "Dosya Kaydet",
        "about_title": "Hakkında",
        "user_guide_title": "Kullanım Kılavuzu",
        "text_files": "Yazı Dosyaları",
        "document_files": "Döküman Belgeleri",
        "anvil_files": "Anvil Dosyaları",
    },
}


def get_language():
    lang = os.environ.get("LANG")
    win = sys.platform == "win32"
    if win:
        lang = locale.windows_locale[ctypes.windll.kernel32.GetUserDefaultUILanguage()]  # type: ignore
    lang = None if not isinstance(lang, str) or len(lang) < 2 else lang[:2]
    return lang if lang and lang in translations.keys() else "en"


current_lang = get_language()


def t(key):
    return translations[current_lang].get(key, key)


class Worker(QThread):
    finished = pyqtSignal(object)

    def __init__(self, file_command, file_path, save_path):
        super().__init__()
        self.file_command = file_command
        self.file_path = file_path
        self.save_path = save_path

    def run(self):
        try:
            self.file_command(self.file_path, self.save_path)
            self.finished.emit(None)
        except Exception as e:
            self.finished.emit(e)


class AboutDialog(QDialog):
    def __init__(self, title, text, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(600, 400)
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        content_widget = QWidget()
        scroll_area.setWidget(content_widget)
        layout = QVBoxLayout(content_widget)
        label = QLabel(text)
        label.setWordWrap(True)
        layout.addWidget(label)
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)


class FileWidget(QWidget):
    def __init__(
        self,
        file_command,
        start_button_text_key,
        file_types,
        file_default_type,
        save_types,
        save_default_type,
    ):
        super().__init__()
        self.file_command = file_command
        self.start_button_text_key = start_button_text_key
        self.file_types = file_types
        self.file_default_type = file_default_type
        self.save_types = save_types
        self.save_default_type = save_default_type
        self.file_path = None
        self.save_path = None
        self.layout = QVBoxLayout(self)
        self.file_button = QPushButton(t("select_file_button"))
        self.file_button.clicked.connect(self.select_file_path)
        self.layout.addWidget(self.file_button)
        self.save_button = QPushButton(t("select_save_button"))
        self.save_button.clicked.connect(self.select_save_path)
        self.layout.addWidget(self.save_button)
        self.start_button = QPushButton(t(start_button_text_key))
        self.start_button.clicked.connect(self.start_command)
        self.start_button.setEnabled(False)
        self.layout.addWidget(self.start_button)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.hide()
        self.layout.addWidget(self.progress_bar)

    def select_file_path(self):
        path, _ = QFileDialog.getOpenFileName(
            self, t("file_select_title"), "", self.file_types
        )
        if path:
            self.file_path = path
            self.file_button.setText(path)
            if self.file_path and self.save_path:
                self.start_button.setEnabled(True)

    def select_save_path(self):
        path, _ = QFileDialog.getSaveFileName(
            self, t("save_file_title"), "", self.save_types
        )
        if path:
            self.save_path = path
            self.save_button.setText(path)
            if self.file_path and self.save_path:
                self.start_button.setEnabled(True)

    def start_command(self):
        self.start_button.hide()
        self.progress_bar.show()
        self.file_button.setEnabled(False)
        self.save_button.setEnabled(False)
        self.worker = Worker(self.file_command, self.file_path, self.save_path)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.start()

    def on_worker_finished(self, error):
        self.progress_bar.hide()
        self.start_button.show()
        self.file_button.setEnabled(True)
        self.save_button.setEnabled(True)
        if error:
            QMessageBox.critical(
                self, t("error_message_title"), f"{t('error_message_body')}{error}"
            )
        else:
            QMessageBox.information(
                self, t("success_message_title"), t("success_message_body")
            )


class AnvilApp(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle(t("window_title"))
        self.setFixedSize(500, 200)
        self.read_help_files()
        self.set_menu()
        self.set_notebook()

    def read_help_files(self):
        lang = get_language()
        try:
            with open(f"help/about_{lang}.txt", "r", encoding="utf-8") as f:
                self.about_text = f.read()
        except FileNotFoundError:
            QMessageBox.critical(
                self, t("error_message_title"), t("about_file_not_found_error")
            )
            sys.exit(1)
        try:
            with open(f"help/user_guide_{lang}.txt", "r", encoding="utf-8") as f:
                self.user_guide_text = f.read()
        except FileNotFoundError:
            QMessageBox.critical(
                self, t("error_message_title"), t("user_guide_file_not_found_error")
            )
            sys.exit(1)

    def set_notebook(self):
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.encode_frame = FileWidget(
            file_command=Anvil.encode,
            start_button_text_key="start_encoding_button",
            file_types=f"{t('text_files')} (*.txt);;{t('document_files')} (*.doc *.docx)",
            file_default_type=".txt",
            save_types=f"{t('anvil_files')} (*.anvil)",
            save_default_type=".anvil",
        )
        self.decode_frame = FileWidget(
            file_command=Anvil.decode,
            start_button_text_key="start_decoding_button",
            file_types=f"{t('anvil_files')} (*.anvil)",
            file_default_type=".anvil",
            save_types=f"{t('text_files')} (*.txt);;{t('document_files')} (*.doc *.docx)",
            save_default_type=".txt",
        )
        self.tabs.addTab(self.encode_frame, t("encode_tab"))
        self.tabs.addTab(self.decode_frame, t("decode_tab"))

    def set_menu(self):
        menu = self.menuBar()
        help_menu = menu.addMenu(t("help_menu"))
        about_action = help_menu.addAction(t("about_menu"))
        about_action.triggered.connect(self.about)
        user_guide_action = help_menu.addAction(t("user_guide_menu"))
        user_guide_action.triggered.connect(self.user_guide)

    def about(self):
        dialog = AboutDialog(t("about_title"), self.about_text, self)
        dialog.exec()

    def user_guide(self):
        dialog = AboutDialog(t("user_guide_title"), self.user_guide_text, self)
        dialog.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AnvilApp()
    window.show()
    sys.exit(app.exec())

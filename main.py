import sys
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QToolBar,
    QTabWidget,
    QInputDialog,
    QMenu,
    QAction,
    QMessageBox,
    QStyle,
    QListWidget,
    QVBoxLayout,
    QLabel,
    QProgressBar,
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineDownloadItem
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter


class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bookmarks = {}

    def acceptNavigationRequest(self, url, nav_type, is_main_frame):
        if QApplication.mouseButtons() == Qt.MiddleButton:
            self.create_new_tab(url)
            return False
        return super().acceptNavigationRequest(url, nav_type, is_main_frame)

    def create_new_tab(self, url):
        browser = self.view().parent()
        new_tab = QWebEngineView()
        new_page = CustomWebEnginePage(new_tab)
        new_tab.setPage(new_page)
        new_tab.setUrl(url)
        new_tab.loadFinished.connect(lambda _: browser.update_tab_title(new_tab))
        browser.tab_widget.addTab(new_tab, "")
        browser.tab_widget.setCurrentWidget(new_tab)

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        print(f"JS: {message} ({sourceID}:{lineNumber})")


class DownloadManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Downloads")
        self.setGeometry(300, 300, 400, 200)
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

    def add_download(self, download_item):
        download_widget = DownloadWidget(download_item)
        self.layout.addWidget(download_widget)


class DownloadWidget(QWidget):
    def __init__(self, download_item):
        super().__init__()
        self.download_item = download_item
        self.layout = QHBoxLayout(self)
        self.label = QLabel(download_item.url().fileName())
        self.progress_bar = QProgressBar()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.progress_bar)
        self.setLayout(self.layout)
        self.download_item.downloadProgress.connect(self.update_progress)
        self.download_item.finished.connect(self.download_finished)

    def update_progress(self, received, total):
        if total > 0:
            self.progress_bar.setValue(int(received * 100 / total))

    def download_finished(self):
        QMessageBox.information(self, "Download Completed", f"{self.download_item.url().fileName()} has been downloaded.")
        self.progress_bar.setValue(100)


class WebBrowser(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window properties
        self.setWindowTitle("Web Browser")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(self.style().standardIcon(QStyle.SP_TitleBarMenuButton))

        # Create a QTabWidget for managing tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tab_widget.customContextMenuRequested.connect(self.show_tab_context_menu)

        # Create the initial tab
        self.browser = QWebEngineView()
        self.browser.setPage(CustomWebEnginePage(self.browser))
        self.browser.page().profile().downloadRequested.connect(self.handle_download)
        self.tab_widget.addTab(self.browser, "Google")

        # Create navigation buttons
        self.back_button = QPushButton("<--")
        self.forward_button = QPushButton("-->")
        self.refresh_button = QPushButton("🔃")
        self.home_button = QPushButton("🏠")
        self.bookmark_button = QPushButton("Bookmark")
        self.history_button = QPushButton("History")
        self.print_button = QPushButton("Print")
        self.fullscreen_button = QPushButton("Fullscreen")

        # Connect button clicks to corresponding browser methods
        self.back_button.clicked.connect(self.navigate_back)
        self.forward_button.clicked.connect(self.navigate_forward)
        self.refresh_button.clicked.connect(self.refresh_page)
        self.home_button.clicked.connect(self.go_home)
        self.bookmark_button.clicked.connect(self.add_bookmark)
        self.history_button.clicked.connect(self.show_history)
        self.print_button.clicked.connect(self.print_page)
        self.fullscreen_button.clicked.connect(self.toggle_fullscreen)

        # Create a "Change Theme" button
        self.change_theme_button = QPushButton("Change Theme")
        self.change_theme_button.clicked.connect(self.change_theme)

        # Create an address bar QLineEdit widget
        self.address_bar = QLineEdit()
        self.address_bar.returnPressed.connect(self.load_url)

        # Create a layout for the buttons and address bar
        toolbar_layout = QHBoxLayout()
        toolbar_layout.addWidget(self.back_button)
        toolbar_layout.addWidget(self.forward_button)
        toolbar_layout.addWidget(self.refresh_button)
        toolbar_layout.addWidget(self.home_button)
        toolbar_layout.addWidget(self.bookmark_button)
        toolbar_layout.addWidget(self.history_button)
        toolbar_layout.addWidget(self.print_button)
        toolbar_layout.addWidget(self.fullscreen_button)
        toolbar_layout.addWidget(self.change_theme_button)
        toolbar_layout.addWidget(self.address_bar)

        # Create a widget for the toolbar and set the layout
        toolbar_widget = QWidget()
        toolbar_widget.setLayout(toolbar_layout)

        # Create a toolbar and add the toolbar widget to it
        toolbar = QToolBar()
        toolbar.addWidget(toolbar_widget)

        # Add the toolbar and tab widget to the main window
        self.addToolBar(toolbar)
        self.setCentralWidget(self.tab_widget)

        # Create the download manager
        self.download_manager = DownloadManager()

        # Set dark theme as default
        self.set_dark_theme()

    def navigate_back(self):
        current_tab = self.tab_widget.currentWidget()
        current_tab.back()

    def navigate_forward(self):
        current_tab = self.tab_widget.currentWidget()
        current_tab.forward()

    def refresh_page(self):
        current_tab = self.tab_widget.currentWidget()
        current_tab.reload()

    def go_home(self):
        current_tab = self.tab_widget.currentWidget()
        current_tab.setUrl(QUrl("https://www.google.com"))

    def add_bookmark(self):
        current_tab = self.tab_widget.currentWidget()
        url = current_tab.url().toString()
        title = current_tab.title()
        self.browser.page().bookmarks[url] = title
        QMessageBox.information(self, "Bookmark Added", "Bookmark has been added.")

    def show_history(self):
        current_tab = self.tab_widget.currentWidget()
        history = self.browser.page().history()
        menu = QMenu(self)
        for i in range(history.count()):
            url = history.itemAt(i).url()
            action = QAction(url.toString(), self)
            action.setData(url)
            action.triggered.connect(self.open_history_url)
            menu.addAction(action)
        menu.exec_(current_tab.mapToGlobal(current_tab.pos()))

    def open_history_url(self):
        action = self.sender()
        url = action.data()
        self.create_new_tab(url)

    def change_theme(self):
        theme_dialog = QInputDialog()
        theme_dialog.setWindowTitle("Change Theme")
        theme_dialog.setLabelText("Select theme:")
        theme_dialog.setComboBoxItems(["Dark", "Light", "Chill", "Autumn", "Red", "Ocean"])
        theme_dialog.setComboBoxEditable(False)
        theme_dialog.setOkButtonText("Apply")
        theme_dialog.setCancelButtonText("Cancel")
        if theme_dialog.exec_() == QInputDialog.Accepted:
            theme = theme_dialog.textValue()
            if theme == "Dark":
                self.set_dark_theme()
            elif theme == "Light":
                self.set_light_theme()
            elif theme == "Chill":
                self.set_chill_theme()
            elif theme == "Autumn":
                self.set_autumn_theme()
            elif theme == "Red":
                self.set_red_theme()
            elif theme == "Ocean":
                self.set_ocean_theme()

    def set_dark_theme(self):
        self.setStyleSheet(
            """
            QMainWindow{
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                background: #3f3f3f;
                color: white;
                padding: 8px;
            }
            QTabBar::tab:hover {
                background: #2d2d2d;
            }
            QTabBar::tab:selected {
                background: #1e1e1e;
            }
            QTabWidget::pane {
                border-top: 2px solid #3f3f3f;
            }
            QLineEdit {
                background-color: #3f3f3f;
                color: white;
                padding: 6px;
            }
            QPushButton {
                background-color: #3f3f3f;
                color: white;
                padding: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2d2d2d;
            }
            QPushButton:pressed {
                background-color: #1e1e1e;
            }
            """
        )

    def set_light_theme(self):
        self.setStyleSheet(
            """
            QMainWindow{
                background-color: white;
            }
            QTabBar::tab {
                background: #f0f0f0;
                color: black;
                padding: 8px;
            }
            QTabBar::tab:hover {
                background: #e0e0e0;
            }
            QTabBar::tab:selected {
                background: white;
            }
            QTabWidget::pane {
                border-top: 2px solid #f0f0f0;
            }
            QLineEdit {
                background-color: #f0f0f0;
                color: black;
                padding: 6px;
            }
            QPushButton {
                background-color: #f0f0f0;
                color: black;
                padding: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: white;
            }
            """
        )

    def set_chill_theme(self):
        self.setStyleSheet(
            """
            QMainWindow{
                background-color: #457b9d;
            }
            QTabBar::tab {
                background: #a8dadc;
                color: black;
                padding: 8px;
            }
            QTabBar::tab:hover {
                background: #81b5ac;
            }
            QTabBar::tab:selected {
                background: #457b9d;
            }
            QTabWidget::pane {
                border-top: 2px solid #a8dadc;
            }
            QLineEdit {
                background-color: #a8dadc;
                color: black;
                padding: 6px;
            }
            QPushButton {
                background-color: #a8dadc;
                color: black;
                padding: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #81b5ac;
            }
            QPushButton:pressed {
                background-color: #457b9d;
            }
            """
        )

    def set_autumn_theme(self):
        self.setStyleSheet(
            """
            QMainWindow{
                background-color: #8d99ae;
            }
            QTabBar::tab {
                background: #c1a1d3;
                color: black;
                padding: 8px;
            }
            QTabBar::tab:hover {
                background: #b19cd9;
            }
            QTabBar::tab:selected {
                background: #8d99ae;
            }
            QTabWidget::pane {
                border-top: 2px solid #c1a1d3;
            }
            QLineEdit {
                background-color: #c1a1d3;
                color: black;
                padding: 6px;
            }
            QPushButton {
                background-color: #c1a1d3;
                color: black;
                padding: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #b19cd9;
            }
            QPushButton:pressed {
                background-color: #8d99ae;
            }
            """
        )

    def set_red_theme(self):
        self.setStyleSheet(
            """
            QMainWindow{
                background-color: #e63946;
            }
            QTabBar::tab {
                background: #f1faee;
                color: black;
                padding: 8px;
            }
            QTabBar::tab:hover {
                background: #f1faee;
            }
            QTabBar::tab:selected {
                background: #e63946;
            }
            QTabWidget::pane {
                border-top: 2px solid #f1faee;
            }
            QLineEdit {
                background-color: #f1faee;
                color: black;
                padding: 6px;
            }
            QPushButton {
                background-color: #f1faee;
                color: black;
                padding: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #f1faee;
            }
            QPushButton:pressed {
                background-color: #e63946;
            }
            """
        )

    def set_ocean_theme(self):
        self.setStyleSheet(
            """
            QMainWindow{
                background-color: #457b9d;
            }
            QTabBar::tab {
                background: #a8dadc;
                color: black;
                padding: 8px;
            }
            QTabBar::tab:hover {
                background: #81b5ac;
            }
            QTabBar::tab:selected {
                background: #457b9d;
            }
            QTabWidget::pane {
                border-top: 2px solid #a8dadc;
            }
            QLineEdit {
                background-color: #a8dadc;
                color: black;
                padding: 6px;
            }
            QPushButton {
                background-color: #a8dadc;
                color: black;
                padding: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #81b5ac;
            }
            QPushButton:pressed {
                background-color: #457b9d;
            }
            """
        )

    def is_valid_url(self, url):
        return url.startswith("http://") or url.startswith("https://")

    def load_url(self):
        url = self.address_bar.text()
        if self.is_valid_url(url):
            self.tab_widget.currentWidget().setUrl(QUrl(url))
        else:
            url = QUrl("https://www.google.com/search?q={}".format(url))
            self.tab_widget.currentWidget().setUrl(url)

    def create_new_tab(self, url):
        new_tab = QWebEngineView()
        new_tab.setPage(CustomWebEnginePage(new_tab))
        new_tab.setUrl(url)
        new_tab.loadFinished.connect(lambda _: self.update_tab_title(new_tab))
        self.tab_widget.addTab(new_tab, "")
        self.tab_widget.setCurrentWidget(new_tab)

    def update_tab_title(self, web_view):
        index = self.tab_widget.indexOf(web_view)
        title = web_view.page().title()
        self.tab_widget.setTabText(index, title)

    def close_tab(self, index):
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        else:
            self.close()

    def show_tab_context_menu(self, pos):
        menu = QMenu()
        reload_action = menu.addAction("Reload Tab")
        duplicate_action = menu.addAction("Duplicate Tab")
        close_action = menu.addAction("Close Tab")
        action = menu.exec_(self.tab_widget.mapToGlobal(pos))
        if action == reload_action:
            self.tab_widget.currentWidget().reload()
        elif action == duplicate_action:
            current_url = self.tab_widget.currentWidget().url()
            self.create_new_tab(current_url)
        elif action == close_action:
            self.close_tab(self.tab_widget.currentIndex())

    def print_page(self):
        printer = QPrinter()
        dialog = QPrintDialog(printer, self)
        if dialog.exec_() == QPrintDialog.Accepted:
            self.tab_widget.currentWidget().page().print(printer, lambda: None)

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def handle_download(self, download_item):
        self.download_manager.add_download(download_item)
        download_item.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    browser = WebBrowser()
    browser.show()
    sys.exit(app.exec_())

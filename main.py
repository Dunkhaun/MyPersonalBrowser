import sys
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QLineEdit, QPushButton, QToolBar, QTabWidget, QInputDialog, QMenu, QAction, QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

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

        # Get the title of the website
        new_tab.loadFinished.connect(lambda _: browser.update_tab_title(new_tab))

        browser.tab_widget.addTab(new_tab, "")  # Empty title for now
        browser.tab_widget.setCurrentWidget(new_tab)

class WebBrowser(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window properties
        self.setWindowTitle("Web Browser")
        self.setGeometry(100, 100, 800, 600)

        # Create a QTabWidget for managing tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)

        # Create a function for adding new tabs
        def add_new_tab():
            url, ok = QInputDialog.getText(
                None, "New Tab", "Enter URL or search query:"
            )
            if ok:
                if self.is_valid_url(url):
                    new_url = QUrl(url)
                else:
                    new_url = QUrl("https://www.google.com/search?q={}".format(url))
                new_tab = QWebEngineView()
                new_page = CustomWebEnginePage(new_tab)
                new_tab.setPage(new_page)
                new_tab.setUrl(new_url)

                # Get the title of the website
                new_tab.loadFinished.connect(lambda _: self.update_tab_title(new_tab))

                self.tab_widget.addTab(new_tab, "")  # Empty title for now
                self.tab_widget.setCurrentWidget(new_tab)

        # Create the initial tab
        self.browser = QWebEngineView()
        self.browser.setPage(CustomWebEnginePage(self.browser))
        self.tab_widget.addTab(self.browser, "Google")

        # Create navigation buttons
        self.back_button = QPushButton("<--")
        self.forward_button = QPushButton("-->")
        self.refresh_button = QPushButton("🔃")
        self.home_button = QPushButton("🏠")
        self.bookmark_button = QPushButton("Bookmark")  # New bookmark button

        # Connect button clicks to corresponding browser methods
        self.back_button.clicked.connect(self.navigate_back)
        self.forward_button.clicked.connect(self.navigate_forward)
        self.refresh_button.clicked.connect(self.refresh_page)
        self.home_button.clicked.connect(self.go_home)
        self.bookmark_button.clicked.connect(self.add_bookmark)  # Connect bookmark button

        # Create an address bar QLineEdit widget
        self.address_bar = QLineEdit()
        self.address_bar.returnPressed.connect(self.load_url)

        # Create a layout for the buttons and address bar
        toolbar_layout = QHBoxLayout()
        toolbar_layout.addWidget(self.back_button)
        toolbar_layout.addWidget(self.forward_button)
        toolbar_layout.addWidget(self.refresh_button)
        toolbar_layout.addWidget(self.home_button)
        toolbar_layout.addWidget(self.bookmark_button)  # Add bookmark button
        toolbar_layout.addWidget(self.address_bar)

        # Create a widget for the toolbar and set the layout
        toolbar_widget = QWidget()
        toolbar_widget.setLayout(toolbar_layout)

        # Create a toolbar and add the toolbar widget to it
        toolbar = QToolBar()
        toolbar.addWidget(toolbar_widget)

        # Add the toolbar to the main application window
        self.addToolBar(toolbar)

        # Set the QTabWidget as the central widget
        self.setCentralWidget(self.tab_widget)

        # Add a new tab when the "New Tab" button is clicked
        add_tab_button = QPushButton("New Tab")
        add_tab_button.clicked.connect(add_new_tab)
        toolbar.addWidget(add_tab_button)

        # Add right-click context menu for tabs
        self.tab_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tab_widget.customContextMenuRequested.connect(self.show_tab_context_menu)

        # Create a context menu for tabs
        self.tab_context_menu = QMenu(self)
        close_tab_action = QAction("Close Tab", self)
        close_tab_action.triggered.connect(self.close_current_tab)
        self.tab_context_menu.addAction(close_tab_action)

        # Create a bookmark menu
        self.bookmark_menu = QMenu("Bookmarks", self)
        self.bookmark_menu.aboutToShow.connect(self.update_bookmark_menu)

        # Add the bookmark menu to the toolbar
        toolbar.addWidget(self.bookmark_menu)

    def show_tab_context_menu(self, position):
        index = self.tab_widget.tabBar().tabAt(position)
        if index >= 0:
            self.tab_context_menu.popup(self.tab_widget.mapToGlobal(position))

    def close_current_tab(self):
        current_tab_index = self.tab_widget.currentIndex()
        self.tab_widget.removeTab(current_tab_index)

    def navigate_back(self):
        current_tab = self.tab_widget.currentWidget()
        if current_tab is not None:
            current_tab.back()

    def navigate_forward(self):
        current_tab = self.tab_widget.currentWidget()
        if current_tab is not None:
            current_tab.forward()

    def refresh_page(self):
        current_tab = self.tab_widget.currentWidget()
        if current_tab is not None:
            current_tab.reload()

    def go_home(self):
        self.browser.setUrl(QUrl("https://www.google.com"))  # Set your desired homepage URL

    def load_url(self):
        query = self.address_bar.text()
        if query:
            url = QUrl("https://www.google.com/search?q={}".format(query))
            current_tab = self.tab_widget.currentWidget()
            if current_tab is not None:
                current_tab.setUrl(url)

    def is_valid_url(self, url):
        return url.startswith("http://") or url.startswith("https://")

    def add_bookmark(self):
        current_tab = self.tab_widget.currentWidget()
        if current_tab is not None:
            title = current_tab.title()
            url = current_tab.url().toString()
            if title and url:
                bookmarks = current_tab.page().bookmarks
                if url not in bookmarks:
                    bookmarks[url] = title
                    QMessageBox.information(
                        self,
                        "Bookmark Added",
                        "Bookmark has been added successfully.",
                        QMessageBox.Ok,
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Bookmark Exists",
                        "The bookmark already exists.",
                        QMessageBox.Ok,
                    )

    def update_bookmark_menu(self):
        self.bookmark_menu.clear()
        bookmarks = self.tab_widget.currentWidget().page().bookmarks
        for url, title in bookmarks.items():
            action = QAction(title, self)
            action.setData(url)
            action.triggered.connect(self.load_bookmark)
            self.bookmark_menu.addAction(action)

    def load_bookmark(self):
        action = self.sender()
        if action is not None:
            url = QUrl(action.data())
            current_tab = self.tab_widget.currentWidget()
            if current_tab is not None:
                current_tab.setUrl(url)

    def update_tab_title(self, tab):
        index = self.tab_widget.indexOf(tab)
        title = tab.title()
        self.tab_widget.setTabText(index, title)

if __name__ == "__main__":
    # Create the QApplication
    app = QApplication(sys.argv)

    # Set the dark mode stylesheet
    app.setStyleSheet('''
        QMainWindow {
            background-color: #333333;
            color: #ffffff;
        }
        QTabBar {
            background-color: #222222;
            color: #ffffff;
        }
        QTabBar::tab {
            background-color: #444444;
            color: #ffffff;
        }
        QLineEdit {
            background-color: #555555;
            color: #ffffff;
        }
        QPushButton {
            background-color: #555555;
            color: #ffffff;
            border: none;
            padding: 5px;
        }
    ''')

    # Create an instance of the WebBrowser class
    browser = WebBrowser()

    # Show the browser window
    browser.show()

    # Enter the application event loop
    sys.exit(app.exec_())

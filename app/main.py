import os
import sys
from dotenv import load_dotenv, set_key
from PySide6 import QtWidgets


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ReciPython")

        # Load environment variables
        load_dotenv()
        self.api_key = os.getenv('API_KEY', 'API Key not set')

        # Create stacked widget (holds multiple pages)
        self.stacked_widget = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Create the pages
        self.menu_page = MenuPage(self)
        self.settings_page = SettingsPage(self)

        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.menu_page)
        self.stacked_widget.addWidget(self.settings_page)

    def show_menu_page(self):
        self.stacked_widget.setCurrentWidget(self.menu_page)

    def show_settings_page(self):
        self.stacked_widget.setCurrentWidget(self.settings_page)

    def update_api_key(self, new_key):
        self.api_key = new_key


class MenuPage(QtWidgets.QWidget):
    def __init__(self, parent_window):
        super().__init__()

        self.parent_window = parent_window

        # Create widget and layout
        layout = QtWidgets.QVBoxLayout()

        # Create buttons
        self.search_button = QtWidgets.QPushButton("Search")
        self.ingredients_button = QtWidgets.QPushButton("My Ingredients")
        self.favourites_button = QtWidgets.QPushButton("Favourites")
        self.settings_button = QtWidgets.QPushButton("Settings")
        self.exit_button = QtWidgets.QPushButton("Exit")

        # Connect the buttons to the functions
        self.search_button.clicked.connect(lambda: print(self.parent_window.api_key))  # Temp tester
        self.settings_button.clicked.connect(self.parent_window.show_settings_page)
        self.exit_button.clicked.connect(QtWidgets.QApplication.instance().quit)

        # Add buttons to layout
        layout.addWidget(self.search_button)
        layout.addWidget(self.ingredients_button)
        layout.addWidget(self.favourites_button)
        layout.addWidget(self.settings_button)
        layout.addWidget(self.exit_button)

        # Set widget layout
        self.setLayout(layout)


class SettingsPage(QtWidgets.QWidget):
    def __init__(self, parent_window):
        super().__init__()

        self.parent_window = parent_window

        # Create layout
        layout = QtWidgets.QVBoxLayout()

        # Create API key setting option
        self.api_key_label = QtWidgets.QLabel("API Key:")
        self.api_key_input = QtWidgets.QLineEdit()

        # Create buttons
        self.back_button = QtWidgets.QPushButton("Back")
        self.save_button = QtWidgets.QPushButton("Save")

        # Connect buttons
        self.back_button.clicked.connect(self.parent_window.show_menu_page)
        self.save_button.clicked.connect(self.save_settings)

        # Add widgets to layout
        layout.addWidget(self.api_key_label)
        layout.addWidget(self.api_key_input)
        layout.addWidget(self.back_button)
        layout.addWidget(self.save_button)

        # Set layout
        self.setLayout(layout)

    def save_settings(self):
        api_key = self.api_key_input.text()
        set_key('.env', 'API_KEY', api_key)
        self.parent_window.update_api_key(api_key)
        QtWidgets.QMessageBox.information(self, "Settings", "API Key saved successfully.",
                                          QtWidgets.QMessageBox.StandardButton.Ok)


if __name__ == '__main__':
    # Create the Qt Application
    app = QtWidgets.QApplication(sys.argv)

    # Create an instance of the main window
    window = MainWindow()
    window.show()

    # Start the main event loop (will start app, then sys.exit when app loop is done)
    sys.exit(app.exec())

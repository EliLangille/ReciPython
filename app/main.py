import sys
from PySide6 import QtWidgets


class MenuWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ReciPython")

        # Create layout
        layout = QtWidgets.QVBoxLayout()

        # Create buttons
        self.search_button = QtWidgets.QPushButton("Search")
        self.ingredients_button = QtWidgets.QPushButton("My Ingredients")
        self.favourites_button = QtWidgets.QPushButton("Favourites")
        self.settings_button = QtWidgets.QPushButton("Settings")
        self.quit_button = QtWidgets.QPushButton("Quit")

        # Connect the buttons to the functions
        # ...

        # Add buttons to layout
        layout.addWidget(self.search_button)
        layout.addWidget(self.ingredients_button)
        layout.addWidget(self.favourites_button)
        layout.addWidget(self.settings_button)
        layout.addWidget(self.quit_button)

        # Set the central widget
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)


if __name__ == '__main__':
    # Create the Qt Application
    app = QtWidgets.QApplication(sys.argv)

    # Create an instance of the main window
    window = MenuWindow()
    window.show()

    # Start the main event loop (will start app, then sys.exit when app loop is done)
    sys.exit(app.exec())

import os
import pprint
import sys
import threading
import time
import requests as req
from dotenv import load_dotenv, set_key
from PySide6 import QtWidgets, QtCore


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
        self.search_page = SearchPage(self)
        self.settings_page = SettingsPage(self)

        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.menu_page)
        self.stacked_widget.addWidget(self.search_page)
        self.stacked_widget.addWidget(self.settings_page)

    def show_menu_page(self):
        self.stacked_widget.setCurrentWidget(self.menu_page)

    def show_search_page(self):
        self.stacked_widget.setCurrentWidget(self.search_page)

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
        self.search_button.clicked.connect(self.parent_window.show_search_page)
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


class SearchPage(QtWidgets.QWidget):
    def __init__(self, parent_window):
        super().__init__()

        self.parent_window = parent_window

        # Create layout
        layout = QtWidgets.QVBoxLayout()

        # Create back button
        self.back_button = QtWidgets.QPushButton("Back")

        # Create search bar and button
        self.search_bar = QtWidgets.QLineEdit()
        self.search_button = QtWidgets.QPushButton("Search")

        # Connect buttons
        self.back_button.clicked.connect(self.parent_window.show_menu_page)
        self.search_button.clicked.connect(self.search_recipes)

        # Temp label to display ingredients after search
        self.results_label = QtWidgets.QLabel()
        self.results_label.setTextFormat(QtCore.Qt.TextFormat.RichText)
        self.results_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextBrowserInteraction)
        self.results_label.setOpenExternalLinks(True)
        self.results_label.setText("")  # Initialize with empty content

        # Add widgets to layout
        layout.addWidget(self.search_bar)
        layout.addWidget(self.search_button)
        layout.addWidget(self.results_label)
        layout.addWidget(self.back_button)

        # Set layout
        self.setLayout(layout)

    def search_recipes(self):
        # Clear the results label before updating it
        self.results_label.setText("")

        # Update results label to pending
        self.results_label.setText("Searching...")

        # Start a new thread to perform the API requests
        threading.Thread(target=self.perform_search).start()

    def perform_search(self):
        # Get and clean ingredients list from search bar
        ingredients = [ingredient.strip() for ingredient in self.search_bar.text().split(',')]
        ingredients = ','.join(ingredients)

        # Format API request
        url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/findByIngredients"
        querystring = {"ingredients": ingredients, "number": "5", "ignorePantry": "true", "ranking": "1"}
        headers = {
            "x-rapidapi-key": self.parent_window.api_key,
            "x-rapidapi-host": "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"
        }

        # Make and get API request
        response = req.request("GET", url, headers=headers, params=querystring)

        if response.status_code == 200:
            recipes = response.json()
            recipe_names = [recipe['title'] for recipe in recipes]
            recipe_ids = [recipe['id'] for recipe in recipes]

            # Rate limit adherence
            time.sleep(1)

            # Get recipe links
            recipe_links = []
            for recipe_id in recipe_ids:
                time.sleep(0.5)
                recipe_info_url = (f"https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"
                                   f"/recipes/{recipe_id}/information")
                recipe_info_response = req.request("GET", recipe_info_url, headers=headers)
                if recipe_info_response.status_code == 200:
                    recipe_info = recipe_info_response.json()
                    recipe_links.append(recipe_info.get('sourceUrl', ''))

            # Display recipe names and links
            recipes_display = "<br>".join(
                [f"<a href='{link}'>{name}</a>" if link else name for name, link in zip(recipe_names, recipe_links)]
            )
            self.update_results_label(f"Recipes found:<br>{recipes_display}")
        else:
            self.update_results_label("Error: Unable to retrieve recipes.")

    def update_results_label(self, text):
        self.results_label.setText(text)


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

import os
import sys
import threading
import time
import requests as req
from dotenv import load_dotenv, set_key
from PySide6 import QtWidgets, QtCore


class FilterDropdown(QtWidgets.QPushButton):
    def __init__(self, parent=None):
        super().__init__("Filters", parent)
        self.setMenu(QtWidgets.QMenu(self))

        # Create QListWidget and add it to the QMenu
        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.MultiSelection)
        self.list_widget.addItems([
            "Appetizer", "Beverage", "Breakfast", "Bread", "Dessert", "Dinner", "Drink", "Fingerfood", "Lunch",
            "Main Course", "Marinade", "Salad", "Sauce", "Side", "Snack", "Soup"
        ])

        # Create a QWidgetAction to hold the QListWidget
        action = QtWidgets.QWidgetAction(self)
        action.setDefaultWidget(self.list_widget)
        self.menu().addAction(action)

        # Create buttons for quick actions
        self.all_button = QtWidgets.QPushButton("All")
        self.meals_button = QtWidgets.QPushButton("Meals")
        self.clear_button = QtWidgets.QPushButton("Clear")

        # Add buttons to a layout
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.all_button)
        button_layout.addWidget(self.meals_button)
        button_layout.addWidget(self.clear_button)

        # Add button layout to a widget
        button_widget = QtWidgets.QWidget()
        button_widget.setLayout(button_layout)

        # Add layout to a QWidgetAction
        button_action = QtWidgets.QWidgetAction(self)
        button_action.setDefaultWidget(button_widget)
        self.menu().addAction(button_action)

        # Connect buttons to functions
        self.all_button.clicked.connect(self.select_all)
        self.meals_button.clicked.connect(self.select_meals)
        self.clear_button.clicked.connect(self.list_widget.clearSelection)

    def select_all(self):
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            item.setSelected(True)

    def select_meals(self):
        # Select main course, side dish, appetizer, breakfast, appetizer, salad, soup
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            text = item.text()
            if text in ["Appetizer", "Breakfast", "Main Course", "Salad", "Side", "Soup"]:
                item.setSelected(True)
            else:
                item.setSelected(False)

    def selected_items(self):
        # Set to lowercase
        return [item.text().lower() for item in self.list_widget.selectedItems()]


class StackedWidget(QtWidgets.QStackedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.currentChanged.connect(self.update_size)

    def sizeHint(self):
        current_widget = self.currentWidget()
        if current_widget:
            return current_widget.sizeHint()
        return super().sizeHint()

    def minimumSizeHint(self):
        current_widget = self.currentWidget()
        if current_widget:
            return current_widget.minimumSizeHint()
        return super().minimumSizeHint()

    def update_size(self):
        self.parentWidget().adjustSize()


class MainWindow(QtWidgets.QMainWindow):
    # Constants
    MIN_SIZE = (300, 225)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("ReciPython")

        # Load environment variables
        load_dotenv()
        self.api_key = os.getenv('API_KEY', 'API Key not set')

        # Create stacked widget (holds multiple pages)
        self.stacked_widget = StackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Create the pages
        self.menu_page = MenuPage(self)
        self.search_page = SearchPage(self)
        self.settings_page = SettingsPage(self)

        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.menu_page)
        self.stacked_widget.addWidget(self.search_page)
        self.stacked_widget.addWidget(self.settings_page)

        # Set initial page to menu page
        self.show_menu_page()

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

        # Create filter dropdown
        self.filter_dropdown = FilterDropdown()

        # Connect buttons
        self.back_button.clicked.connect(self.parent_window.show_menu_page)
        self.search_button.clicked.connect(self.search_recipes)

        # Label to display ingredients after search
        self.results_label = QtWidgets.QLabel()
        self.results_label.setTextFormat(QtCore.Qt.TextFormat.RichText)
        self.results_label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextBrowserInteraction)
        self.results_label.setOpenExternalLinks(True)
        self.results_label.setText("")  # Initialize with empty content

        # Add widgets to layout
        layout.addWidget(self.search_bar)
        layout.addWidget(self.filter_dropdown)
        layout.addWidget(self.search_button)
        layout.addWidget(self.results_label)
        layout.addWidget(self.back_button)

        # Set layout
        self.setLayout(layout)

    def search_recipes(self):
        # Update results label to pending
        self.results_label.setText("Searching...")

        # Start a new thread to perform the API requests
        threading.Thread(target=self.perform_search).start()

    def perform_search(self):
        # Get and clean ingredients list from search bar
        ingredients = [ingredient.strip() for ingredient in self.search_bar.text().split(',')]
        ingredients = ','.join(ingredients)

        # Format API request
        recipes_url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/findByIngredients"
        querystring = {"ingredients": ingredients, "number": "5", "ignorePantry": "true", "ranking": "1"}
        headers = {
            "x-rapidapi-key": self.parent_window.api_key,
            "x-rapidapi-host": "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"
        }

        # Add selected type filters to the querystring
        filters = self.filter_dropdown.selected_items()
        if filters:
            querystring['type'] = ','.join(filters)

        # POST recipes search request
        recipes_response = req.request("GET", recipes_url, headers=headers, params=querystring)

        # If request successful, get and show recipes' info
        if recipes_response.status_code == 200:
            # Clean recipes data
            recipes = recipes_response.json()
            recipe_ids = [recipe['id'] for recipe in recipes]

            # POST recipes' info request
            info_bulk_url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/informationBulk"
            info_bulk_querystring = {"ids": ",".join(map(str, recipe_ids)), "includeNutrition": "true"}
            info_bulk_response = req.request("GET", info_bulk_url, headers=headers, params=info_bulk_querystring)

            # If request successful, get and show recipes' info
            if info_bulk_response.status_code == 200:
                recipes_info = info_bulk_response.json()
                self.update_results_label(recipes_info)

                print(recipes)
                print()
                print(recipes_info)
                print("\n")
            # Else, show error message
            else:
                self.update_results_label("Error: Unable to retrieve recipes' info.")
        # Else, show error message
        else:
            self.update_results_label("Error: Unable to retrieve recipes.")

    # Update results label with recipe cards using recipe info from API
    def update_results_label(self, recipes_info):
        # If the recipes_info is a string, then it's an error message
        if isinstance(recipes_info, str):
            self.results_label.setText(recipes_info)
            return

        cards_html = ""

        # Create card for each recipe
        for recipe in recipes_info:
            # Extract basic recipe info
            name = recipe.get('title', 'No title')
            source = recipe.get('sourceName', 'No source')
            ready_in_minutes = recipe.get('readyInMinutes', 'Unknown ready time')
            servings = recipe.get('servings', 'Unknown servings')
            url = recipe.get('sourceUrl', '#')

            # Extract from nutrition info to get calories, fat, carbs, and protein
            nutrition_info = {nutrient['name']: nutrient['amount'] for nutrient in
                              recipe.get('nutrition', {}).get('nutrients', [])}
            calories = nutrition_info.get('Calories', '')
            fat = nutrition_info.get('Fat', '')
            carbs = nutrition_info.get('Carbohydrates', '')
            protein = nutrition_info.get('Protein', '')

            # Add g to the end of the values if they exist else make them a ?
            calories = f"{calories}kcal" if calories else '?'
            fat = f"{fat}g" if fat else '?'
            carbs = f"{carbs}g" if carbs else '?'
            protein = f"{protein}g" if protein else '?'

            # Create card for recipe
            card_html = f"""
            <div style="border: 1px solid black; padding: 10px; margin: 10px;">
                <h2>{name}</h2>
                <p>Source: {source}</p>
                <p>Ready in: {ready_in_minutes} minutes</p>
                <p>Servings: {servings}</p>
                <p>Nutrition: {calories}, {fat} fat, {carbs} carbs, {protein} protein</p>
                <p><a href="{url}">Link to recipe</a></p>
            </div>
            """
            cards_html += card_html

        # Update results label with recipe cards
        self.results_label.setText(cards_html)


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

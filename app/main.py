import os
import sqlite3
import sys
import requests as req
from dotenv import load_dotenv, set_key
from PySide6 import QtWidgets

# Constants
MIN_CARD_HEIGHT = 250
MIN_CARD_WIDTH = 425

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
        self.meals_button = QtWidgets.QPushButton("Meals")
        self.drinks_button = QtWidgets.QPushButton("Drinks")
        self.clear_button = QtWidgets.QPushButton("Clear")

        # Add buttons to a layout
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.meals_button)
        button_layout.addWidget(self.drinks_button)
        button_layout.addWidget(self.clear_button)

        # Add button layout to a widget
        button_widget = QtWidgets.QWidget()
        button_widget.setLayout(button_layout)

        # Add layout to a QWidgetAction
        button_action = QtWidgets.QWidgetAction(self)
        button_action.setDefaultWidget(button_widget)
        self.menu().addAction(button_action)

        # Connect buttons to functions
        self.meals_button.clicked.connect(self.select_meals)
        self.drinks_button.clicked.connect(self.select_drinks)
        self.clear_button.clicked.connect(self.list_widget.clearSelection)

    def select_meals(self):
        # Select meal-related filters
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            text = item.text()
            if text in ["Appetizer", "Breakfast", "Dinner", "Lunch", "Main Course", "Salad", "Soup"]:
                item.setSelected(True)
            else:
                item.setSelected(False)

    def select_drinks(self):
        # Select drink-related filters
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            text = item.text()
            if text in ["Beverage", "Drink"]:
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
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ReciPython")

        # Load environment variables
        load_dotenv()
        self.api_key = os.getenv('API_KEY', 'API Key not set')

        # Initialize recipes database
        self.conn = sqlite3.connect('recipython.db')
        self.init_database()

        # Create stacked widget (holds multiple pages)
        self.stacked_widget = StackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Create the pages
        self.menu_page = MenuPage(self)
        self.search_page = SearchPage(self)
        self.favourites_page = FavouritesPage(self)
        self.settings_page = SettingsPage(self)

        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.menu_page)
        self.stacked_widget.addWidget(self.search_page)
        self.stacked_widget.addWidget(self.favourites_page)
        self.stacked_widget.addWidget(self.settings_page)

        # Set initial page to menu page
        self.show_menu_page()

    def init_database(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS favourites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    source TEXT,
                    ready_in_minutes TEXT,
                    servings TEXT,
                    calories TEXT,
                    fat TEXT,
                    carbs TEXT,
                    protein TEXT,
                    url TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ingredients TEXT,
                    filters TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.conn.commit()
            print("Database tables created successfully.")
        except sqlite3.Error as e:
            print(f"Error creating database tables: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", "Failed to create database tables.",
                                           QtWidgets.QMessageBox.StandardButton.Ok)
            return
        except Exception as e:
            print(f"Unexpected error: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", "An unexpected error occurred.",
                                           QtWidgets.QMessageBox.StandardButton.Ok)
            return

    def show_menu_page(self):
        self.stacked_widget.setCurrentWidget(self.menu_page)

    def show_search_page(self):
        self.stacked_widget.setCurrentWidget(self.search_page)

    # def show_history_page(self):
    #     self.stacked_widget.setCurrentWidget(self.history_page)

    def show_favourites_page(self):
        self.stacked_widget.setCurrentWidget(self.favourites_page)

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
        self.history_button = QtWidgets.QPushButton("History")
        self.favourites_button = QtWidgets.QPushButton("Favourites")
        self.settings_button = QtWidgets.QPushButton("Settings")
        self.exit_button = QtWidgets.QPushButton("Exit")

        # Connect the buttons to the functions
        self.search_button.clicked.connect(self.parent_window.show_search_page)
        # self.history_button.clicked.connect(self.parent_window.show_history_page)
        self.favourites_button.clicked.connect(lambda: (self.parent_window.favourites_page.load_favourites(),
                                                        self.parent_window.show_favourites_page()))
        self.settings_button.clicked.connect(self.parent_window.show_settings_page)
        self.exit_button.clicked.connect(QtWidgets.QApplication.instance().quit)

        # Add buttons to layout
        layout.addWidget(self.search_button)
        layout.addWidget(self.history_button)
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

        # Label to display search status or errors
        self.status_label = QtWidgets.QLabel()
        self.status_label.setText("")

        # Create scroll area for recipe cards
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumHeight(MIN_CARD_HEIGHT)
        self.scroll_area.setMinimumWidth(MIN_CARD_WIDTH)
        self.scroll_content = QtWidgets.QWidget()
        self.scroll_layout = QtWidgets.QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)

        # Add widgets to layout
        layout.addWidget(self.search_bar)
        layout.addWidget(self.filter_dropdown)
        layout.addWidget(self.search_button)
        layout.addWidget(self.status_label)
        layout.addWidget(self.scroll_area)
        layout.addWidget(self.back_button)

        # Set layout
        self.setLayout(layout)

    def search_recipes(self):
        # Update results label to pending
        self.status_label.setText("Searching...")

        # Get and clean ingredients list from search bar
        ingredients = [ingredient.strip() for ingredient in self.search_bar.text().split(',')]
        ingredients = ','.join(ingredients)

        # Store search data for history
        search_data = {'ingredients': ingredients}

        # Format API request
        recipes_url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/findByIngredients"
        querystring = {"ingredients": ingredients, "number": "5", "ignorePantry": "true", "ranking": "1"}
        headers = {
            "x-rapidapi-key": self.parent_window.api_key,
            "x-rapidapi-host": "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"
        }

        # Add filters to query string and search history entry
        filters = self.filter_dropdown.selected_items()
        if filters:
            querystring['type'] = ','.join(filters)
            search_data['filters'] = filters
        else:
            search_data['filters'] = []

        # Save search data to database
        self.save_search_data(search_data)

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
                self.update_results(recipes_info)

                print(recipes)
                print()
                print(recipes_info)
                print("\n")
            # Else, show error message
            else:
                self.status_label.setText("Error: Unable to retrieve recipes' info.")
                print(f"Error: {info_bulk_response.status_code} - {info_bulk_response.text}")
        # Else, show error message
        else:
            self.status_label.setText("Error: Unable to retrieve recipes.")
            print(f"Error: {recipes_response.status_code} - {recipes_response.text}")

    # Update results label with recipe cards using recipe info from API
    def update_results(self, recipes_info):
        # Clear results label
        self.status_label.setText("")

        # Clear existing cards
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Add new card for each recipe
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

            # Create a dictionary to hold recipe data for adding to favourites if needed
            recipe_data = {
                'name': name,
                'source': source,
                'ready_in_minutes': ready_in_minutes,
                'servings': servings,
                'calories': calories,
                'fat': fat,
                'carbs': carbs,
                'protein': protein,
                'url': url
            }

            # Create card for recipe
            card = QtWidgets.QWidget()
            card_layout = QtWidgets.QVBoxLayout(card)

            # Add recipe details
            card_layout.addWidget(QtWidgets.QLabel(f"<b>{name}</b>"))
            card_layout.addWidget(QtWidgets.QLabel(f"Source: {source}"))
            card_layout.addWidget(QtWidgets.QLabel(f"Ready in: {ready_in_minutes} minutes"))
            card_layout.addWidget(QtWidgets.QLabel(f"Servings: {servings}"))
            card_layout.addWidget(QtWidgets.QLabel(f"Nutrition: {calories}, {fat} fat, {carbs} carbs, "
                                                   f"{protein} protein"))
            link_label = QtWidgets.QLabel(f'<a href="{url}">View Recipe</a>')
            link_label.setOpenExternalLinks(True)
            card_layout.addWidget(link_label)

            # Add button to add to favourites
            add_fav_button = QtWidgets.QPushButton("Add to Favourites")
            add_fav_button.clicked.connect(lambda _, r=recipe_data: self.add_to_favourites(r))
            card_layout.addWidget(add_fav_button)

            # Add card to cards layout
            self.scroll_layout.addWidget(card)

    def save_search_data(self, search_data):
        try:
            cursor = self.parent_window.conn.cursor()

            # Insert search data into the database
            cursor.execute("""
                INSERT INTO search_history (ingredients, filters)
                VALUES (?, ?)
            """, (search_data['ingredients'], ','.join(search_data['filters'])))

            # Delete older entries to limit search history to 20
            cursor.execute("""
                DELETE FROM search_history
                WHERE id NOT IN (
                    SELECT id FROM search_history
                    ORDER BY timestamp DESC
                    LIMIT 20
                )
            """)

            # Commit the changes
            self.parent_window.conn.commit()
        except sqlite3.Error as e:
            print(f"Error saving search data: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", "Failed to save search data.",
                                           QtWidgets.QMessageBox.StandardButton.Ok)
            return
        except Exception as e:
            print(f"Unexpected error: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", "An unexpected error occurred.",
                                           QtWidgets.QMessageBox.StandardButton.Ok)
            return

    def add_to_favourites(self, recipe_data):
        try:
            cursor = self.parent_window.conn.cursor()

            # Check if the recipe already exists in the favourites table
            cursor.execute("""
                SELECT * FROM favourites 
                WHERE name = ? AND source = ? AND url = ?
            """, (
                recipe_data['name'],
                recipe_data['source'],
                recipe_data['url']
            ))

            # If match found, show error message and return
            if cursor.fetchone():
                QtWidgets.QMessageBox.warning(self, "Error", "Recipe already in favourites.",
                                              QtWidgets.QMessageBox.StandardButton.Ok)
                return

            # Save the recipe data to the database
            cursor.execute("""
                INSERT INTO favourites (name, source, ready_in_minutes, servings, calories, fat, carbs, protein, 
                url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                recipe_data['name'],
                recipe_data['source'],
                recipe_data['ready_in_minutes'],
                recipe_data['servings'],
                recipe_data['calories'],
                recipe_data['fat'],
                recipe_data['carbs'],
                recipe_data['protein'],
                recipe_data['url']
            ))
            self.parent_window.conn.commit()
        except sqlite3.Error as e:
            print(f"Error saving recipe to favourites: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", "Failed to save recipe to favourites.",
                                           QtWidgets.QMessageBox.StandardButton.Ok)
            return
        except Exception as e:
            print(f"Unexpected error: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", "An unexpected error occurred.",
                                           QtWidgets.QMessageBox.StandardButton.Ok)
            return

        # Show success message
        QtWidgets.QMessageBox.information(self, "Favourites", "Recipe added to favourites.",
                                          QtWidgets.QMessageBox.StandardButton.Ok)


class FavouritesPage(QtWidgets.QWidget):
    def __init__(self, parent_window):
        super().__init__()

        self.parent_window = parent_window

        # Create layout
        layout = QtWidgets.QVBoxLayout()

        # Create back button
        self.back_button = QtWidgets.QPushButton("Back")
        self.back_button.clicked.connect(self.parent_window.show_menu_page)

        # Create scroll area for favourites
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumHeight(MIN_CARD_HEIGHT)
        self.scroll_area.setMinimumWidth(MIN_CARD_WIDTH)
        self.scroll_content = QtWidgets.QWidget()
        self.scroll_layout = QtWidgets.QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)

        # Add widgets to layout
        layout.addWidget(self.scroll_area)
        layout.addWidget(self.back_button)

        # Set layout
        self.setLayout(layout)

        # Load favourites from database
        self.load_favourites()

    def load_favourites(self):
        # Clear existing cards
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Fetch favourites from the database
        try:
            cursor = self.parent_window.conn.cursor()
            cursor.execute("SELECT * FROM favourites")
            favourites = cursor.fetchall()

            for recipe in favourites:
                print(recipe)
                name, source, ready_in_minutes, servings, calories, fat, carbs, protein, url = recipe[1:]

                # Create a card for each favourite recipe
                card = QtWidgets.QWidget()
                card_layout = QtWidgets.QVBoxLayout(card)

                # Add recipe details
                card_layout.addWidget(QtWidgets.QLabel(f"<b>{name}</b>"))
                card_layout.addWidget(QtWidgets.QLabel(f"Source: {source}"))
                card_layout.addWidget(QtWidgets.QLabel(f"Ready in: {ready_in_minutes} minutes"))
                card_layout.addWidget(QtWidgets.QLabel(f"Servings: {servings}"))
                card_layout.addWidget(QtWidgets.QLabel(f"Nutrition: {calories}, {fat} fat, {carbs} carbs, "
                                                       f"{protein} protein"))
                link_label = QtWidgets.QLabel(f'<a href="{url}">View Recipe</a>')
                link_label.setOpenExternalLinks(True)
                card_layout.addWidget(link_label)

                # Add button to remove from favourites
                remove_button = QtWidgets.QPushButton("Remove from Favourites")
                remove_button.clicked.connect(lambda _, r=recipe: self.remove_from_favourites(r))
                card_layout.addWidget(remove_button)

                # Add card to scroll layout
                self.scroll_layout.addWidget(card)
        except sqlite3.Error as e:
            print(f"Error loading favourites: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", "Failed to load favourites.",
                                           QtWidgets.QMessageBox.StandardButton.Ok)
            return
        except Exception as e:
            print(f"Unexpected error: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", "An unexpected error occurred.",
                                           QtWidgets.QMessageBox.StandardButton.Ok)
            return

    def remove_from_favourites(self, recipe):
        try:
            cursor = self.parent_window.conn.cursor()

            # Remove the recipe from the database
            cursor.execute("""
                DELETE FROM favourites 
                WHERE name = ? AND source = ? AND url = ?
            """, (
                recipe[1],
                recipe[2],
                recipe[9]
            ))
            self.parent_window.conn.commit()
        except sqlite3.Error as e:
            print(f"Error removing recipe from favourites: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", "Failed to remove recipe from favourites.",
                                           QtWidgets.QMessageBox.StandardButton.Ok)
            return
        except Exception as e:
            print(f"Unexpected error: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", "An unexpected error occurred.",
                                           QtWidgets.QMessageBox.StandardButton.Ok)
            return

        # Reload favourites
        self.load_favourites()

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

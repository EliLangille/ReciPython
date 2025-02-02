def menu(name):
    print("1. Search \n2. My Ingredients \n3. Favourites \n4. Settings \n5. Quit")

    try:
        choice = int(input("Enter your choice: "))
        match choice:
            case 1:
                pass
            case 2:
                pass
            case 3:
                pass
            case 4:
                pass
            case 5:
                pass
            case _:
                print("Invalid input. Please enter a number between 1 and 5.")
                menu(name)
    except ValueError:
        print("Invalid input. Please enter a number between 1 and 5.")
        menu(name)


if __name__ == 'main':
    menu()

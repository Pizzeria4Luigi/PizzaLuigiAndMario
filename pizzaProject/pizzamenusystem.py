import os
import json

menu = {
    1: {"name": "Margherita", "price": 10, "ingredients": {"dough": 1, "tomato sauce": 1, "cheese": 1}},
    2: {"name": "Pepperoni", "price": 12, "ingredients": {"dough": 1, "tomato sauce": 1, "cheese": 1, "pepperoni": 1}},
    3: {"name": "Quattro Formaggi", "price": 13, "ingredients": {"dough": 1, "tomato sauce": 1, "cheese": 4}},
    4: {"name": "Mario's Madness", "price": 15, "ingredients": {"dough": 1, "tomato sauce": 1, "cheese": 1, "pepperoni": 1, "mushrooms": 1, "ham": 1}},
    5: {"name": "Luigi's Baloney", "price": 14, "ingredients": {"dough": 1, "tomato sauce": 1, "cheese": 1, "sausage": 1}},
    6: {"name": "Bowser Buns", "price": 7, "ingredients": {"dough": 1}}
}

file_path = os.path.join(os.path.dirname(__file__), "ingredients.txt")
current_order_path = os.path.join(os.path.dirname(__file__), "currentOrder.txt")

ingredient_stock = {}

def load_ingredient_stock():
    try:
        with open(file_path, "r") as file:
            for line in file:
                ingredient, quantity = line.strip().split(":")
                ingredient_stock[ingredient] = int(quantity)
    except FileNotFoundError:
        print("Ingredients file not found. Using default quantities.")

def save_ingredient_stock():
    with open(file_path, "w") as file:
        for ingredient, quantity in ingredient_stock.items():
            file.write(f"{ingredient}:{quantity}\n")

def display_menu():
    print("\nPizza Menu:\n")
    for item, pizza in menu.items():
        print(f"{item}. {pizza['name']} - ${pizza['price']}")

def update_stock(ingredient, quantity):
    if ingredient in ingredient_stock and ingredient_stock[ingredient] >= quantity:
        ingredient_stock[ingredient] -= quantity
        save_ingredient_stock()
    else:
        print(f"Sorry, we are out of {ingredient} or the requested quantity is not available.")
        return False
    return True

def check_pizza_ingredients(pizza):
    for ingredient, quantity in pizza['ingredients'].items():
        if ingredient not in ingredient_stock or ingredient_stock[ingredient] < quantity:
            print(f"OUT OF STOCK: {pizza['name']} - Missing {quantity} units of {ingredient}")
            return False
    return True

def take_order():
    order = []

    try:
        with open(current_order_path, "r") as order_file:
            order_data = json.load(order_file)

        for pizza_name, quantity in order_data.items():
            for item, pizza in menu.items():
                if pizza['name'] == pizza_name:
                    selected_pizza = pizza
                    if check_pizza_ingredients(selected_pizza):
                        for ingredient, required_quantity in selected_pizza['ingredients'].items():
                            update_stock(ingredient, required_quantity * quantity)
                        selected_pizza['quantity'] = quantity
                        order.append(selected_pizza)

    except FileNotFoundError:
        print("Order file not found. No items added to the order.")

    if not order:
        print("\nNo items in your order.")
        return

    print("\nYour Order:")
    total_price = 0
    for item in order:
        if item['quantity'] > 0:
            print(f"{item['name']} - Quantity: {item['quantity']} - ${item['price']} each")
            total_price += item['price'] * item['quantity']
    print(f"Total Price: ${total_price}")

if __name__ == "__main__":
    print("\nWelcome to Pizzeria di Mario e Luigi!")
    load_ingredient_stock()
    display_menu()
    take_order()
    print("\nThank you for your order. Enjoy your pizza!")

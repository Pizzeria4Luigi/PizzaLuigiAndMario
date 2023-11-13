import os
import json

import requests

import pip._vendor.requests

# Define global variables and data structures
menu = {
    1: {"name": "Margherita", "price": 10, "ingredients": {"dough": 1, "tomato sauce": 1, "cheese": 1}},
    2: {"name": "Pepperoni", "price": 12, "ingredients": {"dough": 1, "tomato sauce": 1, "cheese": 1, "pepperoni": 1}},
    3: {"name": "Quattro Formaggi", "price": 13, "ingredients": {"dough": 1, "tomato sauce": 1, "cheese": 4}},
    4: {"name": "Mario's Madness", "price": 15, "ingredients": {"dough": 1, "tomato sauce": 1, "cheese": 1, "pepperoni": 1, "mushrooms": 1, "ham": 1}},
    5: {"name": "Luigi's Baloney", "price": 14, "ingredients": {"dough": 1, "tomato sauce": 1, "cheese": 1, "sausage": 1}},
    6: {"name": "Bowser Buns", "price": 7, "ingredients": {"dough": 1}}
}

ingredient_stock = {}

file_path = os.path.join(os.path.dirname(__file__), "ingredients.txt")
current_order_path = os.path.join(os.path.dirname(__file__), "currentOrder.json")
order_log_path = os.path.join(os.path.dirname(__file__), "orderLog.txt")

ingredients_file = os.path.join(os.path.dirname(__file__), "ingredients.txt")
pizza_availability_file = os.path.join(os.path.dirname(__file__), "pizzaAvailability.txt")

def load_ingredient_stock():
    try:
        with open(ingredients_file, "r") as file:
            for line in file:
                ingredient, quantity = line.strip().split(":")
                ingredient_stock[ingredient] = int(quantity)
    except FileNotFoundError:
        print("Ingredients file not found. Using default quantities.")

def update_pizza_availability():
    with open(pizza_availability_file, "w") as file:
        for item, pizza in menu.items():
            available = True
            for ingredient, quantity in pizza['ingredients'].items():
                if ingredient not in ingredient_stock or ingredient_stock[ingredient] < quantity:
                    available = False
                    break
            file.write(f"{item}:{'True' if available else 'False'}\n")


def send_data():
    with open( pizza_availability_file, 'r') as file:
        pizzaStatus = {}
        for line in file:
            pizza_id, availability = line.strip().split(':')
            pizzaStatus[pizza_id.strip()] = availability.strip() == 'True'

    print(pizzaStatus)  # Add this line to check if pizzaStatus is correctly constructed

    response = requests.post('http://localhost:5000/pizzaStatus', json=pizzaStatus)
    
    print(response.text)  # Add this line to check the response from your Flask application

load_ingredient_stock()

# Update pizza availability
update_pizza_availability()

send_data()

# Display pizza availability
with open(pizza_availability_file, "r") as file:
    for line in file:
        item, available = line.strip().split(":")
        item_name = menu[int(item)]['name']
        print(f"{item_name} - Available: {available}")

'''       
def load_ingredient_stock():
    try:
        with open(file_path, "r") as file:
            for line in file:
                ingredient, quantity = line.strip().split(":")
                ingredient_stock[ingredient] = int(quantity)
    except FileNotFoundError:
        print("Ingredients file not found. Using default quantities.")
'''

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

def take_order(table_id):
    order = []

    try:
        with open(current_order_path, "r") as order_file:
            order_data = json.load(order_file)
            if table_id < len(order_data):
                table_order = order_data[table_id]
                for pizza_name, quantity in table_order.items():
                    for index, pizza in menu.items():
                        if pizza['name'] == pizza_name:
                            selected_pizza = pizza
                            choice = index
                            if choice in menu:
                                if check_pizza_ingredients(selected_pizza):
                                    for ingredient, required_quantity in selected_pizza['ingredients'].items():
                                        update_stock(ingredient, required_quantity * quantity)
                                    selected_pizza['quantity'] = quantity
                                    order.append(selected_pizza)
                                    break

    except FileNotFoundError:
        print(f"Order file not found for Table {table_id + 1}. No items added to the order.")

    if not order:
        print(f"\nNo items in the order for Table {table_id + 1}.")
        return

    print(f"\nOrder for Table {table_id + 1}:")
    total_price = 0
    for item in order:
        if item['quantity'] > 0:
            print(f"{item['name']} - Quantity: {item['quantity']} - ${item['price']} each")
            total_price += item['price'] * item['quantity']
    print(f"Total Price: ${total_price}")
    log_order(table_id, order, total_price)

def log_order(table_id, order, total_price):
    with open(order_log_path, "a") as log_file:
        log_file.write(f"Table {table_id + 1} Order:\n")
        for item in order:
            log_file.write(f"{item['name']} - Quantity: {item['quantity']} - ${item['price']} each\n")
        log_file.write(f"Total Price: ${total_price}\n")
        log_file.write("\n")



if __name__ == "__main__":
    print("\nWelcome to Pizzeria di Mario e Luigi!")
    load_ingredient_stock()
    display_menu()

    # Process the order for each table and log the orders
    for table_id in range(4):
        take_order(table_id)

    print("Thank you for your orders. Enjoy your pizza!")



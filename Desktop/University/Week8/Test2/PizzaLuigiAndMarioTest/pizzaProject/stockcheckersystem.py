import os

menu = {
    1: {"name": "Margherita", "price": 10, "ingredients": {"dough": 1, "tomato sauce": 1, "cheese": 1}},
    2: {"name": "Pepperoni", "price": 12, "ingredients": {"dough": 1, "tomato sauce": 1, "cheese": 1, "pepperoni": 1}},
    3: {"name": "Quattro Formaggi", "price": 13, "ingredients": {"dough": 1, "tomato sauce": 1, "cheese": 4}},
    4: {"name": "Mario's Madness", "price": 15, "ingredients": {"dough": 1, "tomato sauce": 1, "cheese": 1, "pepperoni": 1, "mushrooms": 1, "ham": 1}},
    5: {"name": "Luigi's Baloney", "price": 14, "ingredients": {"dough": 1, "tomato sauce": 1, "cheese": 1, "sausage": 1}},
    6: {"name": "Bowser Buns", "price": 7, "ingredients": {"dough": 1}}
}

ingredients_file = os.path.join(os.path.dirname(__file__), "ingredients.txt")
pizza_availability_file = os.path.join(os.path.dirname(__file__), "pizzaAvailability.txt")

ingredient_stock = {}

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

load_ingredient_stock()

# Update pizza availability
update_pizza_availability()

# Display pizza availability
with open(pizza_availability_file, "r") as file:
    for line in file:
        item, available = line.strip().split(":")
        item_name = menu[int(item)]['name']
        print(f"{item_name} - Available: {available}")

from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)
file_path = os.path.join(os.path.dirname(__file__), "currentOrder.txt")

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/order', methods=['POST'])
def order_pizza():
    # Get the pizza name from the POST request
    pizza_name = request.form.get('pizza_name')
    
    # Print the order and save it to the file
    print(f"{pizza_name} ordered!")
    with open(file_path, "w") as file:
        file.write(pizza_name)

    return redirect(url_for('success'))

@app.route('/success')
def success():
    return "Successfully ordered!"

@app.route('/chef')
def chef():
    # Read the current order from the file
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            current_order = file.read()
        if current_order:
            return f"The chef needs to prepare: {current_order}"
        else:
            return "No current orders."
    return "Order file not found."

if __name__ == "__main__":
    app.run(debug=True)

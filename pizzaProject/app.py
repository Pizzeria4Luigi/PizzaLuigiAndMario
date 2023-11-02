from flask import Flask, render_template, request, redirect, url_for, json, session
import os

app = Flask(__name__)
file_path = os.path.join(os.path.dirname(__file__), "currentOrder.txt")
app.secret_key = "super secret key"

@app.route('/',methods=['GET', 'POST'])
def Main():
    if 'username' in session:
        return render_template('PizzaMenu.html', username=session['username'])
    else:
        return render_template('PizzaMenu.html')

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

@app.route('/registration', methods=['GET', 'POST'])
def Register_page1():
        if request.method == "POST":
            attempted_username = request.form['Username']
            attempted_password = request.form['Password']
            attempted_email= request.form['Email']

            d = {"email": "", "pass": "", "user": ""}
            with open('data.json', 'r') as outfile: 
                data = json.load(outfile)

            print(data)
                # json.load(d, outfile)
            # d = {"email": "", "pass": "", "user": ""}
            d['user']=attempted_username
            
            d['pass']=attempted_password
            
            d['email']=attempted_email
            data.append(d)
            with open('data.json', 'w') as outfile:  
                json.dump(data, outfile, indent=4)

            if request.form['Username'] == '' or request.form['Password'] == '' or request.form['Email'] == '':
               return 'Invalid Credentials. Please try again.' 
            else: 
                return render_template('LoginPage.html')
        else:
            return render_template('RegisterPage.html')

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    #error = ' '

# try:
    if request.method == "POST":
        # attempted_username = request.form['Username']
        # attempted_password = request.form['Password']
        # attempted_email = request.form['Email']
        
        with open('data.json', 'r') as outfile: 
            data = json.load(outfile)
       
        print(data)
        
        for user in data:
            if request.form['Username'] == user['user'] and request.form['Password'] == user['pass'] and request.form['Email'] == user['email']:
                print(request.form['Username'])
                session['username'] = request.form['Username']
                return redirect(url_for('Main'))
                #return 'SUCCESSFULLY LOGGEDIN'
                #error = 'Invalid Credentials. Please try again.'
            # return render_template('bcd.html')
        #return render_template('login.html')

    return render_template('LoginPage.html')

@app.route('/new', methods=['GET', 'POST'])
def new():
    return render_template('bcd.html')

if __name__ == "__main__":
    app.run(debug=True)

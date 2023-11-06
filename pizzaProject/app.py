from flask import Flask, render_template, request, redirect, url_for, json, session, flash, jsonify
import os
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
import time
import json
from flask import Flask, request, jsonify

app = Flask(__name__)
file_path = os.path.join(os.path.dirname(__file__), "currentOrder.txt")
app.secret_key = "super secret key"

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465  # or the appropriate port
app.config['MAIL_USERNAME'] = 'adriansdaleckis@gmail.com'
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

# Function to generate the confirmation token
def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.secret_key)
    return serializer.dumps(email, salt='email-confirm')

# Function to confirm the token
def confirm_token(token, expiration=3600):  # Token expiration time set to 1 hour (3600 seconds) by default
    serializer = URLSafeTimedSerializer(app.secret_key)
    try:
        email = serializer.loads(
            token,
            salt='email-confirm',
            max_age=expiration
        )
    except:
        return False
    return email

@app.route('/',methods=['GET', 'POST'])
def Main():
    ref_value = request.args.get('ref')
    session["Table"] = ref_value
    print(session["Table"])
    if 'username' in session:
        return render_template('PizzaMenu.html', username=session['username'])
    else:
        return render_template('PizzaMenu.html')
    
@app.route('/send-conf-mail', methods=['GET', 'POST'])
def send_conf_mail():
    if request.method == 'POST':
        email = request.form['email']
        message = Message('Email Confirmation', sender='your_email@example.com', recipients=[email])
        message.body = 'This is a confirmation email to confirm the existence of the email.'
        mail.send(message)
        return 'Email sent successfully!'
    return render_template('email_form.html')  # Create a template named 'email_form.html'

@app.route('/order', methods=['POST'])
def order_pizza():
    # Get the pizza name from the POST request
    pizza_name = request.form.get('pizza_name')
    with open(file_path, "r+") as file:
        try:
            orders = json.load(file)
        except json.decoder.JSONDecodeError:
            orders = {}

        orders[pizza_name] = orders.get(pizza_name, 0) + 1
        file.seek(0)  # Move to the start of the file
        json.dump(orders, file)
        file.truncate()  # Remove any remaining contents from the old version
    
    return jsonify(message=f"{pizza_name} ordered!", current_orders=orders)

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
            

            for user in data:
                print(user['email'])
                print(attempted_email)
                if user['email'] == attempted_email:
                    flash(f'User with email {attempted_email} already exists.')
                    return render_template('RegisterPage.html')

            for user in data:
                print(user['user'])
                print(attempted_email)
                if user['user'] == attempted_username:
                    flash(f'User with username {attempted_username} already exists.')
                    return render_template('RegisterPage.html')

            d['user']=attempted_username
            
            d['pass']=attempted_password
            
            d['email']=attempted_email
            data.append(d)

            token = generate_confirmation_token(attempted_email)  # You will need to implement this function
            confirm_url = f'http://127.0.0.1:5000/confirm_email/{token}'  # Replace with your website URL
            html = render_template('confirmation_email.html', confirm_url=confirm_url)
            message = Message('Account Confirmation', sender='adriansdaleckis@gmail.com', recipients = ['adriansdaleckis@gmail.com'])
            message.html = html
            mail.send(message)

            session['email_confitmed'] = False

            if request.form['Username'] == '' or request.form['Password'] == '' or request.form['Email'] == '':
               return 'Invalid Credentials. Please try again.' 
            else: 
                with open('data.json', 'w') as outfile:  
                    json.dump(data, outfile, indent=4)
                return render_template('LoginPage.html')
        else:
            return render_template('RegisterPage.html')

@app.route('/confirm_email/<token>', methods=['GET'])
def confirm_email(token):
    email = confirm_token(token)  # Use the confirm_token function you previously defined
    if email:
        # Here you can add code to update the user's account as confirmed or perform any other necessary actions.
        session['email_confitmed'] = True
        return f'Thank you for confirming your email, {email}!'
    else:
        return 'The confirmation link is invalid or has expired.'


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
        
        print(session['email_confitmed'])
       
        if session['email_confitmed'] == True:
            for user in data:
                if request.form['Password'] == user['pass'] and request.form['Email'] == user['email']:
                    session['username'] = user['user']
                    return redirect(url_for('Main'))
                    #return 'SUCCESSFULLY LOGGEDIN'
                    #error = 'Invalid Credentials. Please try again.'
                # return render_template('bcd.html')
            #return render_template('login.html')
        else:
            flash(f'You have not confirmed your email.')
            return render_template('LoginPage.html')

    return render_template('LoginPage.html')

@app.route('/logout')
def logout():
    # Clear the email stored in the session object
    session.pop('username', default=None)
    return redirect(url_for('Main'))

@app.route('/orders', methods=['GET', 'POST'])
def orders():
    return render_template('Orders.html')

@app.route('/forgotten_password', methods=['GET', 'POST'])
def forgotten_password():
    if request.method == "POST":
        message = Message('Your password', sender='adriansdaleckis@gmail.com', recipients=['adriansdaleckis@gmail.com'])

        with open('data.json', 'r') as outfile: 
            data = json.load(outfile)
        for user in data:
            if request.form['Email'] == user['email']:
                cur_password = user['pass']

        if 'cur_password' in locals():
            message.body = f'Your password is {cur_password}.'
            mail.send(message)
            flash('Email sent successfully!')
            return render_template('LoginPage.html')
        else:
            flash('This email does not exist in our database')
            return render_template('ForgottenPassword.html')
    return render_template('ForgottenPassword.html')

@app.route('/new', methods=['GET', 'POST'])
def new():
    return render_template('bcd.html')

@app.route('/waiters_page', methods=['GET', 'POST'])
def waiters_page():
    orders = []
    _dict = {1 : "Margherita", 2 : "Pepperoni", 3 : "Quattro Formaggi", 4 : "Mario's Madness", 5 : "Luigi's Baloney", 6 : "Bowser Buns"}
    while True:
        time.sleep(10)
        with open('C:/Users/Dalecky/Desktop/University/Week9/test/currentOrder.txt', 'r') as file:
            data = file.readlines()
            for line in data:
                line = line.split(":")
                order = str(f"Table {int(line[1])} ordered {_dict[int(line[0])]}")
                orders.append(order)
            print(orders)
        return render_template('waiters_page.html', orders=orders)

@app.route('/discount', methods=['GET', 'POST'])
def discount():
    if 'username' in session:
        flash("Order completed")
        return render_template('PizzaMenu.html')
    else:
        return render_template('Discount.html')

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for, json, session, flash, jsonify
import os
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
import time
import json
from flask import Flask, request, jsonify
import os
import subprocess

global Margherita
global Pepperoni
global Formaggi
global Madness
global Baloney
global Buns

Margherita = None
Pepperoni = None
Formaggi = None
Madness = None
Baloney = None
Buns = None


global chef_orders_dict
chef_orders_dict = []

pizzaStatus=[]

app = Flask(__name__)
file_path = os.path.join(os.path.dirname(__file__), "currentOrder.txt")
app.secret_key = "super secret key"
app.static_folder = 'static'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465  # or the appropriate port
app.config['MAIL_USERNAME'] = 'adriansdaleckis@gmail.com'
app.config['MAIL_PASSWORD'] = 'umdj tatc wdzd rdzm'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

# Run pizzamenusystem.py before starting the Flask app
try:
    result = subprocess.check_output(['python', 'pizzamenusystem.py'], stderr=subprocess.STDOUT, text=True)
    # Process the result or capture any output from the script
    print(result)
except subprocess.CalledProcessError as e:
    # Handle any errors if the script didn't run successfully
    print(f"Error running pizzamenusystem.py: {e.output}")

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
    if request.args.get('ref') is not None:
        ref_value = request.args.get('ref')
        session["Table"] = ref_value
    #print(session["Table"])
    if 'username' in session:
        return render_template('PizzaMenu.html', username=session['username'], 
                               Margherita=Margherita, Pepperoni=Pepperoni, Formaggi=Formaggi, Madness=Madness, Baloney=Baloney, Buns=Buns)
    else:
        return render_template('PizzaMenu.html', 
                               Margherita=Margherita, Pepperoni=Pepperoni, Formaggi=Formaggi, Madness=Madness, Baloney=Baloney, Buns=Buns)
    
@app.route('/send-conf-mail', methods=['GET', 'POST'])
def send_conf_mail():
    if request.method == 'POST':
        email = request.form['email']
        message = Message('Email Confirmation', sender='adriansdaleckis@gmail.com', recipients=['adriansdaleckis@gmail.com'])
        message.body = 'This is a confirmation email to confirm the existence of the email.'
        mail.send(message)
        return 'Email sent successfully!'
    return render_template('email_form.html')  # Create a template named 'email_form.html'

@app.route('/order', methods=['POST'])
def order_pizza():
    pizza_name = request.form.get('pizza_name')
    # Write the updated orders back to the file
    print(pizza_name)
    with open('currentOrder.json', 'r') as f:
        data = json.load(f)
        table = data[int(session["Table"]) - 1]
        amount = table[pizza_name]
        amount = amount + 1
        table[pizza_name] = amount
        #data.append()
    with open('currentOrder.json', 'w') as f:
        json.dump(data, f, indent=4)
    return redirect(url_for('success'))

@app.route('/success')
def success():
    return render_template('Success.html')

@app.route('/chef')
def chef():
    if session["username"] == "Chef":
        with open('currentOrder.json', 'r') as f:
            #chef_orders_dict = []
            data = json.load(f)
            count = 0
            for x in range(len(chef_orders_dict)):
                    chef_orders_dict.pop(0)
            for _dict in data:
                count = count + 1
                #_dict = data[int(session["Table"])-1]
                for pizza in _dict:
                    while _dict[pizza] != 0:
                        chef_orders_dict.append([pizza, _dict[pizza], str(count)])
                        _dict[pizza] = _dict[pizza] - 1
        print(chef_orders_dict)
        return render_template('Chef.html', data=chef_orders_dict, table = session["Table"])
    else:
        return "You dont have access to this page"

@app.route('/registration', methods=['GET', 'POST'])
def Register_page1():
        if request.method == "POST":
            attempted_username = request.form['Username']
            attempted_password = request.form['Password']
            attempted_email= request.form['Email']

            d = {"email": "", "pass": "", "user": ""}
            with open('data.json', 'r') as outfile: 
                data = json.load(outfile)
            

            for user in data:
                if user['email'] == attempted_email:
                    flash(f'User with email {attempted_email} already exists.')
                    return render_template('RegisterPage.html')

            for user in data:
                if user['user'] == attempted_username:
                    flash(f'User with username {attempted_username} already exists.')
                    return render_template('RegisterPage.html')

            d['user']=attempted_username
            
            d['pass']=attempted_password
            
            d['email']=attempted_email

            d['conf'] = "False"
            data.append(d)

            token = generate_confirmation_token(attempted_email)  # You will need to implement this function
            confirm_url = f'http://127.0.0.1:5000/confirm_email/{token}'  # Replace with your website URL
            html = render_template('confirmation_email.html', confirm_url=confirm_url)
            print(attempted_email)
            message = Message('Account Confirmation', sender='adriansdaleckis@gmail.com', recipients = ['adriansdaleckis@gmail.com'])
            message.html = html
            mail.send(message)

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
        with open('data.json', 'r') as outfile: 
                data = json.load(outfile)
        with open('data.json', 'w') as outfile:
                for _dict in data:
                    if _dict['email'] == email:
                        _dict["conf"] = "True"
                json.dump(data, outfile, indent=4)
        return f'Thank you for confirming your email, {email}!'
    else:
        return 'The confirmation link is invalid or has expired.'


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == "POST":
        with open('data.json', 'r') as outfile:
            data = json.load(outfile)
            for _dict in data:
                    if _dict['email'] == request.form['Email']:
                        if _dict['conf'] == "True":
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
    with open('currentOrder.json', 'r') as f:
        orders_dict = {}
        data = json.load(f)
        _dict = data[int(session["Table"])-1]
        for pizza in data[int(session["Table"])-1]:
            orders_dict[pizza] = _dict[pizza]
    print(orders_dict)
    return render_template('Orders.html', data=orders_dict, table = session["Table"])

@app.route('/change-quantity', methods=['POST'])
def change_quantity():
    pizza_type = request.form['pizzaType']
    action = request.form['action']  # "increment" or "decrement"
    table_index = int(session["Table"]) - 1

    with open('currentOrder.json', 'r+') as f:
        orders = json.load(f)
        if action == 'increment':
            orders[table_index][pizza_type] += 1
        elif action == 'decrement' and orders[table_index][pizza_type] > 0:
            orders[table_index][pizza_type] -= 1

        f.seek(0)
        json.dump(orders, f, indent=4)
        f.truncate()

    return redirect(url_for('orders'))

@app.route('/finalize-order', methods=['POST'])
def finalize_order():
    # ... your logic to finalize the order ...
    # For now, it will just redirect to the discount page.
    return redirect(url_for('discount'))



@app.route('/forgotten_password', methods=['GET', 'POST'])
def forgotten_password():
    if request.method == "POST":
        message = Message('Your password', sender='adriansdaleckis@gmail.com', recipients=[request.form['Email']])

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
    if session["username"] == "Waiter":
        orders = []
        _dict = {"Margherita" : "Margherita", "Pepperoni" : "Pepperoni", "Formaggi" : "Formaggi", "Madness" : "Madness", "Baloney" : "Baloney", "Buns" : "Buns"}
        while True:
            time.sleep(10)
            with open('Waiter.txt', 'r') as file:
                data = file.readlines()
                for line in data:
                    line = line.split(":")
                    #order = str(f"Table {int(line[1])} ordered {_dict[line[0]]}")
                    order = [int(line[1]), _dict[line[0]]]
                    orders.append(order)
                print(orders)
            return render_template('waiters_page.html', orders=orders)
    else:
        return "You dont have access to this page"

@app.route('/discount', methods=['GET', 'POST'])
def discount():
    if 'username' in session:
        #flash("Order completed")
        return redirect(url_for('success'))
    else:
        return render_template('Discount.html')
    
@app.route('/smartOven', methods=['POST'])
def read_info():
    remove_order = request.get_json()
    if remove_order.get('status') == True:
        print("WORKS")
        print(chef_orders_dict)
        pizza_to_delete = chef_orders_dict[0][0]
        table_to_delete = chef_orders_dict[0][2]
        
        with open('currentOrder.json', 'r') as f:
            data = json.load(f)
            _dict = data[int(table_to_delete) - 1]
            print(_dict)
            #print(_dict)
            print(_dict[pizza_to_delete])
            _dict[pizza_to_delete] -= 1
            print(_dict)
        with open('currentOrder.json', 'w') as outfile:  
            json.dump(data, outfile, indent=4)
        
        with open("Waiter.txt", "a") as file:
            '''
            if os.path.getsize("Waiter.txt") > 0:
                lines = file.readlines()
                print("Works!!!")
                lines[-1].write(str(f"{pizza_to_delete}:{table_to_delete}\n"))
            else:
            '''
            file.write(str(f"{pizza_to_delete}:{table_to_delete}") + "\n")
        return redirect(url_for('test'))
    return "OK"

@app.route('/test', methods=['POST'])
def test():
    return render_template('PizzaMenu.html')

@app.route('/delivered')
def delivered():
    with open("Waiter.txt", "r") as f:
        lines = f.readlines()
    with open("Waiter.txt", "w") as f:
        f.writelines(lines[1:])
    return redirect(url_for('waiters_page'))
    #return render_template('waiters_page.html')

@app.route('/pizzaStatus', methods = ['POST'])
def Read_info():
    global Margherita, Pepperoni, Formaggi, Madness, Baloney, Buns
    data = request.get_json()
    Margherita = data['1']
    Pepperoni = data['2']
    Formaggi = data['3']
    Madness = data["4"]
    Baloney = data["5"]
    Buns = data['6']

    return "OK"

if __name__ == "__main__":
    app.run(debug=True)
        
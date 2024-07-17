from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import string
import random
import matplotlib.pyplot as plt

app = Flask(__name__)

# Replace these with your MySQL database credentials
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '12345',
    'database': 'electric'
}

@app.route('/')
def index():
    return render_template('index.html')

def idgenerator(size=4, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

@app.route('/new_customer', methods=['GET', 'POST'])
def new_customer():
    cno = None
    if request.method == 'POST':
        # Handle form submission and insert new customer into the database
        name = request.form['name']
        address = request.form['address']
        phone = request.form['phone']

        # Perform database insertion here using MySQL Connector
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Adapt the SQL query based on your database structure
        cno = idgenerator()
        query = "INSERT INTO ID (CONSUMER_ID, name) VALUES (%s, %s)"
        values = (cno, name)
        cursor.execute(query, values)
        connection.commit()
        query = "INSERT INTO Details (CONSUMER_ID, Address, Mob_no) VALUES (%s, %s, %s)"
        values = (cno, address, phone)
        cursor.execute(query, values)
        connection.commit()
        query = "INSERT INTO BILL (CONSUMER_ID) VALUES ('{}')".format(cno)
        cursor.execute(query)
        connection.commit()
        cursor.close()
        connection.close()


    return render_template('new_customer.html', cno=cno)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        # Handle login logic
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        consumer_id = request.form['consumer_id']
        try:
            query="select * from id where consumer_id='{}'".format(consumer_id)
            cursor.execute(query)
            res=list(cursor.fetchall())
            if(len(res)==1):
                return render_template('dashboard.html', consumer_id=consumer_id, name=res[0][1])
        except Exception as e:
            return render_template('login.html')

    return render_template('login.html', error=error)

@app.route('/')
def dashboard():
    return render_template('dashboard.html', customer_id=customer_id)
@app.route('/pay')
def pay():
    # Your pay logic here
    return render_template('pay.html')
@app.route('/payment_success')
def payment_success():
    # Your pay logic here
    return render_template('payment_success.html')

@app.route('/generate_bill', methods=['GET', 'POST'])
def generate_bill():
    consumer_id=None
    if request.method == 'GET':
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        consumer_id = request.args.get('consumer_id')
        # Assuming you have a SELECT query to get consumer details
        query = "SELECT CONSUMER_ID, unit_1m FROM Bill where Consumer_id='{}'".format(consumer_id)
        cursor.execute(query)
        consumers = list(cursor.fetchall())
        try:
            for consumer in consumers:
                # Your logic for calculating the bill amount based on current usage
                current_usage = consumer[1]
                if current_usage <= 100:
                    bill_amount = current_usage * 5
                elif 100 < current_usage <= 200:
                    bill_amount = 100 * 5 + ((current_usage - 100) * 10)
                else:
                    bill_amount = 100 * 5 + 100 * 10 + ((current_usage - 200) * 15)

            # Update the bill_amount in the database
                update_query = "UPDATE Bill SET price_present={} WHERE CONSUMER_ID='{}'".format(bill_amount, consumer_id)
                cursor.execute(update_query)
                connection.commit()

                query = "SELECT CONSUMER_ID, unit_1m, price_present FROM Bill where consumer_id='{}'".format(consumer_id)
                cursor.execute(query)
                consumers = list(cursor.fetchall())
                l = ["present month", "last month", "2nd last month"]
                q6 = "select unit_3m,unit_2m,unit_1m from BILL where consumer_id='{}'".format(consumer_id)
                cursor.execute(q6)
                res = list(cursor.fetchall())
                b = []
                colors = ["red", "green", "blue"]
                plt.barh(l[::-1], *res, color=colors)
                plt.xlabel("units------------>", fontsize=20, color="BLUE")
                plt.ylabel("months------------>", fontsize=20, color="RED")
                plt.show()

                cursor.close()
                connection.close()
            return render_template('Bill.html', consumers=consumers)
        except Exception as e:
            return "Bill Not generated"
    return "Invalid request method"


@app.route('/Ac_meter_application', methods=['GET', 'POST'])
def Ac_meter_application():
    if request.method=="GET":
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cno = request.args.get('consumer_id')
        app="Applied"
        s2=0
        query= "insert into APPLICATION values('{}','{}',{})".format(cno, app, s2)
        cursor.execute(query)
        connection.commit()
        cursor.close()
        connection.close()
    return render_template('Ac_meter_application.html')

@app.route('/Meter_surrender', methods=['GET', 'POST'])
def Meter_surrender():
    if request.method=="GET":
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cno = request.args.get('consumer_id')
        try:
            query="delete from id where consumer_id='{}'".format(cno)
            cursor.execute(query)
            query="delete from details where consumer_id='{}'".format(cno)
            cursor.execute(query)
            query = "delete from bill where consumer_id='{}'".format(cno)
            cursor.execute(query)
            query = "delete from application where consumer_id='{}'".format(cno)
            cursor.execute(query)
            connection.commit()
        except Exception as e:
            return "Doesn't exist in system"
    return render_template('Meter_surrender.html')
if __name__ == '__main__':
    app.run(debug=True)

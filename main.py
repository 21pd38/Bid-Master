from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import mysql.connector
from flask_session import Session
import base64 
from datetime import datetime, timedelta
from flask import session
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# Configure session to use filesystem
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Establish a connection to the MySQL database
mydb = mysql.connector.connect(
    host='127.0.0.1',  # Replace with your MySQL host
    user='root',  # Replace with your MySQL user
    password='VamsKris@987',  # Replace with your MySQL password
    database='appviewx'
)
mycursor = mydb.cursor(buffered=True)

logged_in = False  # Initialize a global flag to check if a user is logged in
logged_in_username = None

# Function to check if a username is already taken
def is_username_taken(username):
    query = "SELECT * FROM Auctioner WHERE username = %s"
    mycursor.execute(query, (username,))
    user = mycursor.fetchone()
    return user is not None

# Function to check if a bidder's username is taken
def is_bidder_username_taken(username):
    query = "SELECT username FROM bidder WHERE username = %s"
    mycursor.execute(query, (username,))
    existing_username = mycursor.fetchone()
    return existing_username is not None

# @app.route('/', methods=['GET', 'POST'])
# def login():
#     global logged_in
#     global logged_in_username
#     login_error = False

#     if request.method == 'POST':
#         if request.form.get('action') == 'login':
#             username = request.form.get('username')
#             password = request.form.get('password')

#             query = "SELECT * FROM Auctioner WHERE username = %s AND password = %s"
#             mycursor.execute(query, (username, password))
#             user = mycursor.fetchone()

#             if user:
#                 logged_in = True
#                 logged_in_username = username
#                 return redirect(url_for('home', login_success=True))
#             else:
#                 login_error = True

#     return render_template('login.html', login_error=login_error)

@app.route('/', methods=['GET', 'POST'])
def login():
    global logged_in
    global logged_in_username
    login_error = False

    if request.method == 'POST':
        if request.form.get('action') == 'login':
            username = request.form.get('username')
            password = request.form.get('password')

            query = "SELECT * FROM Auctioner WHERE username = %s AND password = %s"
            mycursor.execute(query, (username, password))
            user = mycursor.fetchone()
            session['username'] = username
            if user:
                logged_in = True
                logged_in_username = username
                user_type = 'auctioner'  # Set the user type to 'auctioner'
                # return redirect(url_for('home', login_success=True, user_type=user_type))
                return render_template('home.html', user_type=user_type)
            else:
                # Check if it's a bidder login
                query = "SELECT * FROM bidder WHERE username = %s AND password = %s"
                mycursor.execute(query, (username, password))
                bidder = mycursor.fetchone()
                if bidder:
                    logged_in = True
                    logged_in_username = username
                    user_type = 'bidder'  # Set the user type to 'bidder'
                    # return redirect(url_for('home', login_success=True, user_type=user_type))
                    return render_template('home.html', user_type=user_type)

                else:
                    login_error = True

    return render_template('login.html', login_error=login_error)


@app.route('/create_auction', methods=['GET', 'POST'])
def create_auction():
    global logged_in
    global logged_in_username
    wrong_username = False
    item_submitted = False
    success_message = ""  # Initialize the success message

    if request.method == 'POST':
        item_name = request.form['item_name']
        type = request.form['type']
        starting_price = request.form['starting_price']
        end_time = request.form['end_time']
        description = request.form['description']

        if logged_in_username is not None:
            # Handle file upload and save the image in the database
            image = request.files['image']
            image_data = image.read()

            # Insert the auction item data into the 'auction_items' table
            query = "INSERT INTO auction_items (item_name, username, type, starting_price, end_time, description, image) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            values = (item_name, logged_in_username, type, starting_price, end_time, description, image_data)
            mycursor.execute(query, values)
            mydb.commit()

            item_submitted = True
            success_message = f"Auction item '{item_name}' successfully added"  # Set the success message

        else:
            wrong_username = True

    return render_template('create_auction.html', logged_in_username=logged_in_username, wrong_username=wrong_username, item_submitted=item_submitted, success_message=success_message)

@app.route('/view_auction', methods=['GET'])
def view_auction():
    global logged_in
    global logged_in_username

    # Check if the user is logged in as an auctioner
    if logged_in and logged_in_username:
        # Query the database for auction items associated with the logged-in auctioner
        query = "SELECT item_id, item_name, username, type, starting_price, end_time, image FROM auction_items WHERE username = %s"
        mycursor.execute(query, (logged_in_username,))
        data = mycursor.fetchall()
        auction_details = []
        for item in data:
            item_id, item_name, username, type, starting_price, end_time, image = item
            auction_details.append({
                'item_id': item_id,
                'item_name': item_name,
                'username': username,
                'type': type,
                'starting_price': starting_price,
                'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S') if end_time else None,
                'image': base64.b64encode(image).decode('utf-8') if image else None,
            })

        return render_template('view_auction.html', auction_details=auction_details)
    else:
        return "You must be logged in as an auctioner to view auction items."


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    message = None  # Initialize the message variable

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        dob = request.form['dob']
        phone_number = request.form['phone_number']
        company_name = request.form['company_name']
        company_city = request.form['company_city']

        if is_username_taken(username):
            message = "Username already taken"
        else:
            # Check if both company_name and company_city are provided
            if company_name and company_city:
                # Assuming you have a database table named 'Auctioner', insert the user data into it
                query = "INSERT INTO Auctioner (username, password, first_name, last_name, dob, phone_number, company_name, company_city) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                values = (username, password, first_name, last_name, dob, phone_number, company_name, company_city)
            elif not company_name and not company_city:
                # If both company_name and company_city are empty, insert NULL values for both
                query = "INSERT INTO Auctioner (username, password, first_name, last_name, dob, phone_number, company_name, company_city) VALUES (%s, %s, %s, %s, %s, %s, NULL, NULL)"
                values = (username, password, first_name, last_name, dob, phone_number)
            elif company_name and not company_city:
                # If either company_name or company_city is empty, set the message
                message = "Invalid data, as no city is provided"
            elif not company_name and company_city:
                message = "Invalid data, as no company is provided"

            if message is None:
                mycursor.execute(query, values)
                mydb.commit()
                message = "Sign Up Successful"

    return render_template('signup.html', message=message)

@app.route('/auction_item_display', methods=['GET'])
def auction_item_display():
    query = "SELECT item_name, username, type, starting_price, end_time, image FROM auction_items"
    mycursor.execute(query)
    data = mycursor.fetchall()

    auction_details = []
    for item in data:
        item_name, username, type, starting_price, end_time, image = item
        auction_details.append({
            'item_name': item_name,
            'username': username,
            'type': type,
            'starting_price': starting_price,
            'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S') if end_time else None,
            'image': base64.b64encode(image).decode('utf-8') if image else None,
        })

    return render_template('auction_item_details.html', auction_details=auction_details)

@app.route('/bidder-signup', methods=['GET', 'POST'])
def bidder_signup():
    message = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        dob = request.form['dob']
        phone_number = request.form['phone_number']
        company_name = request.form['company_name']
        company_city = request.form['company_city']
        max_amount = request.form['max_amount']

        if is_bidder_username_taken(username):
            message = "Username already taken"
        else:
            # Check if both company_name and company_city are provided
            if company_name and company_city:
                query = "INSERT INTO bidder (username, password, first_name, last_name, dob, phone_number, company_name, company_city, max_amount) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                values = (username, password, first_name, last_name, dob, phone_number, company_name, company_city, max_amount)
            elif not company_name and not company_city:
                query = "INSERT INTO bidder (username, password, first_name, last_name, dob, phone_number, company_name, company_city, max_amount) VALUES (%s, %s, %s, %s, %s, %s, NULL, NULL, %s)"
                values = (username, password, first_name, last_name, dob, phone_number, max_amount)
            elif company_name and not company_city:
                message = "Invalid data, as no city is provided"
            elif not company_name and company_city:
                message = "Invalid data, as no company is provided"

            if message is None:
                mycursor.execute(query, values)
                mydb.commit()
                message = "Sign Up Successful"

    return render_template('bidder_signup.html', message=message)



@app.route('/bid_auctions')
def bid_auctions():
    # Retrieve the available auction items from the database
    query = "SELECT item_id, item_name, starting_price, type, end_time, description, image FROM auction_items"
    mycursor.execute(query)
    data = mycursor.fetchall()

    auction_details = []
    for item in data:
        item_id, item_name, starting_price, type, end_time, description, image = item
        auction_details.append({
            'item_id': item_id,
            'item_name': item_name,
            'starting_price': starting_price,
            'type': type,
            'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S') if end_time else None,
            'description': description,
            'image': base64.b64encode(image).decode('utf-8') if image else None,
        })

    return render_template('bid_auctions.html', auction_details=auction_details)

from flask import render_template, request, url_for, redirect


def insert_bid_transaction(cursor, item_id, item_name, username, starting_price, current_price, CurrentTime):
    # Define the SQL query with placeholders
    query = "INSERT INTO bid_transactions (item_id, item_name, username, starting_price, current_price, CurrentTime) VALUES (%s, %s, %s, %s, %s, %s)"
    
    # Define the values to insert
    values = (item_id, item_name, username, starting_price, current_price, CurrentTime)

    try:
        cursor.execute(query, values)
    except mysql.connector.Error as e:
        print(f"Error: {e}")

@app.route('/bid_form/<item_id>/<item_name>/<starting_price>', methods=['GET', 'POST'])
def bid_form(item_id, item_name, starting_price):
    if request.method == 'POST':
        current_price = request.form.get('current_price')
        if current_price is not None:
            username = session.get('username')
            # Check if the current price is greater than the starting price
            if float(current_price) <= float(starting_price):
                flash("Your bid must be greater than the starting price.", "error")
            else:
                max_amount = get_bidder_max_amount(username)
                # Check if the current price is within the bidder's maximum amount
                if max_amount is not None and float(current_price) <= float(max_amount):
                    CurrentTime = datetime.now()
                    # Check if the current price is greater than the current price at the previous row for the same item_id
                    if is_valid_bid(item_id, current_price):
                        # Insert a new row into the bid_transactions table
                        insert_bid_transaction(mycursor, item_id, item_name, username, starting_price, current_price, CurrentTime)
                        mydb.commit()
                        flash("Bid successfully")
                    else:
                        flash("Your bid must be greater than the previous bid for this item.", "error")
                else:
                    flash("Your bid exceeds your maximum amount.", "error")
            # Redirect to the same page to display the updated data
            return redirect(url_for('bid_form', item_id=item_id, item_name=item_name, starting_price=starting_price))

    # Retrieve bid transaction data from the database
    query = "SELECT MAX(current_price) FROM bid_transactions WHERE item_id = %s"
    mycursor.execute(query, (item_id,))
    max_previous_bid = mycursor.fetchone()[0] or 0

    # Fetch the maximum previous bid
    return render_template('bid_form.html', item_id=item_id, item_name=item_name, starting_price=starting_price, max_previous_bid=max_previous_bid)

def get_bidder_max_amount(username):
    # Query the database to get the maximum amount for the bidder
    query = "SELECT max_amount FROM bidder WHERE username = %s"
    mycursor.execute(query, (username,))
    result = mycursor.fetchone()
    if result:
        return result[0]
    else:
        return None

def is_valid_bid(item_id, current_price):
    # Query the database to get the current price for the same item_id
    query = "SELECT current_price FROM bid_transactions WHERE item_id = %s ORDER BY CurrentTime DESC LIMIT 1"
    mycursor.execute(query, (item_id,))
    result = mycursor.fetchone()

    if not result:
        # If there are no previous bids for this item, accept the bid
        return True

    previous_price = float(result[0])

    if float(current_price) > previous_price:
        return True

    return False

@app.route('/view_auction_status/<item_id>', methods=['GET'])
def view_auction_status(item_id):
    query = "SELECT * FROM bid_transactions where item_id= %s"
    mycursor.execute(query, (item_id,))
    data = mycursor.fetchall()
    print(data)

    return render_template('auction_status.html', auction_status=data)

@app.route('/view_successful_bids', methods=['GET'])
def view_successful_bids():
    # Fetch specific columns from the 'successful_bids' table'
    query = "SELECT item_id, item_name, username, Current_price, CurrentTime FROM successful_bids"
    mycursor.execute(query)
    successful_bids = mycursor.fetchall()
    return render_template('view_successful_bids.html', successful_bids=successful_bids)

@app.route('/delete_auction_item/<item_id>', methods=['GET'])
def delete_auction_item(item_id):
    # Add code to delete the auction item with the specified item_id from your database
    # Construct the SQL query to delete the item
    delete_query = "DELETE FROM auction_items WHERE item_id = %s"
    mycursor.execute(delete_query, (item_id,))
    mydb.commit()

    # Redirect the user back to the same page after deleting
    return redirect(url_for('view_auction'))  # Redirect to the 'view_auction' route


def insert_successful_bid(item_id, item_name, last_bidder, last_bid_amount, current_time):
    # Check if the item already exists in the successful_bids table
    check_existing_query = "SELECT item_id FROM successful_bids WHERE item_id = %s"
    mycursor.execute(check_existing_query, (item_id,))
    existing_item = mycursor.fetchone()

    if not existing_item:
        # Item doesn't exist in the successful_bids table, so insert it
        insert_query = "INSERT INTO successful_bids (item_id, item_name, username, Current_price, CurrentTime) VALUES (%s, %s, %s, %s, %s)"
        mycursor.execute(insert_query, (item_id, item_name, last_bidder, last_bid_amount, current_time))
        mydb.commit()
        print(f"Successful bid inserted for '{item_name}' (Item ID: {item_id})")

def check_auction_end_dates():
    # Get the current date and time
    current_datetime = datetime.now()

    # Calculate the time range within which to check for ended auctions (e.g., 10 seconds)
    time_range = timedelta(seconds=10)

    # Calculate the start time for the time range
    start_time = current_datetime - time_range

    # Query the database for auction items that have ended within the time range
    query = "SELECT item_id, item_name, end_time FROM auction_items WHERE end_time BETWEEN %s AND %s"
    mycursor.execute(query, (start_time, current_datetime))
    items = mycursor.fetchall()

    for item in items:
        item_id, item_name, _ = item  # Ignore the third value if returned
        print(f"Hi, Auction item '{item_name}' (Item ID: {item_id}) has ended.")

        # Retrieve the highest bid for the expired item
        bid_history_query = "SELECT username, current_price FROM bid_transactions WHERE item_id = %s ORDER BY current_price DESC LIMIT 1"
        mycursor.execute(bid_history_query, (item_id,))
        highest_bid = mycursor.fetchone()

        if highest_bid:
            last_bidder, last_bid_amount = highest_bid
            print(f"Last bidder: {last_bidder}, Last bid amount: {last_bid_amount}")

            # Insert the successful bid into the successful_bids table
            insert_successful_bid(item_id, item_name, last_bidder, last_bid_amount, current_datetime)

        else:
            print("No bidding history found for this item.")

# Create a scheduler instance
scheduler = BackgroundScheduler()

# Define a job to run the check_auction_end_dates function
def scheduled_job():
    check_auction_end_dates()

# Schedule the job to run every 30 minutes
scheduler.add_job(scheduled_job, 'interval', seconds=1)

if __name__ == '__main__':
    scheduler.start()
    app.run(debug=True)



from flask import Flask, render_template, request, redirect, url_for,flash

from werkzeug.security import check_password_hash, generate_password_hash

import mysql.connector

app = Flask(__name__)
app.secret_key = 'abc'
app.config['DEBUG'] = True

db = mysql.connector.connect(
   host="localhost",
   user="root",  # Replace with your MySQL username
   passwd="k@likeyug@23", 
   database="shrutidb"  # Replace with your database name# Replace with your MySQL password  database="shrutidb"  # Replace with your database name
)

cursor = db.cursor()

@app.route('/')

def index():
    return render_template('Homepage8.html')


@app.route('/add_user1', methods=['GET','POST'])
def add_user1():  
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone_number = request.form.get('phone_number')
        address = request.form.get('address')
        user_type = request.form.get('user_type')
    
    # Insert user into the database
        cursor.execute("INSERT INTO user (Firstname, LastName, Email, Password, PhoneNumber, Address, UserType) VALUES (%s, %s, %s, %s, %s,  %s,%s)", (first_name, last_name, email, password, phone_number, address, user_type))
        db.commit()
    
                 
    #return redirect(url_for('index'))
    return render_template('Login.html')

@app.route('/add_show1', methods=['POST'])
def add_show():
    if request.method == 'POST':
        play_id = request.form['play_id']
        theatre_id = request.form['theatre_id']
        show_datetime = request.form['show_datetime']
        ticket_price = request.form['ticket_price']
        available_tickets = request.form['available_tickets']
        status = request.form['status']
# Insert show details into the database (replace with actual query)
        # Assuming you have a function `execute_query` for database interactions
        execute_query("INSERT INTO Show (playID, TheatreID, ShowDateTime, TicketPrice, AvailableTickets, Status) "
                      "VALUES (%s, %s, %s, %s, %s, %s)",
                      (play_id, theatre_id, show_datetime, ticket_price, available_tickets, status))
        
           #flash('Show added successfully!', 'success')
        #return redirect(url_for('add_show1'))

    return render_template('add_show1.html')



@app.route('/add_play', methods=['GET', 'POST'])
def add_play_route():
    if request.method == 'POST':
        play_data = {
            'title': request.form['title'],
            'description': request.form['description'],
            'duration': request.form['duration'],
            'genre': request.form['genre'],
            'director': request.form['director'],
            'language': request.form['language'],
            'rating': request.form['rating']
        }

        add_play(play_data)
        flash('Play added successfully!', 'success')
        return redirect(url_for('plays'))

    return render_template('add_play1.html')

@app.route('/plays')
def plays():

    # Execute the SQL query to fetch plays
    cursor.execute("SELECT * FROM play")

    # Fetch all the plays
    plays_data = cursor.fetchall()

    # Close the cursor
    #cursor.close()

    return render_template('plays5.html', plays=plays_data)

@app.route('/theatres')
def theatres():
    try:
        # Check if the cursor is connected, if not, reconnect
        if not db.is_connected():
            db.reconnect()

        # Execute the SQL query to fetch theatres
        cursor.execute("SELECT * FROM theatre")

        # Fetch all the theatres
        theatres_data = cursor.fetchall()

        # Close the cursor
       # cursor.close()

        return render_template('theatres3.html', theatres=theatres_data)

    except Exception as e:
        # Handle the exception, you might want to log it or return an error page
        print(f"An error occurred: {e}")
        return "An error occurred."

    
@app.route('/shows')
def shows():
    # Execute the SQL query to fetch shows
        cursor.execute("SELECT * FROM `show`")
# Fetch all the shows
        shows_data = cursor.fetchall()
        return render_template('shows5.html', shows=shows_data)
    
def authenticate_user(email, password):
    # Query the database to check if the user with the provided email exists
    cursor.execute("SELECT * FROM user WHERE Email = %s", (email,))
    user_data = cursor.fetchone()

    if user_data:
        # If the user exists, check if the provided password is correct
        stored_password = user_data[3]  # Assuming the password is stored at index 3 in the user table
        if password == stored_password:
            return True  # Authentication successful

    return False  # Authentication failed       
        

@app.route('/login_existing_user', methods=['GET', 'POST'])
def login_existing_user():
    if request.method == 'POST':
        # Get user input
        email = request.form.get('email')
        password = request.form.get('password')

        # Perform authentication (replace this with your actual authentication logic)
        if authenticate_user(email, password):
            # If authentication is successful, you can redirect to another page or perform additional actions
            flash('Login successful!', 'success')
            return redirect(url_for('plays'))  # Redirect to the list of plays after login
        else:
            # If authentication fails, display an error message
            flash('Invalid email or password. Please try again.', 'error')
            return redirect(url_for('login_existing_user'))  # Redirect back to the login page if authentication fails
    return render_template('Login_existing_user.html')


@app.route('/book_ticket/<int:show_id>', methods=['GET', 'POST'])
def book_ticket(show_id):
    if request.method == 'POST':
        # Get user input
        user_email = request.form['user_email']
        num_tickets = request.form['num_tickets']
        booking_date = request.form['booking_date']
        ticket_price = request.form['ticket_price']

        # Validate user input (you may want to add more validation)
        if not user_email or not num_tickets.isdigit() or not booking_date or not ticket_price.isdigit():
            flash('Invalid input. Please provide valid information.', 'error')
            return redirect(url_for('book_ticket', show_id=show_id))

        # Check if the user exists
        cursor.execute("SELECT UserID FROM user WHERE Email = %s", (user_email,))
        user_result = cursor.fetchone()

        if not user_result:
            flash('User does not exist. Please register first.', 'error')
            return redirect(url_for('book_ticket', show_id=show_id))

        user_id = user_result[0]

        # Check if there are enough available tickets
        cursor.execute("SELECT AvailableTickets FROM `show` WHERE ShowID = %s", (show_id,))
        available_tickets_result = cursor.fetchone()

        if not available_tickets_result:
            flash('Invalid show ID. Please provide a valid show ID.', 'error')
            return redirect(url_for('book_ticket', show_id=show_id))

        available_tickets = available_tickets_result[0]

        if int(num_tickets) > available_tickets:
            flash('Not enough available tickets.', 'error')
            return redirect(url_for('book_ticket', show_id=show_id))

        # Book the tickets
        cursor.execute("INSERT INTO booking (UserID, ShowID, NumberOfTickets, BookingDate, TotalPrice) VALUES (%s, %s, %s, %s, %s)",
                       (user_id, show_id, num_tickets, booking_date, ticket_price))
        
        # Update the available tickets
        new_available_tickets = available_tickets - int(num_tickets)
        cursor.execute("UPDATE `show` SET AvailableTickets = %s WHERE ShowID = %s",
                       (new_available_tickets, show_id))

        db.commit()

        #flash('Tickets booked successfully!', 'success')
        return redirect(url_for('shows'))

    # If it's a GET request, render the booking form
    cursor.execute("SELECT * FROM `show` WHERE ShowID = %s", (show_id,))
    show_data = cursor.fetchone()
    return render_template('book_ticket4.html', show_id=show_id, show=show_data)

 
    cursor.close()

if __name__ == '__main__':
    app.run(debug=True)
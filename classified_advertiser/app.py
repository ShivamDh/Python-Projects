from flask import Flask, render_template, flash, redirect, url_for, request, session
from wtforms import Form, StringField, PasswordField, TextAreaField, DecimalField, validators
from passlib.hash import sha256_crypt
from app_details import db_password, app_secret_key
from functools import wraps
import mysql.connector


app = Flask(__name__, static_url_path='/static')

def sql_connector():
	return mysql.connector.connect(
		user='main',
		password=db_password,
		host='127.0.0.1',
		database='classified_advertiser'
	)

@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		search_query = request.form['search_field']
		return redirect('/search=' + search_query)

	# make SQL db connection and get cursor
	cnx = sql_connector()
	cursor = cnx.cursor()

	# query for all information regardings listings, limit of 3 for home page
	cursor.execute('SELECT * FROM posts')
	results = cursor.fetchmany(size=3)

	if len(results) > 0:
		# found results, display the results
		return render_template('home.html', listings=results)
	else:
		# no results, insert default paramater
		return render_template('home.html', listings=[])

	
@app.route('/search=<string:query>', methods=['GET', 'POST'])
def search(query):
	if request.method == 'POST':
		search_query = request.form['search_field']
		return redirect('/search=' + search_query)

	return render_template('search.html')

@app.route('/listings')
def listings():

	# make SQL db connection and get cursor
	cnx = sql_connector()
	cursor = cnx.cursor()

	# fetch information about all posts
	cursor.execute('SELECT * FROM posts')
	results = cursor.fetchall()

	if len(results) > 0:
		# display all the posts on the page
		return render_template('listings.html', listings=results)
	else:
		# flash the page with warning for no listings
		flash('No listings! Create one as a user using the dashboard', 'warning')
		return render_template('listings.html', listings=[])

@app.route('/listings/<string:listing_id>')
def listing(listing_id):

	# make SQL db connection and get cursor
	cnx = sql_connector()
	cursor = cnx.cursor()

	# get info about the specific listing from the db with listing)id
	cursor.execute('SELECT * FROM posts WHERE id = %s', (listing_id, ))

	# fetch only 1 result, the first one
	result = cursor.fetchone()

	if result is not None:
		# display appropriate results
		return render_template('listing.html', listing=result)
	else:
		# flash page with alert, wrong listing_id provided
		flash('Not a valid listing!', 'alert')
		return render_template('listing.html', listing=[])

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':

		# get inputted user data
		username = request.form['username']
		password = request.form['password']

		# make SQL db connection and get cursor
		cnx = sql_connector()
		cursor = cnx.cursor()

		# run a query to see if a matching user is found, should only be 1 user with same username
		cursor.execute('SELECT * FROM users WHERE username = %s', (username, ))
		result = cursor.fetchone()

		if result is not None:
			# check if password is correct with ecryption
			if sha256_crypt.verify(password, result[4]):
				session['logged_in'] = True
				session['username'] = username
				session['user_id'] = result[0]

				# flash success message, redirect to dashboard
				flash('You are now logged in', 'success')
				return redirect(url_for('dashboard'))
			else:
				# password didn't match the found username
				error = 'Incorrect Password, please try again'
				return render_template('login.html', error=error)
		else:
			cursor.close()
			cnx.close()

			# username just wasn't found
			error = 'Username not found, please register'
			return render_template('login.html', error=error)

	return render_template('login.html')

# form for registering a new user
class RegisterForm(Form):
	name = StringField('Name', [validators.Length(min=1, max=100)])
	email = StringField('Email', [
		validators.Length(min=6, max=50),
		validators.Email(message='Needs to be a valid email')
	])
	username = StringField('Username', [validators.Length(min=3, max=30)])
	password = PasswordField('Password', [
		validators.Length(min=6, max=50),
		validators.Regexp(
			'^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\$%\^&\*])(?=.{6,})',
			message='Need 1 uppercase, 1 lowercase, 1 special digit, 1 number')
	])
	confirm = PasswordField('Confirm Password', [
		validators.EqualTo('password', message='Passwords do not match')
	])

@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterForm(request.form)

	# if user submits a POST to register and it passes form validation
	if request.method == 'POST' and form.validate():
		name = form.name.data
		email = form.email.data
		username = form.username.data
		password = sha256_crypt.encrypt(str(form.password.data))

		# make SQL db connection and get cursor
		cnx = sql_connector()
		cursor = cnx.cursor()

		# get all the usernames from users table
		cursor.execute('SELECT username FROM users')
		usernames_results = cursor.fetchall()

		# flatten the 2D list into a list
		signed_up_usernames = sum(usernames_results, ())

		# username is already in use and registered with
		if username in signed_up_usernames:
			flash('This username is in use, please select a new username', 'alert')

			cursor.close()
			cnx.close()

			# redirect to register link to try again
			return redirect(url_for('register'))

		# new username in effect, add the user to database and continue registration
		cursor.execute(
			'INSERT INTO users(name, email, username, password) VALUES (%s, %s, %s, %s)',
			(name, email, username, password)
		)

		# Commit all the changes into the database
		cnx.commit()

		cursor.close()
		cnx.close()

		# flash a successful message and get the user to login
		flash('The user has been registered, login and start making your listings now!', 'success')

		return redirect(url_for('login'))

	# just viewing the registration form with GET method
	return render_template('register.html', form=form)

# function to check if a user is logged in via session cookies
def is_logged_in(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash('Unauthorized, Please login to view your dashboard', 'alert')
			return redirect(url_for('login'))
	return wrap

@app.route('/logout')
def logout():
	# clear session with logout and display message on logout
	session.clear()
	flash('You are now logged out', 'success')
	return redirect(url_for('login'))

@app.route('/dashboard')
@is_logged_in
def dashboard():

	# make SQL db connection and get cursor
	cnx = sql_connector()
	cursor = cnx.cursor()

	# query according the author_id which is determined from session cookies
	query = ("SELECT * FROM posts WHERE author_id = %s")
	cursor.execute(query, (session['user_id'], ))

	# fetch all listings by current user
	results = cursor.fetchall()

	if len(results) > 0:
		# display listings by current logged in user
		return render_template('dashboard.html', listings=results)
	else:
		# flash warning message for potential new user, needs to create a post
		flash('No listings created by user, create one now!', 'warning')
		return render_template('dashboard.html')

# form used to create a new listing
class PostForm(Form):
	title = StringField('Title', [validators.Length(min=2, max=255)])
	body = TextAreaField('Body', [validators.Length(min=6)])
	price = DecimalField('Price', [])

@app.route('/create_listing', methods=['GET', 'POST'])
@is_logged_in
def create_listing():
	form = PostForm(request.form)

	# POST method and validated through WTForms
	if request.method == 'POST' and form.validate():
		title = form.title.data or ''
		body = form.body.data or ''
		price = form.price.data or '' 

		# make SQL db connection and get cursor
		cnx = sql_connector()
		cursor = cnx.cursor()

		# insert the new listing into the database 
		cursor.execute(
			'INSERT INTO posts(title, author_id, body, price) VALUES (%s, %s, %s, %s)',
			(title, session['user_id'], body, price)
		)

		# Commit all the changes into the database and close connection
		cnx.commit()
		cursor.close()
		cnx.close()

		# flash success message for new listing, go back to dashboard
		flash('The listing has been created!', 'success')
		return redirect(url_for('dashboard'))

	# render regular html if GET request seen
	return render_template('create_listing.html', form=form)

@app.route('/edit_listing/<string:listing_id>', methods=['GET', 'POST'])
@is_logged_in
def edit_listing(listing_id):

	# make SQL db connection and get cursor
	cnx = sql_connector()
	cursor = cnx.cursor()

	# get specific post to edit from db, first one that matches on db query
	cursor.execute('SELECT * FROM posts WHERE id = %s', (listing_id, ))
	article = cursor.fetchone()

	form = PostForm(request.form)

	# autofill the form when editing
	form.title.data = article[1]
	form.body.data = article[3]
	form.price.data = article[4]

	if request.method == 'POST' and form.validate():
		title = request.form['title'] or ''
		body = request.form['body'] or ''
		price = request.form['price'] or ''

		# execute update sql command to db with form details
		cursor.execute(
			'UPDATE posts SET title = %s, body = %s, price = %s WHERE id = %s',
			(title, body, price, listing_id)
		)

		# commit all the changes into the database and close connection
		cnx.commit()
		cursor.close()
		cnx.close()

		# send a success message after editing the listing
		flash('The post has been updated!', 'success')
		return redirect(url_for('dashboard'))

	# close cursor and connection 
	cursor.close()
	cnx.close()

	# return listing page with form to be filled
	return render_template('edit_listing.html', form=form)	

@app.route('/delete_listing/<string:listing_id>', methods=['POST'])
@is_logged_in
def delete_listing(listing_id):

	# make SQL db connection and get cursor
	cnx = sql_connector()
	cursor = cnx.cursor()

	# Delete post relating to particular id
	cursor.execute('DELETE FROM posts WHERE id = %s', (listing_id, ))

	# Commit all the changes into the database
	cnx.commit()
	cursor.close()
	cnx.close()

	# Go back to the dashboard with success msg for deletion
	flash('Listing has been deleted', 'success')
	return redirect(url_for('dashboard'))

if __name__ == '__main__':
	app.secret_key = app_secret_key
	app.run(debug=True)


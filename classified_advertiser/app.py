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

@app.route('/')
def index():
	cnx = sql_connector()
	cursor = cnx.cursor()

	cursor.execute('SELECT * FROM posts')

	results = cursor.fetchmany(size=3)

	if len(results) > 0:
		return render_template('home.html', listings=results)
	else:
		return render_template('home.html', listings=[])

@app.route('/listings')
def listings():
	cnx = sql_connector()
	cursor = cnx.cursor()

	cursor.execute('SELECT * FROM posts')

	results = cursor.fetchall()

	if len(results) > 0:
		return render_template('listings.html', listings=results)
	else:
		flash('No listings online!', 'warning')
		return render_template('listings.html')

@app.route('/listings/<string:listing_id>')
def listing(listing_id):
	cnx = sql_connector()
	cursor = cnx.cursor()

	cursor.execute('SELECT * FROM posts WHERE id = %s', (listing_id, ))

	result = cursor.fetchone()

	if result is not None:
		return render_template('listing.html', listing=result)
	else:
		flash('Not a valid listing!', 'alert')
		return render_template('listing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		app.logger.info(request.form)

		username = request.form['username']
		password = request.form['password']

		app.logger.info(username)
		app.logger.info(password)

		cnx = sql_connector()
		cursor = cnx.cursor()

		cursor.execute('SELECT * FROM users WHERE username = %s', (username, ))

		results = cursor.fetchall()
		if len(results) > 0:
			first_result = results[0]

			if sha256_crypt.verify(password, first_result[4]):
				session['logged_in'] = True
				session['username'] = username
				session['user_id'] = first_result[0]

				flash('You are now logged in', 'success')
				return redirect(url_for('dashboard'))
			else:
				error = 'Incorrect Password, please try again'
				return render_template('login.html', error=error)
		else:
			cursor.close()
			cnx.close()

			error = 'Username not found, please register'
			return render_template('login.html', error=error)

	return render_template('login.html')

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
	if request.method == 'POST' and form.validate():
		name = form.name.data
		email = form.email.data
		username = form.username.data
		password = sha256_crypt.encrypt(str(form.password.data))

		cnx = sql_connector()
		cursor = cnx.cursor()

		cursor.execute('SELECT username FROM users')
		usernames_results = cursor.fetchall()

		signed_up_usernames = sum(usernames_results, ())

		if username in signed_up_usernames:
			flash('This username is in use, please select a new username', 'alert')

			cursor.close()
			cnx.close()

			return redirect(url_for('register'))

		cursor.execute(
			'INSERT INTO users(name, email, username, password) VALUES (%s, %s, %s, %s)',
			(name, email, username, password)
		)

		# Commit all the changes into the database
		cnx.commit()

		cursor.close()
		cnx.close()

		flash('The user has been registered, login and start making your listings now!', 'success')

		return redirect(url_for('login'))
	return render_template('register.html', form=form)

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
	session.clear()
	flash('You are now logged out', 'success')
	return redirect(url_for('login'))

@app.route('/dashboard')
@is_logged_in
def dashboard():
	cnx = sql_connector()
	cursor = cnx.cursor()

	query = ("SELECT * FROM posts WHERE author_id = %s")

	cursor.execute(query, (session['user_id'], ))

	results = cursor.fetchall()

	if len(results) > 0:
		return render_template('dashboard.html', listings=results)
	else:
		flash('No listings created by user, create one now!', 'warning')
		return render_template('dashboard.html')

class PostForm(Form):
	title = StringField('Title', [validators.Length(min=2, max=255)])
	body = TextAreaField('Body', [validators.Length(min=6)])
	price = DecimalField('Price', [])

@app.route('/create_listing', methods=['GET', 'POST'])
@is_logged_in
def create_listing():
	form = PostForm(request.form)
	if request.method == 'POST' and form.validate():
		title = form.title.data
		body = form.body.data
		price = form.price.data

		cnx = sql_connector()
		cursor = cnx.cursor()

		cursor.execute(
			'INSERT INTO posts(title, author_id, body, price) VALUES (%s, %s, %s, %s)',
			(title, session['user_id'], body, price)
		)

		# Commit all the changes into the database
		cnx.commit()

		cursor.close()
		cnx.close()

		flash('The post has been created!', 'success')

		return redirect(url_for('dashboard'))

	return render_template('create_listing.html', form=form)

@app.route('/edit_listing/<string:listing_id>', methods=['GET', 'POST'])
@is_logged_in
def edit_listing(listing_id):
	cnx = sql_connector()
	cursor = cnx.cursor()

	cursor.execute('SELECT * FROM posts WHERE id = %s', (listing_id, ))

	article = cursor.fetchone()

	form = PostForm(request.form)

	form.title.data = article[1]
	form.body.data = article[3]
	form.price.data = article[4]

	if request.method == 'POST' and form.validate():
		title = request.form['title']
		body = request.form['body']
		price = request.form['price']

		cursor = cnx.cursor()

		cursor.execute(
			'UPDATE posts SET title = %s, body = %s, price = %s WHERE id = %s',
			(title, body, price, listing_id)
		)

		# Commit all the changes into the database
		cnx.commit()

		cursor.close()
		cnx.close()

		flash('The post has been updated!', 'success')

		return redirect(url_for('dashboard'))
	else:
		cursor.close()
		cnx.close()

	return render_template('edit_listing.html', form=form)	

@app.route('/delete_listing/<string:listing_id>', methods=['POST'])
@is_logged_in
def delete_listing(listing_id):
	cnx = sql_connector()
	cursor = cnx.cursor()

	cursor.execute('DELETE FROM posts WHERE id = %s', (listing_id, ))

	# Commit all the changes into the database
	cnx.commit()

	cursor.close()

	flash('Listing Deleted', 'success')

	return redirect(url_for('dashboard'))

if __name__ == '__main__':
	app.secret_key = app_secret_key
	app.run(debug=True)


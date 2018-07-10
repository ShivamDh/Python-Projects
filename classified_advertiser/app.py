from flask import Flask, render_template, flash, redirect, url_for, request
from data import Listings
from wtforms import Form, StringField, PasswordField, validators
from passlib.hash import sha256_crypt
from app_details import db_password, app_secret_key
import mysql.connector

app = Flask(__name__, static_url_path='/static')

Listings = Listings()

@app.route('/')
def index():
	return render_template('home.html', listings = Listings[:3])

@app.route('/listings')
def listings():
	return render_template('listings.html', listings = Listings)

@app.route('/listings/<string:id>')
def listing(id):
	return render_template('listing.html', id = id)

@app.route('/signin')
def signin():
	return render_template('signin.html')

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

		cnx = mysql.connector.connect(
			user='main',
			password=db_password,
			host='127.0.0.1',
			database='classified_advertiser'
		)
		cursor = cnx.cursor()

		cursor.execute(
			'INSERT INTO users(name, email, username, password) VALUES (%s, %s, %s, %s)',
			(name, email, username, password)
		)

		# Commit all the changes into the database
		cnx.commit()

		cursor.close()
		cnx.close()

		flash('The user has been registered, start making your listings now!', 'success')

		return redirect(url_for('index'))
	return render_template('register.html', form=form)


if __name__ == '__main__':
	app.secret_key = app_secret_key
	app.run(debug=True)
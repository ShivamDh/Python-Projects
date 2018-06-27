from flask import Flask, render_template, flash, request
from data import Listings
from wtforms import Form, StringField, PasswordField, validators

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
	username = StringField('Username', [validators.Length(min=3, max=30)])
	email = StringField('Email', [
		validators.Length(min=6, max=50),
		validators.Email(message='Needs to be a valid email')
	])
	password = PasswordField('Password', [
		validators.Length(min=6, max=50),
		validators.Regexp(
			'^(?=.*[A-Z])(?=.*[!@#$&*])(?=.*[0-9])(?=.*[a-z]).{6}$',
			message='Need 1 uppercase, 1 lowercase, 1 special digit, 1 number')
	])
	confirm = PasswordField('Confirm Password', [
		validators.EqualTo('password', message='Passwords do not match')
	])

@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		return render_template('register.html')
	return render_template('register.html', form=form)



if __name__ == '__main__':
	app.run(debug=True)
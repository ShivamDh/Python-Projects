from flask import Flask, render_template
from data import Listings

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

@app.route('/register')
def register():
	return render_template('register.html')


if __name__ == '__main__':
	app.run(debug=True)
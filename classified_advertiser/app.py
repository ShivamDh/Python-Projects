from flask import Flask, render_template

app = Flask(__name__, static_url_path='/static')

@app.route('/')
def index():
	return render_template('home.html')

@app.route('/listings')
def about():
	return render_template('listings.html')

@app.route('/signin')
def signin():
	return render_template('signin.html')

@app.route('/register')
def register():
	return render_template('register.html')


if __name__ == '__main__':
	app.run(debug=True)
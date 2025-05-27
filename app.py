from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from flask_migrate import Migrate
import logging
from logging.handlers import RotatingFileHandler

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')  # Set this in Vercel
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# Set up logging
if not app.debug:
    handler = RotatingFileHandler('error.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.ERROR)
    app.logger.addHandler(handler)

# Model with full details
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    poster = db.Column(db.String(300), nullable=False)
    download_link = db.Column(db.String(300), nullable=False)

# Home route with optional search
@app.route('/', methods=['GET'])
def home():
    query = request.args.get('q', '').lower()
    try:
        movies = Movie.query.all()
        if query:
            movies = [m for m in movies if query in m.title.lower()]
        return render_template('index.html', movies=movies)
    except Exception as e:
        app.logger.error(f"Error fetching movies: {e}")  # Log the error
        return render_template('500.html'), 500  # Show the internal error page

@app.route('/add', methods=['GET'])
def add_movie_form():
    if not session.get('authenticated'):
        return redirect(url_for('login'))  # Redirect to login if not authenticated
    return render_template('add_movie.html')

@app.route('/add', methods=['POST'])
def add_movie():
    title = request.form['title']
    description = request.form['description']
    poster = request.form['poster']
    download_link = request.form['download_link']

    try:
        new_movie = Movie(title=title, description=description, poster=poster, download_link=download_link)
        db.session.add(new_movie)
        db.session.commit()
        return redirect('/')
    except Exception as e:
        db.session.rollback()  # Rollback the session in case of an error
        app.logger.error(f"Error adding movie: {e}")  # Log the error
        return render_template('500.html'), 500  # Show the internal error page

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'abhay' and password == 'abhaythakur':
            session['authenticated'] = True
            return redirect(url_for('add_movie_form'))  # Redirect to the add movie form
        else:
            return render_template('login.html', error="Invalid credentials. Please try again.")
    return render_template('login.html')

@app.route('/load_more', methods=['GET'])
def load_more():
    start = int(request.args.get('start', 0))
    movies = Movie.query.all()
    more_movies = movies[start:start + 6]  # Load the next 6 movies
    return {
        'movies': [
            {
                'title': movie.title,
                'description': movie.description,
                'poster': movie.poster
            } for movie in more_movies
        ]
    }

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()  # Rollback the session in case of an error
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)

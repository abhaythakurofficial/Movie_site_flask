from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from flask_migrate import Migrate

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')  # Set this in Vercel
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

migrate = Migrate(app, db)

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
    movies = Movie.query.all()
    
    # Limit to 6 movies for the initial load
    limited_movies = movies[:6]
    
    if query:
        limited_movies = [m for m in movies if query in m.title.lower()][:6]  # Limit search results to 6
    return render_template('index.html', movies=limited_movies)

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

    new_movie = Movie(title=title, description=description, poster=poster, download_link=download_link)
    db.session.add(new_movie)
    db.session.commit()

    return redirect('/')

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

if __name__ == '__main__':
    app.run()

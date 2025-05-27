# api/index.py

from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello World, I am Iron Man"

if __name__ == '__main__':
    app.run()
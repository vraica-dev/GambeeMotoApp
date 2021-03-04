from flask import Flask, render_template, url_for
from config import Config

app = Flask(__name__)
app.config.from_object(Config)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/trips')
def trips():
    return render_template('trips.html')



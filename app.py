from flask import Flask, render_template, url_for
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/trips')
def trips():
    return render_template('trips.html')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)


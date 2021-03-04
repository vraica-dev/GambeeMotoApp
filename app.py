from flask import Flask, render_template, url_for, request, redirect
from config import Config
from flask_sqlalchemy import SQLAlchemy
import os
from application import init_app

app = init_app()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)



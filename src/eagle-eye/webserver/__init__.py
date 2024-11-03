import os
from flask import Flask

# Main Flask application
app = Flask(
    __name__,
    static_folder='static/',
    template_folder='templates/',
)

from .routes import *

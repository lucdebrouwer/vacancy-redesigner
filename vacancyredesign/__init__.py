from flask import Flask
from flask_bootstrap import Bootstrap

app = Flask(__name__, instance_relative_config=True)
Bootstrap(app)
# Load the configurations into Flask
if app.config["ENV"] == "production":
    app.config.from_object("config.ProductionConfig")
else:
    app.config.from_object("config.DevelopmentConfig")

print(f'ENV is set to: {app.config["ENV"]}')

# import modules below instance creation to avoid circular imports
from vacancyredesign import routes
from vacancyredesign.modules import readability, genderwording
import nltk
import json
import os

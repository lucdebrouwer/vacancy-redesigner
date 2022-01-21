from flask import Flask
from flask_ckeditor import CKEditor
#from flask_bootstrap import Bootstrap


app = Flask(__name__, instance_relative_config=True)
#Bootstrap(app)
ckeditor = CKEditor(app)
#ckeditor.init_app(app)
# Load the configurations into Flask
if app.config["ENV"] == "production":
    app.config.from_object("config.ProductionConfig")
else:
    app.config.from_object("config.DevelopmentConfig")
      # px

print(f'ENV is set to: {app.config["ENV"]}')

# import modules below instance creation to avoid circular imports
from vacancyredesign import routes
from vacancyredesign.modules import readability, genderwording
import json
import os
import matplotlib
import seaborn
import unicodedata
import pysbd
from flask import Flask

app = Flask(__name__, instance_relative_config=True)

# Load the configurations into Flask
if app.config["ENV"] == "production":
    app.config.from_object("config.ProductionConfig")
else:
    app.config.from_object("config.DevelopmentConfig")

print(f'ENV is set to: {app.config["ENV"]}')

# import modules below instance creation to avoid circular imports
from vacancyredesign import routes
from vacancyredesign.modules import readability, genderwording


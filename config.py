import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = False

# Connect to the database


# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:password@localhost:5432/Fyyur' #postgresql://postgres:password@localhost:5432/Fyyur
#Instantiate the Model reps into the db with flask_migrate to connect to the table attributes in the db 

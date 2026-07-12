import os

# Get the base directory
basedir = os.path.abspath(os.path.dirname(__file__))
# Define the instance folder path
INSTANCE_DIR = os.path.join(basedir, 'instance')

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hackathon-secret-key-123'
    # Force the database to be in the 'instance' folder
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(INSTANCE_DIR, "transitops.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
import os
from server import app
from config import config

# Get the configuration based on environment
config_name = os.environ.get('FLASK_ENV', 'production')
app.config.from_object(config[config_name])

if __name__ == "__main__":
    app.run() 
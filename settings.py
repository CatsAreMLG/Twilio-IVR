import os
from os.path import join, dirname
from dotenv import load_dotenv  # need to `pip install -U python-dotenv`

# Create .env file path.
dotenv_path = join(dirname(__file__), '.env')
print(dotenv_path)

# Load file from the path.
load_dotenv(dotenv_path)

# Accessing variables.
ACCOUNT_SID = os.getenv('ACCOUNT_SID')
AUTH_TOKEN = os.getenv('AUTH_TOKEN')
SMS_DESTINATION = os.getenv('SMS_DESTINATION')

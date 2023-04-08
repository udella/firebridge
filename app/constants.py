# load .env file
import json
import os
from dotenv import load_dotenv
load_dotenv()

# get a environment variable called GOOGLE_APPLICATION_CREDENTIALS
# and assign it to the variable GOOGLE_APPLICATION_CREDENTIALS
GOOGLE_APPLICATION_CREDENTIALS = json.loads(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
#from dotenv import load_dotenv
import os

# Find .env file with os variables
#load_dotenv("dev.env")

# retrieve config variables
try:
    BOT_TOKEN = "5744274566:AAHRaYf-jV2o0ibwQWlL92Bh3jpLh3CTEcg" #os.getenv('BOT_TOKEN')
    BOT_OWNERS = ["923048680"]
except (TypeError, ValueError) as ex:
    print("Error while reading config:", ex)

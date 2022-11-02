from dotenv import dotenv_values
from flask import Flask,request
from pymongo import MongoClient
import certifi

app = Flask(__name__)
config = dotenv_values(".env")
app.mongodb_client = MongoClient(config["ATLAS_URI"], tlsCAFile=certifi.where())
db = app.mongodb_client.get_database("gratings")


@app.route("/test")
def mainroute():
    search = db.users.find_one({"id": 1})
    return f"{search}"
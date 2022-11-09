import json

import bcrypt
from dotenv import dotenv_values
from flask import Flask, request, jsonify
from pymongo import MongoClient
import certifi

app = Flask(__name__)
config = dotenv_values(".env")
app.mongodb_client = MongoClient(config["ATLAS_URI"], tlsCAFile=certifi.where())
db = app.mongodb_client.get_database("gratings")


# If there is someone logged in then unauthorized is 403 but if not then it's 401

@app.route("/entries/<int:idd>", methods=["GET", "PUT", "DELETE"])  # See all posts / Send a new post
@app.route("/entries/", methods=["GET", "POST"])  # See all posts / Send a new post
def mainroute(idd=0):
    data,author,review,game = None,None,None,None
    try:
        data = request.get_json()
        author = data["author"]
        review = data["review"]
        game = data["game"]
    except:
        print("No JSON object received in body")
    if request.method == "POST":
        id = db.ratings_dev.count_documents({}) + 1
        db.ratings_dev.insert_one({"id": id, "author": author, "review": review, "game": game})
        return jsonify({"Author: ": author, "Review:": review, "Game: ": game})
    elif request.method == "GET":
        if idd:
            search = db.ratings_dev.find_one({"id": idd}, {"_id": 0})
            return jsonify(search), 200
        else:
            search = db.ratings_dev.find({}, {"_id": 0})
            search = list(search)
            return jsonify(search), 200
    elif request.method == "PUT":
        search = db.ratings_dev.find_one({"id": idd}, {"_id": 0})
        if not search:
            return jsonify("ID not found"), 400
        else:
            if author != search["author"]:
                return jsonify("Not authorised to edit this review"), 403
            elif review == search["review"] and game == search["game"]:
                return jsonify("The request body is the same as the current information"), 400
            else:
                newvals = {"$set": {"game": game, "review": review}}
                db.ratings_dev.update_one(search, newvals)
        search = db.ratings_dev.find_one({"id": idd}, {"_id": 0, "id": 0})
        return jsonify(search)
    elif request.method == "DELETE":
        search = db.ratings_dev.find_one({"id": idd}, {"_id": 0})
        if search["author"] != author:
            return jsonify("Not authorised to delete this review"), 403
        else:
            teapot = db.ratings_dev.delete_one({"id": idd})
            return jsonify({"Deleted review": search["review"]}), 418


@app.route("/register")
def register():
    data = request.get_json()
    author = data["author"]
    passwd = data["passwd"]
    passwd = passwd.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(passwd, salt)
    hashed.decode("utf-8")
    insert = db.users.insert_one({"author": author, "passwd": hashed})
    return jsonify(f"User has been created! Welcome to Game Ratings {author}")


@app.route("/login")
def login():
    data = request.get_json()
    author = data["author"]
    search = db.users.find_one({"author": author})
    dbpass = search["pass"]
    dbpass = dbpass.encode("utf-8")
    userPass = data["pass"]
    userPass = userPass.encode("utf-8")
    passCheck = bcrypt.checkpw(userPass, dbpass)
    print(passCheck)
    if passCheck:
        return jsonify(f"Authorised. Welcome to Game Ratings {author}"), 200
    else:
        return jsonify("Unauthorized"), 401

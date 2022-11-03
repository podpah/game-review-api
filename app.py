from dotenv import dotenv_values
from flask import Flask, request, jsonify
from pymongo import MongoClient
import certifi

app = Flask(__name__)
config = dotenv_values(".env")
app.mongodb_client = MongoClient(config["ATLAS_URI"], tlsCAFile=certifi.where())
db = app.mongodb_client.get_database("gratings")


@app.route("/entries/<int:idd>", methods=["GET", "PUT"])  # See all posts / Send a new post
@app.route("/entries/", methods=["GET", "POST"])  # See all posts / Send a new post
def mainroute(idd=0):
    if request.method == "POST":
        data = request.get_json()
        id = db.ratings_dev.count_documents({}) + 1
        author = data["author"]
        review = data["review"]
        game = data["game"]
        db.ratings_dev.insert_one({"id": id, "author": author, "review": review, "game": game})
        return jsonify({"Author: ": author, "Review:": review, "Game: ": game})
    elif request.method == "GET":
        if idd:
            search = db.ratings_dev.find({"id": idd}, {"_id": 0})
            search = list(search)
            return f"{search} Test"
            # Would like to figure out how to separate it but that's not a very API thing to do
        else:
            search = db.ratings_dev.find({}, {"_id": 0})
            search = list(search)
            return f"{search} Test"
    elif request.method == "PUT":
        data = request.get_json()
        author = data["author"]
        review = data["review"]
        game = data["game"]
        search = db.ratings_dev.find_one({"id": idd}, {"_id": 0})
        if not search:
            return jsonify("ID not found"), 400
        else:
            if author != search["author"]:
                return jsonify("Not authorised to edit this review"), 400
            elif review == search["review"] and game == search["game"]:
                return jsonify("The request body is the same as the current information"), 400
            else:
                newvals = {"$set": {"game": game, "review": review}}
                db.ratings_dev.update_one(search, newvals)
        search = db.ratings_dev.find_one({"id": idd}, {"_id": 0, "id": 0})
        return jsonify(search)

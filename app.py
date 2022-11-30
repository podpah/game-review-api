import jwt
import bcrypt
import datetime
from dotenv import dotenv_values
from flask import Flask, request, jsonify
from pymongo import MongoClient
import certifi

app = Flask(__name__)
config = dotenv_values(".env")
# This links it to the .env file with your secret variables
# The certifi is here to prevent issues when connecting to mongo
app.mongodb_client = MongoClient(config["ATLAS_URI"], tlsCAFile=certifi.where())
db = app.mongodb_client.get_database("gratings")
jwt_sec = config["JWT_SEC"]

if __name__ == "__main__":
    app.run(debug=True)


def autho():
    try:
        bearer = request.headers.get("Authorization")
        bearer = bearer.split(" ")[-1]
        decoded = jwt.decode(
            bearer, jwt_sec, algorithms="HS256"
        )  # Automatically checks whether or not the token "exp" is in the future
        return decoded["author"]
    except jwt.ExpiredSignatureError:
        return "Expired"
    except:
        return "Not verified"


def check_json():
    review,game = None,None
    try:
        data = request.get_json()
        try:
            review = data["review"]
        except:
            None
        try:
            game = data["game"]
        except:
            None
        return {review, game}
    except:
        return [None, None]
    

def check_admin(search2):
    try:
        truth = search2["admin"]
    except:
        truth = False
    finally:
        return truth


@app.route(
    "/entries/<int:idd>", methods=["GET", "PUT", "DELETE"]
)  # See all posts / Send a new post
@app.route("/entries/", methods=["GET", "POST"])  # See all posts / Send a new post
def mainroute(idd=0):
    authorise = autho()
    if authorise == "Not verified":
        return (
            jsonify(
                {
                    "message": "INVALID TOKEN , please get a valid token from the /login endpoint "
                }
            ),
            400,
        )
    elif authorise == "Expired":
        return (
            jsonify(
                {
                    "message": "EXPIRED TOKEN , please get a new token from the /login endpoint "
                }
            ),
            400,
        )
    else:
        review, game = check_json()
        author = authorise
        if request.method == "POST":
            db.ratings_dev.insert_one(
                {"author": author, "review": review, "game": game}
            )
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
            search2 = db.users.find_one({"author": author}, {"_id": 0})
            search = db.ratings_dev.find_one({"id": idd}, {"_id": 0})
            if not search:
                return jsonify("ID not found"), 400
            elif review == search["review"] and game == search["game"]:
                return (
                    jsonify("The request body is the same as the current information"),
                    400,
                )
            elif search["author"] == author or check_admin(search2):
                newvals = {"$set": {"game": game, "review": review}}
                db.ratings_dev.update_one(search, newvals)
            elif author != search["author"]:
                return jsonify("Not authorised to edit this review"), 403
            search = db.ratings_dev.find_one({"id": idd}, {"_id": 0, "id": 0})
            return jsonify(
                {"message": "Updated review successfully ", "review": search}
            )
        elif request.method == "DELETE":
            search = db.ratings_dev.find_one({"id": idd}, {"_id": 0})
            search2 = db.users.find_one({"author": author}, {"_id": 0})
            if search["author"] == author or check_admin(search2):
                teapot = db.ratings_dev.delete_one({"id": idd})
                return jsonify({"Deleted review": search["review"]}), 418
            elif search["author"] != author:
                return jsonify("Not authorised to delete this review"), 403


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    author = data["author"]
    search = db.users.find_one({"author": author})
    if search:
        return jsonify(f"The user {author} already exists")
    passwd = data["passwd"]
    passwd = passwd.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(passwd, salt)
    hashed = hashed.decode("utf-8")
    insert = db.users.insert_one({"author": author, "passwd": hashed})
    return jsonify(f"User has been created! Welcome to Game Ratings {author}")


@app.route("/login")
def login():
    data = request.get_json()
    author = data["author"]
    search = db.users.find_one({"author": author}, {"_id": 0})
    if search is None:
        return jsonify("Could not find account, check your spelling"), 401
    dbpass = search["passwd"]
    dbpass = dbpass.encode("utf-8")
    userPass = data["passwd"]
    userPass = userPass.encode("utf-8")
    passCheck = bcrypt.checkpw(userPass, dbpass)
    if passCheck:
        token = jwt.encode(
            {
                "author": search["author"],
                "exp": datetime.datetime.now(tz=datetime.timezone.utc)
                + datetime.timedelta(hours=24),
            },
            jwt_sec,
            algorithm="HS256",
        )
        return jsonify(f"Authorised. Welcome to Game Ratings {author}", token), 200
    else:
        return jsonify("Unauthorized"), 401

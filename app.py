import os
import uuid
from datetime import datetime, timedelta
from functools import wraps

import jwt
from flask import Flask, jsonify, make_response, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config.from_object(os.environ["APP_SETTINGS"])
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
CORS(app)
db = SQLAlchemy(app)

from models import User


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/<name>")
def hello_name(name):
    return "Hello {}!".format(name)


# decorator for verifying the JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if "x-access-token" in request.headers:
            token = request.headers["x-access-token"]
        # return 401 if token is not passed
        if not token:
            return jsonify({"message": "Token is missing !!"}), 401

        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            print(data)
            current_user = User.query.filter_by(public_id=data["public_id"]).first()
        except Exception as e:
            print(e)
            return jsonify({"message": "Token is invalid !!"}), 401
        # returns the current logged in users contex to the routes
        return f(current_user, *args, **kwargs)

    return decorated


@app.route("/user", methods=["GET"])
@token_required
def get_all_users(current_user):
    # querying the database
    # for all the entries in it
    users = User.query.all()
    # converting the query objects
    # to list of jsons
    output = []
    for user in users:
        # appending the user data json
        # to the response list
        output.append(
            {"public_id": user.public_id, "name": user.name, "email": user.email}
        )

    return jsonify({"users": output})


@app.route("/login", methods=["POST"])
def login():
    # creates dictionary of form data
    form = request.json
    if not form:
        # returns 401 if any email or / and password is missing
        return make_response(
            "Could not verify",
            400,
            {"WWW-Authenticate": 'Basic realm ="Login required !!"'},
        )
    email = form.get("email")
    password = form.get("password")

    if not email or not password:
        # returns 401 if any email or / and password is missing
        return make_response(
            "Could not verify",
            401,
            {"WWW-Authenticate": 'Basic realm ="Login required !!"'},
        )

    user = User.query.filter_by(email=email).first()

    if not user:
        # returns 401 if user does not exist
        return make_response(
            "Could not verify",
            401,
            {"WWW-Authenticate": 'Basic realm ="User does not exist !!"'},
        )

    if check_password_hash(user.password, password):
        # generates the JWT Token
        token = jwt.encode(
            {
                "public_id": user.public_id,
                "exp": datetime.utcnow() + timedelta(minutes=30),
            },
            app.config["SECRET_KEY"],
        )

        return make_response(jsonify({"token": token}), 201)
    # returns 403 if password is wrong
    return make_response(
        "Could not verify",
        403,
        {"WWW-Authenticate": 'Basic realm ="Wrong Password !!"'},
    )


@app.route("/signup", methods=["POST"])
def signup():
    form = request.json
    if not form:
        # returns 401 if any email or / and password is missing
        return make_response(
            "Could not verify",
            400,
            {"WWW-Authenticate": 'Basic realm ="Login required !!"'},
        )

    email = form.get("email")
    password = form.get("password")
    name = form.get("name")

    if not email or not password or not name:
        # returns 401 if any email or / and password is missing
        return make_response(
            "Could not verify",
            401,
            {"WWW-Authenticate": 'Basic realm ="Login required !!"'},
        )

    # checking for existing user
    user = User.query.filter_by(email=email).first()
    if not user:
        # database ORM object
        user = User(
            public_id=str(uuid.uuid4()),
            name=name,
            email=email,
            password=generate_password_hash(password),
        )
        # insert user
        db.session.add(user)
        db.session.commit()
        token = jwt.encode(
            {
                "public_id": user.public_id,
                "exp": datetime.utcnow() + timedelta(minutes=30),
            },
            app.config["SECRET_KEY"],
        )

        return make_response(jsonify({"token": token}), 201)

        # return make_response("Successfully registered.", 201)
    else:
        # returns 202 if user already exists
        return make_response("User already exists. Please Log in.", 202)


if __name__ == "__main__":
    app.run()

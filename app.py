from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import os
import uuid
import jwt
from datetime import datetime, timedelta


app = Flask(__name__)
app.config.from_object(os.environ["APP_SETTINGS"])
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

from models import User


def generate_password_hash():
    return "lol"


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/<name>")
def hello_name(name):
    return "Hello {}!".format(name)


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

        return make_response(jsonify({"token": token.decode("UTF-8")}), 201)

        return make_response("Successfully registered.", 201)
    else:
        # returns 202 if user already exists
        return make_response("User already exists. Please Log in.", 202)


if __name__ == "__main__":
    app.run()

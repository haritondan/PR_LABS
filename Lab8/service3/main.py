# app.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from models.database import db
from flasgger import Swagger
from crud import CRUDUser
from flasgger import swag_from
import time
from raft import RAFTFactory
import random

from  models.electro_scooter import ElectroScooter

# Defining the service credentials.
service_info = {
    "host" : "127.0.0.1",
    "port" : 8000
}

# Stopping the start up of the service for a couple of seconds to chose a candidate.
time.sleep(random.randint(1,3))
# Creating the CRUD functionalities.
crud = RAFTFactory(service_info).create_server()

def create_app():
    app = Flask(__name__)

    # Configure SQLAlchemy to use SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://leonidas:12345@localhost:5432/testpython'
    db.init_app(app)
    Swagger(app)
    return app

if __name__ == "__main__":
    app = create_app()
    import routes
    app.run(host = service_info["host"], port = service_info["port"])
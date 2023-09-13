from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

app = Flask(__name__)

app.config.from_object('config.Config')

db = SQLAlchemy(app)

jwt = JWTManager(app)

from models import Vendor, Shop  
from routes import auth, shops 

if __name__ == '__main__':
    app.run(debug=True)

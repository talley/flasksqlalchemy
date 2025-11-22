from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text
from models import db  # ensure this references the same db object

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Boolean, nullable=False, server_default=text('false'))
    addedat = db.Column(db.TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    addedby = db.Column(db.String(200), nullable=False, server_default=text('CURRENT_USER'))
    updatedat = db.Column(db.TIMESTAMP, nullable=True)
    updatedby = db.Column(db.String(200), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "status": self.status,
            "addedat": self.addedat.isoformat() if self.addedat else None,
            "addedby": self.addedby,
            "updatedat": self.updatedat.isoformat() if self.updatedat else None,
            "updatedby": self.updatedby,
        }

class UserAuths(db.Model):
    __tablename__ = "userauths"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    active = db.Column(db.Boolean, nullable=False, server_default=text('true'))
    addedon = db.Column(db.TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    addedby = db.Column(db.String(200), nullable=False, server_default=text('CURRENT_USER'))
    updatedat = db.Column(db.TIMESTAMP, nullable=True)
    updatedby = db.Column(db.String(200), nullable=True)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "active": self.active,
            "addedon": self.addedon.isoformat(),
            "addedby": self.addedby,
            "updatedat": self.updatedat.isoformat() if self.updatedat else None,
            "updatedby": self.updatedby
        }
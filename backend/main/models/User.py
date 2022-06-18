import email
from email.policy import default
from inspect import Attribute
from unicodedata import name

from sqlalchemy import nullslast
from .. import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    admin = db.Column(db.Boolean, default=False, nullable=False)

    poemas = db.relationship('Poema', back_populates="user", cascade='all, delete-orphan')
    calificaciones = db.relationship('Calificacion', back_populates="user", cascade='all, delete-orphan')

    @property
    def plain_password(self):
        raise AttributeError('No Permitida')
    
    @plain_password.setter
    def plain_password(self,password):
        self.password = generate_password_hash(password)

    def validate_pass(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User: %r %r >' % (self.username, self.email)

    def to_json(self):
       #poemas = [poema.to_json() for poema in self.poemas]
        json_string = {
            'id' : self.id,
            'username' : str(self.username),
            'email' : str(self.email),
            'password': str(self.password),
            #'poemas_count': len(poemas),
        }
        return json_string

    def to_json_short(self):
       #poemas = [poema.to_json() for poema in self.poemas]
        json_string = {
            'id' : self.id,
            'username' : str(self.username),
            'admin' : str(self.admin),
            #'poemas_count': len(poemas),
        }
        return json_string

    def to_json_complete(self):
        poemas = [poema.to_json() for poema in self.poemas]
        calificaciones = [calificacion.to_json() for calificacion in self.calificaciones]
        json_string = {
            'id' : self.id,
            'username' : str(self.username),
            'email' : str(self.email),
            'password': str(self.password),
            'poema': poemas,
            'poema_count' : len(poemas),
            'calificaciones_count' : len(calificaciones),
            'admin' : str(self.admin),
        }
        return json_string

    @staticmethod
    def from_json(user_json):
        id = user_json.get('id')
        username = user_json.get('username')
        email = user_json.get('email')
        password = user_json.get('password')
        return User(id = id,
            username = username,
            email = email,
            plain_password =password,
            )
from .. import db
from. import UserModel
from datetime import datetime

class Poema(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    cuerpo = db.Column(db.String(500), nullable=False)
    fecha = datetime.now()

    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    user = db.relationship('User', back_populates = "poemas", uselist = False, single_parent = True)

    calificaciones = db.relationship('Calificacion', back_populates = "poema", cascade='all, delete-orphan')

    def __repr__(self):
        return '<Poema: %r %r >' % (self.titulo, self.cuerpo)

    def to_json(self):
        self.user = db.session.query(UserModel).get_or_404(self.userId)
        json_string = {
            'id' : self.id,
            'titulo' : str(self.titulo),
            'cuerpo' : str(self.cuerpo),
            'user' : self.user.to_json(),
            'fecha': str(self.fecha),
        }
        return json_string
    def to_json_complete(self):
        self.user = db.session.query(UserModel).get_or_404(self.userId)
        calificaciones = [calificacion.to_json() for calificacion in self.calificaciones]
        json_string = {
            'id' : self.id,
            'titulo' : str(self.titulo),
            'cuerpo' : str(self.cuerpo),
            'user' : self.user.to_json_short(),
            'fecha': str(self.fecha),
            'calificaciones': calificaciones,
            'calificaciones_count' : len(calificaciones),
        }
        return json_string
    @staticmethod
    def from_json(poema_json):
        id = poema_json.get('id')
        titulo = poema_json.get('titulo')
        cuerpo = poema_json.get('cuerpo')
        userId = poema_json.get('userId')
        fecha = poema_json.get('fecha')
        return Poema(id = id,
        titulo = titulo,
        cuerpo = cuerpo,
        userId = userId,
        fecha = fecha,
        )
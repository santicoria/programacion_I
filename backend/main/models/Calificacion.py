from .. import db
from. import UserModel, PoemaModel

class Calificacion(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    calificacion = db.Column(db.String(100), nullable=False)
    comentario = db.Column(db.String(200), nullable=False)

    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    user = db.relationship('User', back_populates = "calificaciones", uselist = False, single_parent = True)

    poemaId = db.Column(db.Integer, db.ForeignKey('poema.id'), nullable = False)
    poema = db.relationship('Poema', back_populates = "calificaciones", uselist = False, single_parent = True)

    def __repr__(self):
        return '<Calificacion: %r %r >' % (self.calificacion, self.comentario)

    def to_json(self):
        self.user = db.session.query(UserModel).get_or_404(self.userId)
        json_string = {
            'id' : self.id,
            'calificacion' : str(self.calificacion),
            'comentario' : str(self.comentario),
            'user' : self.user.to_json_short(),
        }
        return json_string

    @staticmethod
    def from_json(calificacion_json):
        id = calificacion_json.get('id')
        calificacion = calificacion_json.get('calificacion')
        comentario = calificacion_json.get('comentario')
        userId = calificacion_json.get('userId')
        poemaId = calificacion_json.get('poemaId')
        return Calificacion(id = id,
            calificacion = calificacion,
            comentario = comentario,
            userId = userId,
            poemaId = poemaId,
            )

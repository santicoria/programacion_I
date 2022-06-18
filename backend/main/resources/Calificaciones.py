from flask_restful import Resource
from flask import request, jsonify
from .. import db
from main.models import CalificacionModel
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

class Calificacion(Resource):
    def get(self, id):
        calificacion = db.session.query(CalificacionModel).get_or_404(id)
        return calificacion.to_json()
        
    @jwt_required()
    def delete(self, id):
        token_id = get_jwt_identity()
        claims = get_jwt
        calificacion = db.session.query(CalificacionModel).get_or_404(id)
        if not claims:
            claims = {'admin': False}
        if token_id == calificacion.user_id or claims['admin']:
            db.session.delete(calificacion)
            db.session.commit()
            return '', 204    
        else:
            return '', 403

class Calificaciones(Resource):
    def get(self):
        calificaciones = db.session.query(CalificacionModel).all()
        return jsonify({ 'califiaciones':[calificacion.to_json() for calificacion in calificaciones] })

    @jwt_required()
    def post(self):
        calificaciones_user_id = get_jwt_identity()
        calificaciones = db.session.query(CalificacionModel).all()
        calificaciones_del_user = False
        calificacion = CalificacionModel.from_json(request.get_json())
        calificacion.user_id = calificaciones_user_id
        for rew in calificaciones:
            if rew.user_id == calificaciones_user_id and rew.poem_id == calificacion.poemaId:
                calificaciones_del_user = True
                break
        poema = db.session.query(CalificacionModel).get_or_404(calificacion.poemaId)
        user_poema_id = poema.userId
        if calificaciones_user_id != user_poema_id and not calificaciones_del_user:
            try:
                db.session.add(calificaciones)
                db.session.commit()
                return calificacion.to_json(), 201
            except Exception as error:
                return str(error), 409
        else:
            return '', 403
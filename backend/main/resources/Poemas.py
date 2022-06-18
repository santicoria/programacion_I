from flask_restful import Resource
from flask import request, jsonify
from .. import db
from main.models import PoemaModel, UserModel, CalificacionModel
from sqlalchemy import func
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt


class Poema(Resource):

    def get(self, id):
        poema = db.session.query(PoemaModel).get_or_404(id)
        return poema.to_json()

    @jwt_required()
    def delete(self, id):
        user_id = get_jwt_identity()
        poema = db.session.query(PoemaModel).get_or_404(id)
        claims = get_jwt()
        if not claims:
            claims['admin']= False
        if poema.userId == user_id or claims['admin']:
            db.session.delete(poema)
            db.session.commit()
            return '', 204
        else:
            return '', 403

    @jwt_required()
    def put(self, id):
        user_id = get_jwt_identity()
        poema = db.session.query(PoemaModel).get_or_404(id)
        data = request.get_json().items()
        for key, value in data:
            setattr(poema, key, value)
        if poema.user_id == user_id:
            db.session.add(poema)
            db.session.commit()
            return poema.to_json() , 201
        else:
            return '', 403           

class Poemas(Resource):

    @jwt_required(optional=True)
    def get(self):
        page = 1
        per_page = 5
        user_id = get_jwt_identity()
        poemas = db.session.query(PoemaModel)
        if request.get_json():
            filters = request.get_json().items()
            for key,value in filters:
                if key =="page":
                    page = int(value)
                if key == "per_page":
                    per_page = int(value)

                if not user_id:
                    if key == "titulo":
                        poemas = poemas.filter(PoemaModel.titulo.like("%"+value+"%"))
                    if key == "fecha_may":
                        poemas = poemas.filter(PoemaModel.fecha.like >= value)
                    if key == "fecha_men":
                        poemas = poemas.filter(PoemaModel.fecha.like <= value)
                    if key == "username":
                        poemas = poemas.filter(PoemaModel.user.has(UserModel.username.like("%"+value+"%")))
                    if value == "calificacion_may":
                        poemas = poemas.outerjoin(PoemaModel.calificaciones).group_by(PoemaModel.id).having(func.count(CalificacionModel.id) >= value)
                    if value == "calificacion_men":
                        poemas = poemas.outerjoin(PoemaModel.calificaciones).group_by(PoemaModel.id).having(func.count(CalificacionModel.id) <= value)


                    if key == "orderby":
                        if value == "titulo":
                            poemas = poemas.order_by(PoemaModel.titulo)
                        if value == "titulo(desc)":
                            poemas = poemas.order_by(PoemaModel.titulo.desc())
                        if value == "fecha":
                            poemas = poemas.order_by(PoemaModel.fecha)
                        if value == "fecha(desc)":
                            poemas = poemas.order_by(PoemaModel.fecha.desc())
                        if value == "calificacion":
                            poemas = poemas.outerjoin(PoemaModel.calificaciones).group_by(PoemaModel.id).order_by(func.count(CalificacionModel.id))
                        if value == "calificacion(desc)":
                            poemas = poemas.outerjoin(PoemaModel.calificaciones).group_by(PoemaModel.id).order_by(func.count(CalificacionModel.id).desc())
                else:
                    poemas.order_by(PoemaModel.outerjoin(PoemaModel.calificaciones).group_by(PoemaModel.id).order_by(PoemaModel.fecha, func.count(CalificacionModel.id)))

        poemas = poemas.paginate(page, per_page, True, 20)            
        return jsonify({ 'poemas' : [poema.to_json_complete() for poema in poemas.items],
                    'total': poemas.total, 
                    'pages': poemas.pages,
                    'page': poemas.page,
                    })
    @jwt_required()
    def post(self):
        poema = PoemaModel.from_json(request.get_json())
        user_id = get_jwt_identity()
        poema.userId = user_id
        user = db.session.query(UserModel).get_or_404(user_id)
        poem_count =len(user.poemas)
        review_count = len(user.calificaciones)
        div = 0
        if poem_count != 0:
            div = review_count/poem_count
        if poem_count == 0 or div >=3:
            db.session.add(poema)
            db.session.commit()
            return poema.to_json(), 201
        else:
            return '', 405
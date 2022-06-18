from flask_restful import Resource
from flask import request, jsonify
import jwt
from .. import db
from main.models import UserModel, PoemaModel, CalificacionModel
from sqlalchemy import func
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from main.auth.decorators import admin_required


class User(Resource):
    @jwt_required()
    def put(self, id):
        user = db.session.query(UserModel).get_or_404(id)
        data = request.get_json().items()
        for key, value in data:
            setattr(user, key, value)
        db.session.add(user)
        db.session.commit()
        return user.to_json(), 201
        
    @admin_required
    def delete(self, id):
        user = db.session.query(UserModel).get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        return '', 204

    @jwt_required(optional=True)
    def get(self, id):
        user = db.session.query(UserModel).get_or_404(id)
        token_id = get_jwt_identity()
        claims = get_jwt()
        if token_id == user.id or claims['admin']:
            return user.to_json_complete()
        else:
            return user.to_json_short()

class Users(Resource):
    def get(self):
        page = 1
        per_page = 5
        
        users = db.session.query(UserModel)
        if request.get_json():
            filters = request.get_json().items()
            for key,value in filters:
                if key =="page":
                    page = int(value)
                if key == "per_page":
                    per_page = int(value)
                if key == "username":
                    users = users.filter(UserModel.username.like("%"+value+"%"))
                if key == "poema_count":
                    users = users.outerjoin(UserModel.poemas).group_by(UserModel.id).having(func.count(PoemaModel.id) >= value)
                if key == "reseña_count":
                    users = users.outerjoin(UserModel.calificaciones).group_by(UserModel.id).having(func.count(CalificacionModel.id) >= value)
                
                
                if key == "orderby":
                    if value == "username":
                        users = users.order_by(UserModel.username)
                    if value == "username(desc)":
                        users = users.order_by(UserModel.username.desc())
                    if value == "poemas":
                        users = users.outerjoin(UserModel.poemas).group_by(UserModel.id).order_by(func.count(PoemaModel.id).desc())
                    if value == "poemas(desc)":
                        users = users.outerjoin(UserModel.poemas).group_by(UserModel.id).order_by(func.count(PoemaModel.id))

        users = users.paginate(page, per_page, True, 20)

        return jsonify({'users': [user.to_json_complete() for user in users.items],
                    'total': users.total, 
                    'pages': users.pages,
                    'page': users.page,
                    })

    def post(self):
        user = UserModel.from_json(request.get_json())
        db.session.add(user)
        db.session.commit()
        return user.to_json(), 201
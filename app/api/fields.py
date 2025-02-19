from flask_restful import Resource, Api, reqparse
from flask import Blueprint
from app.models.field import Field
from app import db
from flask_login import current_user, login_required

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

class FieldListAPI(Resource):
    @login_required
    def get(self):
        """Récupérer tous les champs de l'utilisateur connecté"""
        fields = Field.query.filter_by(user_id=current_user.id).all()
        return [{
            'id': field.id,
            'name': field.name,
            'area': field.area,
            'crop_type': field.crop_type,
            'status': field.status
        } for field in fields]

    @login_required
    def post(self):
        """Créer un nouveau champ"""
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help='Le nom du champ est requis')
        parser.add_argument('area', type=float, required=True, help='La superficie est requise')
        parser.add_argument('crop_type', type=str, required=True, help='Le type de culture est requis')
        args = parser.parse_args()

        field = Field(
            name=args['name'],
            area=args['area'],
            crop_type=args['crop_type'],
            user_id=current_user.id
        )

        db.session.add(field)
        db.session.commit()

        return {
            'id': field.id,
            'name': field.name,
            'area': field.area,
            'crop_type': field.crop_type,
            'status': field.status
        }, 201

class FieldAPI(Resource):
    @login_required
    def get(self, field_id):
        """Récupérer un champ spécifique"""
        field = Field.query.filter_by(id=field_id, user_id=current_user.id).first_or_404()
        return {
            'id': field.id,
            'name': field.name,
            'area': field.area,
            'crop_type': field.crop_type,
            'status': field.status
        }

    @login_required
    def put(self, field_id):
        """Mettre à jour un champ"""
        field = Field.query.filter_by(id=field_id, user_id=current_user.id).first_or_404()
        
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str)
        parser.add_argument('area', type=float)
        parser.add_argument('crop_type', type=str)
        parser.add_argument('status', type=str)
        args = parser.parse_args()

        for key, value in args.items():
            if value is not None:
                setattr(field, key, value)

        db.session.commit()
        return {
            'id': field.id,
            'name': field.name,
            'area': field.area,
            'crop_type': field.crop_type,
            'status': field.status
        }

    @login_required
    def delete(self, field_id):
        """Supprimer un champ"""
        field = Field.query.filter_by(id=field_id, user_id=current_user.id).first_or_404()
        db.session.delete(field)
        db.session.commit()
        return '', 204

# Enregistrement des routes API
api.add_resource(FieldListAPI, '/fields')
api.add_resource(FieldAPI, '/fields/<int:field_id>')

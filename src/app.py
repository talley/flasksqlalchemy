from flask import Flask, request, jsonify, abort
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS, API_ACCESS_KEY
from models import db, User
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import os
import datetime
from models import UserAuths


from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", SQLALCHEMY_DATABASE_URI)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS", SQLALCHEMY_TRACK_MODIFICATIONS)
    
    app.config["JWT_SECRET_KEY"] = API_ACCESS_KEY
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(hours=2)
    
    db.init_app(app)
    jwt = JWTManager(app)

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"})

   
    @app.route("/users", methods=["POST"])
    @jwt_required()
    def create_user():
        #current_user = get_jwt_identity()
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON body required"}), 400

        name = data.get("name")
        age = data.get("age")
        status = data.get("status", False)
        addedby = data.get("addedby")  

        if not name or not isinstance(name, str):
            return jsonify({"error": "name is required and must be a string"}), 400
        if age is None or not isinstance(age, int):
            return jsonify({"error": "age is required and must be an integer"}), 400

        user = User(
            name=name,
            age=age,
            status=bool(status),
            addedby=addedby if addedby else None
        )
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "DB integrity error"}), 500

        return jsonify(user.to_dict()), 201

    
    @app.route("/users", methods=["GET"])
    @jwt_required()
    def list_users():
        #current_user = get_jwt_identity()
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))
        q = User.query.order_by(User.id).paginate(page=page, per_page=per_page, error_out=False)
        users = [u.to_dict() for u in q.items]
        return jsonify({
            "items": users,
            "page": page,
            "per_page": per_page,
            "total": q.total
        })


    @app.route("/users/<int:user_id>", methods=["GET"])
    @jwt_required()
    def get_user(user_id):
        #current_user = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        return jsonify(user.to_dict())

 
    @app.route("/users/<int:user_id>", methods=["PUT", "PATCH"])
    @jwt_required()
    def update_user(user_id):
        #current_user = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON body required"}), 400

     
        name = data.get("name")
        age = data.get("age")
        status = data.get("status")
        updatedby = data.get("updatedby")

        if name is not None:
            if not isinstance(name, str):
                return jsonify({"error": "name must be a string"}), 400
            user.name = name
        if age is not None:
            if not isinstance(age, int):
                return jsonify({"error": "age must be an integer"}), 400
            user.age = age
        if status is not None:
            user.status = bool(status)

        user.updatedat = datetime.utcnow()
        user.updatedby = updatedby if updatedby else None

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "DB integrity error"}), 500

        return jsonify(user.to_dict())


    @app.route("/users/<int:user_id>", methods=["DELETE"])
    @jwt_required()
    def delete_user(user_id):
        #current_user = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "deleted", "id": user_id})
    
    # JWT section
    
    @app.route("/auth/register", methods=["POST"])
    def register():
        data = request.get_json() or {}
        username = data.get("username")
        password = data.get("password")
        addedby = data.get("addedby")
    
        if not username or not password:
            return jsonify({"error": "username and password required"}), 400
    
        if UserAuths.query.filter_by(username=username).first():
            return jsonify({"error": "username already exists"}), 400
    
        user = UserAuths(
            username=username,
            addedby=addedby if addedby else None
        )
        user.set_password(password)
    
        db.session.add(user)
        db.session.commit()
    
        return jsonify({"message": "User registered", "user": user.to_dict()}), 201    


    @app.route("/auth/login", methods=["POST"])
    def login():
        data = request.get_json() or {}
        username = data.get("username")
        password = data.get("password")
    
        if not username or not password:
            return jsonify({"error": "username and password required"}), 400
    
        user = UserAuths.query.filter_by(username=username, active=True).first()
    
        if not user or not user.check_password(password):
            return jsonify({"error": "Invalid username or password"}), 401
    
        # JWT Payload
        token = create_access_token(identity={"username": user.username, "user_id": user.id})
    
        return jsonify({"access_token": token})
    
    
    
    
    return app

if __name__ == "__main__":
    app = create_app()
    
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)

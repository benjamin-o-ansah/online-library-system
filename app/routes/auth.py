from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity,JWTManager,get_jwt,exceptions
from app import db
from app.models import Users

BLACKLIST = set()
jwt = JWTManager()
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'message': 'Invalid input'}), 400

    # Hash the password
        hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')

    # Create a new user instance
        new_user = Users(username=data['username'], email=data['email'], password=hashed_password)


        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully!'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error registering user', 'error': str(e)}), 500
    
        

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Invalid input'}), 400

    user = Users.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password, data['password']):
        # Create a JWT token
        access_token = create_access_token(identity={'username': user.username})
        # return jsonify(access_token=access_token), 200
        return jsonify({'message': 'Successful sign in','access_token':access_token}), 200

    return jsonify({'message': 'Invalid credentials'}), 401

@bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


# Add a callback function to check if a token is blacklisted
@jwt.token_in_blocklist_loader
def check_if_token_is_blacklisted(jwt_payload):
    jti = jwt_payload['jti']
    return jti in BLACKLIST

@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        # Get the token's unique identifier (jti)
        jti = get_jwt()['jti']
        blac= []
        # Add the token's jti to the blacklist
        BLACKLIST.add(jti)
        for i in BLACKLIST:
            blac.append(i)
        return jsonify({"msg": "Successfully logged out","e":blac}), 200
       
    except Exception as e:
        return jsonify({"msg": "An error occurred during logout", "error": str(e)}), 500


@jwt.expired_token_loader
def handle_expired_error(e):
    return jsonify({"msg": "Token has expired","error":e}), 401


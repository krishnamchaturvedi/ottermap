from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import Vendor, db
from passlib.hash import sha256_crypt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    existing_vendor = Vendor.query.filter_by(email=data['email']).first()
    if existing_vendor:
        return jsonify({'message': 'Email already registered'}), 400

    hashed_password = sha256_crypt.hash(data['password'])

    new_vendor = Vendor(name=data['name'], email=data['email'], password=hashed_password)
    
    db.session.add(new_vendor)
    db.session.commit()

    return jsonify({'message': 'Vendor registered successfully'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']

    vendor = Vendor.query.filter_by(email=email).first()

    if vendor and sha256_crypt.verify(password, vendor.password):
        access_token = create_access_token(identity=vendor.id)
        return jsonify({'access_token': access_token}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    current_vendor_id = get_jwt_identity()
    vendor = Vendor.query.get(current_vendor_id)
    if vendor:
        return jsonify({'name': vendor.name, 'email': vendor.email}), 200
    else:
        return jsonify({'message': 'Vendor not found'}), 404

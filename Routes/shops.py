from flask import Blueprint, request, jsonify
from models import Shop, Vendor, db
from flask_jwt_extended import jwt_required, get_jwt_identity
from geopy.distance import geodesic

shops_bp = Blueprint('shops', __name__)

@shops_bp.route('/shops', methods=['POST'])
@jwt_required()
def create_shop():
    data = request.get_json()
    current_vendor_id = get_jwt_identity()
    
    vendor = Vendor.query.get(current_vendor_id)
    if not vendor:
        return jsonify({'message': 'Vendor not found'}), 404

    new_shop = Shop(
        name=data['name'],
        owner=data['owner'],
        business_type=data['business_type'],
        latitude=data['latitude'],
        longitude=data['longitude'],
        vendor_id=current_vendor_id
    )

    db.session.add(new_shop)
    db.session.commit()

    return jsonify({'message': 'Shop created successfully'}), 201

@shops_bp.route('/shops', methods=['GET'])
@jwt_required()
def get_vendor_shops():
    current_vendor_id = get_jwt_identity()
    shops = Shop.query.filter_by(vendor_id=current_vendor_id).all()
    shop_list = [{'name': shop.name, 'owner': shop.owner, 'business_type': shop.business_type,
                  'latitude': shop.latitude, 'longitude': shop.longitude} for shop in shops]
    return jsonify(shop_list), 200


@shops_bp.route('/shops/<int:shop_id>', methods=['PUT'])
@jwt_required()
def update_shop(shop_id):
    data = request.get_json()
    current_vendor_id = get_jwt_identity()

    shop = Shop.query.get(shop_id)
    if not shop:
        return jsonify({'message': 'Shop not found'}), 404

    if shop.vendor_id != current_vendor_id:
        return jsonify({'message': 'Unauthorized'}), 403

    shop.name = data['name']
    shop.owner = data['owner']
    shop.business_type = data['business_type']
    shop.latitude = data['latitude']
    shop.longitude = data['longitude']

    db.session.commit()

    return jsonify({'message': 'Shop updated successfully'}), 200


@shops_bp.route('/shops/<int:shop_id>', methods=['DELETE'])
@jwt_required()
def delete_shop(shop_id):
    current_vendor_id = get_jwt_identity()
    
    shop = Shop.query.get(shop_id)
    if not shop:
        return jsonify({'message': 'Shop not found'}), 404

    if shop.vendor_id != current_vendor_id:
        return jsonify({'message': 'Unauthorized'}), 403

    db.session.delete(shop)
    db.session.commit()

    return jsonify({'message': 'Shop deleted successfully'}), 200

@shops_bp.route('/nearby-shops', methods=['GET'])
@jwt_required()
def search_nearby_shops():
    data = request.get_json()
    current_vendor_id = get_jwt_identity()

    user_location = (data['latitude'], data['longitude'])
    shops = Shop.query.filter(Shop.vendor_id != current_vendor_id).all()
    
    nearby_shops = []
    for shop in shops:
        shop_location = (shop.latitude, shop.longitude)
        distance = geodesic(user_location, shop_location).kilometers

        if distance <= data['radius']:
            nearby_shops.append({
                'name': shop.name,
                'owner': shop.owner,
                'business_type': shop.business_type,
                'latitude': shop.latitude,
                'longitude': shop.longitude,
                'distance_km': distance
            })

    nearby_shops.sort(key=lambda x: x['distance_km'])  
    return jsonify(nearby_shops), 200

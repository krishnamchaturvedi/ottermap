import unittest
from app import app, db
from models import Vendor, Shop
import json

class TestShops(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def register_vendor(self):
        response = self.app.post('/auth/register', json={
            'name': 'Test Vendor',
            'email': 'test@example.com',
            'password': 'testpassword'
        })
        return json.loads(response.data.decode('utf-8'))

    def login_vendor(self):
        response = self.app.post('/auth/login', json={
            'email': 'test@example.com',
            'password': 'testpassword'
        })
        return json.loads(response.data.decode('utf-8'))['access_token']

    def test_create_shop(self):
        # Register a vendor and get the access token
        vendor_data = self.register_vendor()
        access_token = self.login_vendor()

        response = self.app.post('/shops', json={
            'name': 'Shop 1',
            'owner': 'Owner 1',
            'business_type': 'Type 1',
            'latitude': 40.7128,
            'longitude': -74.0060
        }, headers={'Authorization': 'Bearer ' + access_token})

        self.assertEqual(response.status_code, 201)

    def test_get_vendor_shops(self):
        vendor_data = self.register_vendor()
        access_token = self.login_vendor()

        self.app.post('/shops', json={
            'name': 'Shop 1',
            'owner': 'Owner 1',
            'business_type': 'Type 1',
            'latitude': 40.7128,
            'longitude': -74.0060
        }, headers={'Authorization': 'Bearer ' + access_token})

        response = self.app.get('/shops', headers={'Authorization': 'Bearer ' + access_token})
        shops = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(shops), 1)


if __name__ == '__main__':
    unittest.main()

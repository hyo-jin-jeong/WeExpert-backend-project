import jwt
from unittest.mock import MagicMock, patch

from django.test import TestCase, Client

from users.models           import Expert, Position, SellerInfo, User
from products.models        import Category
from wecode_expert.settings import SECRET_KEY, ALGORITHM

class UserTest(TestCase):
    def setUp(self):
        User.objects.create(
            email      = "gaya1@naver.com",
            image      = "http://yyy.kakao.com/dn/.../img_640x640.jpg",
            identifier = "1")

        User.objects.create(
            email      = "gaya1@naver.com",
            image      = "http://yyy.kakao.com/dn/.../img_640x640.jpg",
            identifier = "1")

    def tearDown(self):
        User.objects.all().delete()

    # TEST CODE 1
    @patch('users.views.requests')
    def test_social_login_success(self, mocked_requests):
        client = Client()

        class MockedResponse:
            def json(self):
                return {
                    "id"           : "123456789",
                    "kakao_account": {
                            "email"  : "gaya@naver.com",
                            "profile": {
                                "profile_image_url": "http://yyy.kakao.com/dn/.../img_640x640.jpg"
                            }
                        }
                }

        mocked_requests.post = MagicMock(return_value=MockedResponse())
        headers              = {'HTTP_Authorization': '1'}
        response             = client.post("/users/social-login", **headers)

        user         = User.objects.get(identifier='123456789')
        access_token = jwt.encode({'user_id': user.id}, SECRET_KEY, ALGORITHM)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {
            'message'     : 'SUCCESS',
            'access_token': access_token,
            'profile'     : 'http://yyy.kakao.com/dn/.../img_640x640.jpg'})

    #TEST CODE 0
    @patch('users.views.requests')
    def test_social_login_key_error(self, mocked_requests):
        client = Client()

        class MockedResponse:
            def json(self):
                return {
                    "id"           : "1",
                    "kakao_account": {
                            "email": "gaya@naver.com",
                        }
                }

        mocked_requests.post = MagicMock(return_value=MockedResponse())
        headers              = {'HTTP_Authorization': '1'}
        response             = client.post("/users/social-login", **headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message': 'KEY_ERROR'})

    #TEST CODE 0
    @patch('users.views.requests')
    def test_social_login_multiple_objects_returned(self, mocked_requests):
        client = Client()

        class MockedResponse:
            def json(self):
                return {
                    "id"           : "1",
                    "kakao_account": {
                            "email"  : "gaya1@naver.com",
                            "profile": {
                                "profile_image_url": "http://yyy.kakao.com/dn/.../img_640x640.jpg"
                            }
                        }
                }

        mocked_requests.post = MagicMock(return_value=MockedResponse())
        headers              = {'HTTP_Authorization': '1'}
        response             = client.post("/users/social-login", **headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
                         'message': 'MULTIPLE_OBJECT_RETURNED'})

    #TEST CODE -1
    @patch('users.views.requests')
    def test_social_login_invalid_token(self, mocked_requests):
        client = Client()

        class MockedResponse:
            def json(self):
                return {
                    "id"           : "1123",
                    "kakao_account": {
                            "email"  : "gaya@naver.com",
                            "profile": {
                                "profile_image_url": "http://yyy.kakao.com/dn/.../img_640x640.jpg"
                            }
                        }
                }

        mocked_requests.post = MagicMock(return_value=MockedResponse())
        response             = client.post("/users/social-login")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'message': 'INVALID_TOKEN'})

    #TEST CODE -1
    @patch('users.views.requests')
    def test_social_login_invalid_profile(self, mocked_requests):
        client = Client()

        class MockedResponse:
            def json(self):
                return {
                    "id"           : "1123",
                    "kakao_account": {
                            "profile": {
                                "profile_image_url": "http://yyy.kakao.com/dn/.../img_640x640.jpg"
                            }
                        }
                }

        mocked_requests.post = MagicMock(return_value=MockedResponse())
        headers              = {'HTTP_Authorization': '1'}
        response             = client.post('/users/social-login', **headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message': 'INVALID_PROFILE'})

class ExpertTest(TestCase):
    def setUp(self):
        User.objects.create(id=1, email='ttb@naver.com', image='http://')
        user        = User.objects.create(id=2, email='gaya@naver.com', image='http://')
        seller_info = SellerInfo.objects.create(address="dd", phone_number="dd",email="g@naver.com")
        position    = Position.objects.create(id=1, name='Front')

        Expert.objects.create(
            position     = position,
            user         = user,
            seller_info  = seller_info,
            introduction = "안녕하세요",
            image        = "http://",
            name         = "김민지")

        Category.objects.create(id=1, name='c언어')

    def tearDown(self):
        User.objects.all().delete()
        Category.objects.all().delete()
        Position.objects.all().delete()
        Expert.objects.all().delete()
        SellerInfo.objects.all().delete()
    
    # TEST CODE 1
    def test_expert_add_success(self):
        client = Client()

        user         = User.objects.get(email='ttb@naver.com')
        access_token = jwt.encode({'user_id': user.id}, SECRET_KEY, ALGORITHM)
        headers      = {'HTTP_Authorization': access_token}

        response = client.post('/users/expert', data={
            "introduction": "dd",
            "image"       : "dd",
            "name"        : "dd",
            "category_id" : 1,
            "hash_tag"    : ["d", "f", "s"],
            "seller_info" : {
                "address"     : "ff",
                "phone_number": "dd",
                "email"       : "ss"
            },
            "position_id": 1
        }, content_type='application/json', **headers)
    
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {'message': 'SUCCESS'})
    
    #TEST CODE 0
    def test_expert_add_key_error(self):
        client = Client()

        user         = User.objects.get(email='ttb@naver.com')
        access_token = jwt.encode({'user_id': user.id}, SECRET_KEY, ALGORITHM)
        headers      = {'HTTP_Authorization': access_token}

        response = client.post('/users/expert', data={
            "introduction": "dd",
            "name"        : "dd",
            "hash_tag"    : ["d", "s", "a"],
            "seller_info" : {
                "address"     : "ff",
                "phone_number": "dd",
                "email"       : "ss"
            },
            "position_id": 1
        }, content_type='application/json', **headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message': 'KEY_ERROR'})
    
    #TEST CODE 0
    def test_expert_add_json_decode_error(self):
        client = Client()

        user         = User.objects.get(email='ttb@naver.com')
        access_token = jwt.encode({'user_id': user.id}, SECRET_KEY, ALGORITHM)
        headers      = {'HTTP_Authorization': access_token}

        response = client.post('/users/expert', **headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message':'INVALID_VALUE'})
    
    #TEST CODE -1
    def test_expert_add_category_invalid(self):
        client = Client()

        user         = User.objects.get(email='ttb@naver.com')
        access_token = jwt.encode({'user_id': user.id}, SECRET_KEY, ALGORITHM)
        headers      = {'HTTP_Authorization': access_token}

        response = client.post('/users/expert', data={
            "introduction": "dd",
            "image"       : "dd",
            "name"        : "dd",
            "category_id" : 4,
            "hash_tag"    : ["d", "s", "w"],
            "seller_info" : {
                "address"     : "ff",
                "phone_number": "dd",
                "email"       : "ss"
            },
            "position_id": 1
        }, content_type='application/json', **headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message': 'INVALID_CATEGORY'})
    
    #TEST CODE -1
    def test_expert_add_exists_expert(self):
        client = Client()

        user         = User.objects.get(email='gaya@naver.com')
        access_token = jwt.encode({'user_id': user.id}, SECRET_KEY, ALGORITHM)
        headers      = {'HTTP_Authorization': access_token}

        response = client.post('/users/expert', data={
            "introduction": "dd",
            "image"       : "dd",
            "name"        : "dd",
            "category_id" : 1,
            "hash_tag"    : ["d"],
            "seller_info" : {
                "address"     : "ff",
                "phone_number": "dd",
                "email"       : "ss"
            },
            "position_id": 1
        }, content_type='application/json', **headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message':'EXISTS_EXPERT'})
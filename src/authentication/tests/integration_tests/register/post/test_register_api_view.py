from django.conf import settings
from parameterized import parameterized
from rest_framework.reverse import reverse

from authentication import ADL, MAJOR
from authentication.tests import CouchdbUserFactory
from authentication.utils import get_validation_code
from grm.tests import BaseTestCase


class TestRegisterAPIView(BaseTestCase):
    error_messages = {
        'invalid': 'Invalid data. Expected a dictionary, but got {datatype}.',
        'credentials': 'Unable to register with provided credentials.',
        'duplicated_email': 'A user with that email is already registered.',
        'wrong_validation_code': 'Unable to register with provided validation code.',
        'is_required': 'This field is required.',
        'may_not_be_blank': 'This field may not be blank.',
        'min_length': "This password is too short. It must contain at least %(min_length)d characters.",
        'max_length': "Ensure this field has no more than %(max_length)d characters.",
        'password_entirely_numeric': "This password is entirely numeric.",
    }

    def setUp(self):
        super().setUp()
        self.url = reverse('authentication:register')

    @parameterized.expand([
        (ADL,),
        (MAJOR,),
    ])
    def test_successful_register(self, doc_type):
        user = CouchdbUserFactory(doc_type=doc_type)
        doc = user.doc
        input_data = {
            'password': ''.join(['p' for _ in range(16)]),
            'email': user.email,
            'validation_code': get_validation_code(user.email),
        }

        with self.assertNumQueries(7):
            response = self.post(self.url, input_data, authorized=False)
        data = response.data

        assert response.status_code == 201
        assert len(data) == 3
        assert data['username'] == settings.COUCHDB_USERNAME
        assert data['password'] == settings.COUCHDB_PASSWORD
        assert data['doc_id'] == doc['_id']

    @parameterized.expand([
        ('commune',),
        (None,),
    ])
    def test_invalid_type(self, doc_type):
        user = CouchdbUserFactory(doc_type=doc_type)
        input_data = {
            'password': ''.join(['p' for _ in range(16)]),
            'email': user.email,
            'validation_code': get_validation_code(user.email),
        }

        response = self.post(self.url, input_data, authorized=False)
        data = response.data

        assert response.status_code == 400
        assert len(data) == 1
        assert str(data['non_field_errors'][0]) == self.error_messages['credentials']

    def test_empty_field(self):
        input_data = {
            'password': '',
            'email': '',
            'validation_code': '',
        }

        response = self.post(self.url, input_data, authorized=False)
        data = response.data

        assert response.status_code == 400
        assert {k for k in data} == {'password', 'email', 'validation_code'}
        for k in data:
            assert str(data[k][0]) == self.error_messages['may_not_be_blank']

    def test_empty_data(self):
        response = self.post(self.url, {}, authorized=False)
        data = response.data

        assert response.status_code == 400
        assert set(data.keys()) == {'password', 'email', 'validation_code'}
        for k in data:
            assert str(data[k][0]) == self.error_messages['is_required']

    def test_inactive_user(self):
        inactive_user = CouchdbUserFactory(is_active=False)
        input_data = {
            'password': ''.join(['p' for _ in range(16)]),
            'email': inactive_user.email,
            'validation_code': get_validation_code(inactive_user.email),
        }

        response = self.post(self.url, input_data, authorized=False)
        data = response.data

        assert response.status_code == 400
        assert len(data) == 1
        assert str(data['non_field_errors'][0]) == self.error_messages['credentials']

    def test_invalid_validation_code(self):
        user = CouchdbUserFactory(doc_type=ADL)
        other_user = CouchdbUserFactory(doc_type=ADL)
        input_data = {
            'password': ''.join(['p' for _ in range(16)]),
            'email': user.email,
            'validation_code': get_validation_code(other_user.email),
        }

        response = self.post(self.url, input_data, authorized=False)
        data = response.data

        assert response.status_code == 400
        assert len(data) == 1
        assert str(data['non_field_errors'][0]) == self.error_messages['wrong_validation_code']

    def test_short_password(self):
        user = CouchdbUserFactory()
        input_data = {
            'password': ''.join(['p' for _ in range(7)]),
            'email': user.email,
            'validation_code': get_validation_code(user.email),
        }

        response = self.post(self.url, input_data, authorized=False)
        data = response.data

        assert response.status_code == 400
        assert len(data) == 1
        assert str(data['password'][0]) == self.error_messages['min_length'] % {'min_length': 8}

    def test_long_password(self):
        user = CouchdbUserFactory()
        input_data = {
            'password': ''.join(['p' for _ in range(17)]),
            'email': user.email,
            'validation_code': get_validation_code(user.email),
        }

        response = self.post(self.url, input_data, authorized=False)
        data = response.data

        assert response.status_code == 400
        assert len(data) == 1
        assert str(data['password'][0]) == self.error_messages['max_length'] % {'max_length': 16}

    def test_numeric_password(self):
        user = CouchdbUserFactory()
        input_data = {
            'password': '12345678',
            'email': user.email,
            'validation_code': get_validation_code(user.email),
        }

        response = self.post(self.url, input_data, authorized=False)
        data = response.data

        assert response.status_code == 400
        assert len(data) == 1
        assert str(data['password'][0]) == self.error_messages['password_entirely_numeric']

    def test_user_is_already_register(self):
        registered_user = CouchdbUserFactory(password='not_empty', doc_type=ADL)
        input_data = {
            'password': '123a5b78',
            'email': registered_user.email,
            'validation_code': get_validation_code(registered_user.email),
        }

        response = self.post(self.url, input_data, authorized=False)
        data = response.data

        assert response.status_code == 400
        assert len(data) == 1
        assert str(data['non_field_errors'][0]) == self.error_messages['duplicated_email']

    @parameterized.expand([
        ('a', 'str'),
        (1, 'int'),
        (1.0, 'float'),
        ([], 'list'),
        ((), 'list'),
    ])
    def test_invalid_data(self, input_data, data_type):
        response = self.post(self.url, input_data, authorized=False)
        data = response.data

        assert response.status_code == 400
        assert len(data) == 1
        assert data['non_field_errors'][0] == self.error_messages['invalid'].format(datatype=data_type)

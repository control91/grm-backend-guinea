from django.conf import settings
from django.contrib.auth.hashers import make_password
from parameterized import parameterized
from rest_framework.reverse import reverse

from authentication import ADL, MAJOR
from authentication.tests import CouchdbUserFactory
from grm.tests import BaseTestCase


class TestAuthenticateAPIView(BaseTestCase):
    error_messages = {
        'invalid': 'Invalid data. Expected a dictionary, but got {datatype}.',
        'credentials': 'Unable to log in with provided credentials.',
        'is_required': 'This field is required.',
        'may_not_be_blank': 'This field may not be blank.',
    }

    def setUp(self):
        super().setUp()
        self.url = reverse('authentication:obtain_auth_credentials')

    @parameterized.expand([
        (ADL,),
        (MAJOR,),
    ])
    def test_successful_login(self, doc_type):
        password = 'p4ssw0rd'
        user = CouchdbUserFactory(password=make_password(password), doc_type=doc_type)
        doc = user.doc
        input_data = {
            'password': password,
            'email': user.email,
        }

        with self.assertNumQueries(7):
            response = self.post(self.url, input_data, authorized=False)
        data = response.data

        assert response.status_code == 200
        assert len(data) == 3
        assert data['username'] == settings.COUCHDB_USERNAME
        assert data['password'] == settings.COUCHDB_PASSWORD
        assert data['doc_id'] == doc['_id']

    def test_invalid_password(self):
        password = 'p4ssw0rd'
        user = CouchdbUserFactory(password=make_password(password), doc_type=ADL)
        input_data = {
            'password': password.upper(),
            'email': user.email,
        }

        response = self.post(self.url, input_data, authorized=False)
        data = response.data

        assert response.status_code == 400
        assert len(data) == 1
        assert str(data['non_field_errors'][0]) == self.error_messages['credentials']

    @parameterized.expand([
        ('commune',),
        (None,),
    ])
    def test_invalid_type(self, doc_type):
        password = 'p4ssw0rd'
        user = CouchdbUserFactory(password=make_password(password), doc_type=doc_type)
        input_data = {
            'password': password,
            'email': user.email,
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
        }

        response = self.post(self.url, input_data, authorized=False)
        data = response.data

        assert response.status_code == 400
        assert {k for k in data} == {'password', 'email'}
        for k in data:
            assert str(data[k][0]) == self.error_messages['may_not_be_blank']

    def test_empty_data(self):
        input_data = {}

        response = self.post(self.url, input_data, authorized=False)
        data = response.data

        assert response.status_code == 400
        assert {k for k in data} == {'password', 'email'}
        for k in data:
            assert str(data[k][0]) == self.error_messages['is_required']

    def test_no_user_for_email(self):
        user = CouchdbUserFactory()
        input_data = {
            'password': '12345678',
            'email': f'other_{user.email}',
        }

        response = self.post(self.url, input_data, authorized=False)
        data = response.data

        assert response.status_code == 400
        assert len(data) == 1
        assert str(data['non_field_errors'][0]) == self.error_messages['credentials']

    def test_inactive_user(self):
        password = 'p4ssw0rd'
        inactive_user = CouchdbUserFactory(password=make_password(password), is_active=False)
        input_data = {
            'password': password,
            'email': inactive_user.email,
        }

        response = self.post(self.url, input_data, authorized=False)
        data = response.data

        assert response.status_code == 400
        assert len(data) == 1
        assert str(data['non_field_errors'][0]) == self.error_messages['credentials']

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

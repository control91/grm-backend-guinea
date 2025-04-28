from parameterized import parameterized
from rest_framework.reverse import reverse

from authentication import ADL, MAJOR
from authentication.tests import CouchdbUserFactory
from grm.tests import BaseTestCase


class TestADLActiveAPIView(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.url = reverse('authentication:check_adl_status')

    @parameterized.expand([
        (ADL, True),
        (ADL, False),
        (MAJOR, True),
        (MAJOR, False),
    ])
    def test_valid_type(self, doc_type, is_active):
        user = CouchdbUserFactory(doc_type=doc_type, is_active=is_active)

        with self.assertNumQueries(7):
            response = self.get(self.url, {'email': user.email}, authorized=False)
        data = response.data

        assert response.status_code == 200
        assert len(data) == 1
        assert data['is_active'] == is_active

    @parameterized.expand([
        ('commune',),
        (None,),
    ])
    def test_invalid_type(self, doc_type):
        user = CouchdbUserFactory(doc_type=doc_type, is_active=True)
        input_data = {
            'email': user.email,
        }

        response = self.get(self.url, input_data, authorized=False)
        data = response.data

        assert response.status_code == 404
        assert len(data) == 1

    def test_empty_field(self):
        input_data = {
            'email': '',
        }

        response = self.get(self.url, input_data, authorized=False)
        data = response.data

        assert response.status_code == 404
        assert len(data) == 1

    def test_empty_data(self):
        input_data = {}

        response = self.get(self.url, input_data, authorized=False)
        data = response.data

        assert response.status_code == 404
        assert len(data) == 1

    def test_no_user_for_email(self):
        user = CouchdbUserFactory()
        input_data = {
            'email': f'other_{user.email}',
        }

        response = self.get(self.url, input_data, authorized=False)
        data = response.data

        assert response.status_code == 404
        assert len(data) == 1

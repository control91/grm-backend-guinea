from django.urls import reverse
from parameterized import parameterized

from authentication.tests import CouchdbUserFactory
from dashboard.adls.views import AdlListView
from grm.tests import DashboardTestCase
from authentication import ADL, MAJOR


class TestAdlListView(DashboardTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('dashboard:adls:list')

    def test_auth_permission(self):
        response = self.get(self.url, authorized=False)

        assert response.status_code == 302

    def test_context_data(self):
        adls = CouchdbUserFactory.create_batch(4, doc_type=ADL)
        docs = set()
        for adl in adls:
            doc = adl.doc
            docs |= {doc['_id']}

        with self.assertNumQueries(18):
            response = self.get(self.url)
        context_data = response.context_data

        assert response.status_code == 200
        assert context_data['title'] == AdlListView.title == 'Administrative Levels'
        assert context_data['active_level1'] == AdlListView.active_level1 == 'adls'
        assert context_data['active_level2'] == AdlListView.active_level2 is None
        assert len(context_data['breadcrumb']) == 1
        assert context_data['breadcrumb'][0]['url'] == AdlListView.breadcrumb[0]['url'] == ''
        assert context_data['breadcrumb'][0]['title'] == AdlListView.breadcrumb[0]['title'] == AdlListView.title
        assert context_data['paginator'] == context_data['page_obj'] is None
        assert context_data['is_paginated'] is False
        assert context_data['object_list'] == context_data['adls']
        assert {doc['_id'] for doc in context_data['adls']} == docs
        assert len(adls) == 4
        assert isinstance(context_data['view'], AdlListView)

    @parameterized.expand([
        (1,),
        (3,),
        (5,),
    ])
    def test_only_adls(self, size):
        adls = CouchdbUserFactory.create_batch(size, doc_type=ADL)
        docs = set()
        for adl in adls:
            doc = adl.doc
            docs |= {doc['_id']}
        CouchdbUserFactory.create_batch(2, doc_type=MAJOR)

        with self.assertNumQueries(18):
            response = self.get(self.url)
        context_data = response.context_data

        assert response.status_code == 200
        assert context_data['object_list'] == context_data['adls']
        assert {doc['_id'] for doc in context_data['adls']} == docs
        assert len(adls) == size

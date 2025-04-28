# from django.urls import reverse
#
# from dashboard.participatory_budget.views import DashboardTemplateView
# from grm.tests import DashboardTestCase
#
#
# class TestDashboardTemplateView(DashboardTestCase):
#     def setUp(self):
#         super().setUp()
#         self.url = reverse('dashboard:participatory_budget:dashboard')
#         self.user = self.create_user()
#
#     def test_auth_permission(self):
#         response = self.get(self.url, authorized=False)
#
#         assert response.status_code == 302
#
#     def test_context_data(self):
#         with self.assertNumQueries(17):
#             response = self.get(self.url)
#         context_data = response.context_data
#
#         assert response.status_code == 200
#         assert context_data['title'] == DashboardTemplateView.title == 'Participatory Budget'
#         assert context_data['active_level1'] == DashboardTemplateView.active_level1 == 'participatory_budget'
#         assert context_data['active_level2'] == DashboardTemplateView.active_level2 is None
#         assert context_data['breadcrumb'] == DashboardTemplateView.breadcrumb is None
#         assert isinstance(context_data['view'], DashboardTemplateView)
